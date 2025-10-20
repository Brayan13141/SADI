import plotly.express as px
import plotly.io as pio
from django.db.models import Count, Q, F
import logging
from django.shortcuts import render
from actividades.models import Actividad
from metas.models import Meta
from objetivos.models import ObjetivoEstrategico
from proyectos.models import Proyecto
from usuarios.decorators import role_required


@role_required("ADMIN", "APOYO", "DOCENTE", "INVITADO")
def dashboard(request):
    """
    Vista del panel principal con agregaciones optimizadas
    """
    logger = logging.getLogger(__name__)
    usuario = request.user
    es_docente = usuario.role == "DOCENTE"

    # ===================== MANEJO DE ERRORES =====================
    def safe_aggregate(queryset, aggregate_dict, default_value=0):
        """Maneja errores en agregaciones"""
        try:
            result = queryset.aggregate(**aggregate_dict)
            return {k: v or default_value for k, v in result.items()}
        except Exception as e:
            logger.error(f"Error en agregación: {e}")
            return {k: default_value for k in aggregate_dict.keys()}

    def safe_porcentaje(cumplidas, total):
        """Calcula porcentaje manejando casos edge"""
        try:
            if total == 0:
                return 0
            porcentaje = (cumplidas / total) * 100
            return round(porcentaje, 1)
        except (TypeError, ZeroDivisionError, ValueError) as e:
            logger.warning(f"Error calculando porcentaje: {e}")
            return 0

    def safe_count(queryset):
        """Cuenta elementos manejando errores"""
        try:
            return queryset.count()
        except Exception as e:
            logger.error(f"Error contando queryset: {e}")
            return 0

    # ===================== FILTROS POR ROL =====================
    try:
        if es_docente:
            # Verificar que el docente tenga departamento
            if not hasattr(usuario, "departamento") or not usuario.departamento:
                logger.warning(f"Docente {usuario.id} sin departamento asignado")
                # Retornar datos vacíos o manejar según necesidad
                return render(request, "core/dashboard.html", get_empty_context())

            actividades_qs = Actividad.objects.filter(
                meta__departamento=usuario.departamento
            )
            metas_qs = Meta.objects.filter(departamento=usuario.departamento)
            proyectos_qs = Proyecto.objects.filter(
                meta__departamento=usuario.departamento
            ).distinct()
            objetivos_qs = ObjetivoEstrategico.objects.filter(
                proyecto__meta__departamento=usuario.departamento
            ).distinct()
        else:
            # ADMIN, APOYO, INVITADO - datos globales
            actividades_qs = Actividad.objects.all()
            metas_qs = Meta.objects.all()
            proyectos_qs = Proyecto.objects.all()
            objetivos_qs = ObjetivoEstrategico.objects.all()
    except Exception as e:
        logger.error(
            f"Verifique que el usuario actual tenga departamento asignado: {e}"
        )
        return render(request, "core/error.html", {"error": "Error cargando datos"})

    # ===================== ACTIVIDADES CON AGREGACIONES =====================
    actividades_stats = safe_aggregate(
        actividades_qs,
        {
            "total": Count("id"),
            "cumplidas": Count("id", filter=Q(estado="Cumplida")),
            "no_cumplidas": Count("id", filter=~Q(estado="Cumplida")),
        },
    )

    total_actividades = actividades_stats["total"]
    actividades_cumplidas = actividades_stats["cumplidas"]
    actividades_no_cumplidas = actividades_stats["no_cumplidas"]
    porcentaje_actividades = safe_porcentaje(actividades_cumplidas, total_actividades)

    # ===================== METAS CON AGREGACIONES AVANZADAS =====================
    try:
        # Anotar cada meta con el conteo de sus actividades cumplidas y totales
        metas_anotadas = metas_qs.annotate(
            total_actividades=Count("actividad"),
            actividades_cumplidas=Count(
                "actividad", filter=Q(actividad__estado="Cumplida")
            ),
        ).filter(
            total_actividades__gt=0
        )  # Solo metas con actividades

        # Contar metas cumplidas (todas las actividades cumplidas)
        metas_cumplidas_count = metas_anotadas.filter(
            actividades_cumplidas=F("total_actividades")
        ).count()

        total_metas_con_actividades = safe_count(metas_anotadas)
        metas_no_cumplidas = total_metas_con_actividades - metas_cumplidas_count
        porcentaje_metas = safe_porcentaje(
            metas_cumplidas_count, total_metas_con_actividades
        )

    except Exception as e:
        logger.error(f"Error procesando metas: {e}")
        metas_cumplidas_count = 0
        total_metas_con_actividades = 0
        metas_no_cumplidas = 0
        porcentaje_metas = 0

    # ===================== PROYECTOS CON AGREGACIONES =====================
    try:
        # Proyectos con al menos una meta
        proyectos_con_metas = proyectos_qs.annotate(
            total_metas=Count("meta"),
            # Contar metas cumplidas usando subquery o lógica similar
        ).filter(total_metas__gt=0)

        # Para proyectos, necesitamos una lógica más compleja
        # Versión simplificada - podrías optimizar esto con subconsultas
        proyectos_cumplidos_count = 0
        for proyecto in proyectos_con_metas.prefetch_related("meta_set__actividad_set"):
            metas_proyecto = proyecto.meta_set.all()
            if metas_proyecto and all(
                meta.actividad_set.exists()
                and meta.actividad_set.filter(estado="Cumplida").count()
                == meta.actividad_set.count()
                for meta in metas_proyecto
            ):
                proyectos_cumplidos_count += 1

        total_proyectos = safe_count(proyectos_con_metas)
        proyectos_no_cumplidos = total_proyectos - proyectos_cumplidos_count
        porcentaje_proyectos = safe_porcentaje(
            proyectos_cumplidos_count, total_proyectos
        )

    except Exception as e:
        logger.error(f"Error procesando proyectos: {e}")
        proyectos_cumplidos_count = 0
        total_proyectos = 0
        proyectos_no_cumplidos = 0
        porcentaje_proyectos = 0

    # ===================== OBJETIVOS =====================
    try:
        objetivos_con_proyectos = objetivos_qs.filter(proyecto__isnull=False).distinct()
        objetivos_cumplidos_count = 0

        for objetivo in objetivos_con_proyectos.prefetch_related(
            "proyecto_set__meta_set__actividad_set"
        ):
            proyectos_objetivo = objetivo.proyecto_set.all()
            if proyectos_objetivo and all(
                proyecto.meta_set.exists()
                and all(
                    meta.actividad_set.exists()
                    and meta.actividad_set.filter(estado="Cumplida").count()
                    == meta.actividad_set.count()
                    for meta in proyecto.meta_set.all()
                )
                for proyecto in proyectos_objetivo
            ):
                objetivos_cumplidos_count += 1

        total_objetivos = safe_count(objetivos_con_proyectos)
        objetivos_no_cumplidos = total_objetivos - objetivos_cumplidos_count
        porcentaje_objetivos = safe_porcentaje(
            objetivos_cumplidos_count, total_objetivos
        )

    except Exception as e:
        logger.error(f"Error procesando objetivos: {e}")
        objetivos_cumplidos_count = 0
        total_objetivos = 0
        objetivos_no_cumplidos = 0
        porcentaje_objetivos = 0

    # ===================== GRÁFICOS =====================
    try:
        # Gráfico de actividades
        fig_actividades = px.pie(
            names=["Cumplidas", "No Cumplidas"],
            values=[actividades_cumplidas, actividades_no_cumplidas],
            title="Estado de las Actividades",
            color_discrete_sequence=["#2ECC71", "#E74C3C"],
        )
        fig_actividades.update_traces(
            textinfo="percent+label",
            pull=[0.05, 0],
            # Manejar caso sin datos
            text=(
                [actividades_cumplidas, actividades_no_cumplidas]
                if total_actividades > 0
                else [0, 0]
            ),
        )
        grafico_actividades_html = pio.to_html(
            fig_actividades, full_html=False, include_plotlyjs="cdn"
        )

        # ... (similar para otros gráficos, con manejo de errores)

    except Exception as e:
        logger.error(f"Error generando gráficos: {e}")
        grafico_actividades_html = "<p>Error cargando gráfico</p>"
        # ... manejar otros gráficos

    # ===================== CONTEXTO FINAL =====================
    context = {
        # Actividades
        "total_actividades": total_actividades,
        "cumplidas": actividades_cumplidas,
        "no_cumplidas": actividades_no_cumplidas,
        "grafico_actividades_html": grafico_actividades_html,
        "porcentaje_cumplidas": porcentaje_actividades,
        # Metas
        "total_metas": total_metas_con_actividades,
        "metas_cumplidas": metas_cumplidas_count,
        "metas_no_cumplidas": metas_no_cumplidas,
        "porcentaje_metas_cumplidas": porcentaje_metas,
        # Proyectos
        "total_proyectos": total_proyectos,
        "proyectos_cumplidos": proyectos_cumplidos_count,
        "proyectos_no_cumplidos": proyectos_no_cumplidos,
        "porcentaje_proyectos_cumplidos": porcentaje_proyectos,
        # Objetivos
        "total_objetivos": total_objetivos,
        "objetivos_cumplidos": objetivos_cumplidos_count,
        "objetivos_no_cumplidos": objetivos_no_cumplidos,
        "porcentaje_objetivos_cumplidos": porcentaje_objetivos,
        # Info del rol
        "es_docente": es_docente,
        "filtro_aplicado": "Departamento" if es_docente else "Global",
        "departamento_usuario": (
            getattr(usuario.departamento, "nombre", "No asignado")
            if es_docente
            else None
        ),
    }

    return render(request, "core/dashboard.html", context)


def get_empty_context():
    """Retorna contexto vacío para casos de error"""
    return {
        "total_actividades": 0,
        "cumplidas": 0,
        "no_cumplidas": 0,
        "porcentaje_cumplidas": 0,
        "total_metas": 0,
        "metas_cumplidas": 0,
        "metas_no_cumplidas": 0,
        "porcentaje_metas_cumplidas": 0,
        "total_proyectos": 0,
        "proyectos_cumplidos": 0,
        "proyectos_no_cumplidos": 0,
        "porcentaje_proyectos_cumplidos": 0,
        "total_objetivos": 0,
        "objetivos_cumplidos": 0,
        "objetivos_no_cumplidos": 0,
        "porcentaje_objetivos_cumplidos": 0,
        "grafico_actividades_html": "<p>No hay datos disponibles</p>",
        "es_docente": False,
        "filtro_aplicado": "Sin datos",
    }


def index(request):
    return render(request, "index.html")
