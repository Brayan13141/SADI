import plotly.express as px
import plotly.io as pio
from django.db.models import Count, Q
import logging
from django.shortcuts import render, get_object_or_404
from actividades.models import Actividad
from metas.models import Meta
from objetivos.models import ObjetivoEstrategico
from proyectos.models import Proyecto
from usuarios.decorators import role_required
from programas.models import Ciclo
from django.contrib import messages
from django.shortcuts import redirect


@role_required("ADMIN", "APOYO", "DOCENTE", "INVITADO")
def dashboard(request):
    """
    Dashboard general con métricas filtradas por ciclo y departamento según rol.
    """
    logger = logging.getLogger(__name__)
    usuario = request.user
    es_docente = usuario.role == "DOCENTE"
    es_admin = usuario.role == "ADMIN"
    es_apoyo = usuario.role == "APOYO"

    # ===================== FUNCIONES AUXILIARES =====================
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
            return round((cumplidas / total) * 100, 1)
        except Exception as e:
            logger.warning(f"Error calculando porcentaje: {e}")
            return 0

    def safe_count(queryset):
        """Cuenta elementos manejando errores"""
        try:
            return queryset.count()
        except Exception as e:
            logger.error(f"Error contando queryset: {e}")
            return 0

    # ===================== CICLO ACTUAL O SELECCIONADO =====================
    ciclo_id = request.session.get("ciclo_id")
    ciclos_disponibles = Ciclo.objects.all().order_by("-fecha_inicio")
    if ciclo_id:
        ciclo_actual = get_object_or_404(Ciclo, id=ciclo_id)
    else:
        ciclo_actual = (
            ciclos_disponibles.filter(estado="Activo").first()
            or ciclos_disponibles.first()
        )

    if not ciclo_actual:
        return render(
            request,
            "core/dashboard.html",
            {
                "mensaje": "No hay ciclos registrados",
                "ciclos_disponibles": [],
                "ciclo_actual": None,
            },
        )

    # ===================== FILTROS POR ROL Y DEPARTAMENTO =====================
    try:
        #  CORRECCIÓN: Filtrar por departamento según el rol
        if es_docente:
            # DOCENTE: solo su departamento
            if not hasattr(usuario, "departamento") or not usuario.departamento:
                logger.warning(f"Docente {usuario.id} sin departamento asignado")
                return render(request, "core/dashboard.html", get_empty_context())

            departamento_filtro = usuario.departamento

            actividades_qs = Actividad.objects.filter(
                departamento=departamento_filtro, ciclo=ciclo_actual
            )
            metas_qs = Meta.objects.filter(departamento=departamento_filtro)
            proyectos_qs = Proyecto.objects.filter(
                meta__departamento=departamento_filtro
            ).distinct()
            objetivos_qs = ObjetivoEstrategico.objects.filter(
                proyecto__meta__departamento=departamento_filtro
            ).distinct()

        elif es_apoyo:
            # APOYO: solo su departamento (igual que DOCENTE)
            if not hasattr(usuario, "departamento") or not usuario.departamento:
                logger.warning(f"Apoyo {usuario.id} sin departamento asignado")
                return render(request, "core/dashboard.html", get_empty_context())

            departamento_filtro = usuario.departamento

            actividades_qs = Actividad.objects.filter(
                departamento=departamento_filtro, ciclo=ciclo_actual
            )
            metas_qs = Meta.objects.filter(departamento=departamento_filtro)
            proyectos_qs = Proyecto.objects.filter(
                meta__departamento=departamento_filtro
            ).distinct()
            objetivos_qs = ObjetivoEstrategico.objects.filter(
                proyecto__meta__departamento=departamento_filtro
            ).distinct()

        else:
            # ADMIN: todos los departamentos
            # INVITADO: todos los departamentos (o puedes ajustar según necesites)
            actividades_qs = Actividad.objects.filter(ciclo=ciclo_actual)
            metas_qs = Meta.objects.all()
            proyectos_qs = Proyecto.objects.all()
            objetivos_qs = ObjetivoEstrategico.objects.all()
            departamento_filtro = None

    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        return render(request, "core/error.html", {"error": "Error cargando datos"})

    # ===================== ACTIVIDADES =====================
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

    # ===================== METAS =====================
    try:

        metas_con_actividades = metas_qs.filter(
            actividad__ciclo=ciclo_actual
        ).distinct()

        total_metas = safe_count(metas_con_actividades)

        # Contar metas cumplidas (todas sus actividades cumplidas)
        metas_cumplidas_count = 0
        for meta in metas_con_actividades:
            actividades_meta = meta.actividad_set.filter(ciclo=ciclo_actual)
            total_acts_meta = actividades_meta.count()
            acts_cumplidas_meta = actividades_meta.filter(estado="Cumplida").count()

            if total_acts_meta > 0 and acts_cumplidas_meta == total_acts_meta:
                metas_cumplidas_count += 1

        metas_no_cumplidas = total_metas - metas_cumplidas_count
        porcentaje_metas = safe_porcentaje(metas_cumplidas_count, total_metas)

    except Exception as e:
        logger.error(f"Error procesando metas: {e}")
        total_metas = metas_cumplidas_count = metas_no_cumplidas = porcentaje_metas = 0

    # ===================== PROYECTOS =====================
    try:

        proyectos_con_actividades = proyectos_qs.filter(
            meta__actividad__ciclo=ciclo_actual
        ).distinct()

        total_proyectos = safe_count(proyectos_con_actividades)
        proyectos_cumplidos_count = 0

        for proyecto in proyectos_con_actividades:
            # Verificar si todas las metas del proyecto están cumplidas
            metas_proyecto = proyecto.meta_set.all()
            proyecto_cumplido = True

            for meta in metas_proyecto:
                actividades_meta = meta.actividad_set.filter(ciclo=ciclo_actual)
                if actividades_meta.exists():  # Solo considerar metas con actividades
                    total_acts = actividades_meta.count()
                    acts_cumplidas = actividades_meta.filter(estado="Cumplida").count()
                    if acts_cumplidas != total_acts:
                        proyecto_cumplido = False
                        break

            if proyecto_cumplido and any(
                meta.actividad_set.filter(ciclo=ciclo_actual).exists()
                for meta in metas_proyecto
            ):
                proyectos_cumplidos_count += 1

        proyectos_no_cumplidos = total_proyectos - proyectos_cumplidos_count
        porcentaje_proyectos = safe_porcentaje(
            proyectos_cumplidos_count, total_proyectos
        )

    except Exception as e:
        logger.error(f"Error procesando proyectos: {e}")
        total_proyectos = proyectos_cumplidos_count = proyectos_no_cumplidos = (
            porcentaje_proyectos
        ) = 0

    # ===================== OBJETIVOS =====================
    try:

        objetivos_con_actividades = objetivos_qs.filter(
            proyecto__meta__actividad__ciclo=ciclo_actual
        ).distinct()

        total_objetivos = safe_count(objetivos_con_actividades)
        objetivos_cumplidos_count = 0

        for objetivo in objetivos_con_actividades:
            # Verificar si todos los proyectos del objetivo están cumplidos
            proyectos_objetivo = objetivo.proyecto_set.all()
            objetivo_cumplido = True

            for proyecto in proyectos_objetivo:
                metas_proyecto = proyecto.meta_set.all()
                for meta in metas_proyecto:
                    actividades_meta = meta.actividad_set.filter(ciclo=ciclo_actual)
                    if (
                        actividades_meta.exists()
                    ):  # Solo considerar metas con actividades
                        total_acts = actividades_meta.count()
                        acts_cumplidas = actividades_meta.filter(
                            estado="Cumplida"
                        ).count()
                        if acts_cumplidas != total_acts:
                            objetivo_cumplido = False
                            break
                if not objetivo_cumplido:
                    break

            if objetivo_cumplido and any(
                meta.actividad_set.filter(ciclo=ciclo_actual).exists()
                for proyecto in proyectos_objetivo
                for meta in proyecto.meta_set.all()
            ):
                objetivos_cumplidos_count += 1

        objetivos_no_cumplidos = total_objetivos - objetivos_cumplidos_count
        porcentaje_objetivos = safe_porcentaje(
            objetivos_cumplidos_count, total_objetivos
        )

    except Exception as e:
        logger.error(f"Error procesando objetivos: {e}")
        total_objetivos = objetivos_cumplidos_count = objetivos_no_cumplidos = (
            porcentaje_objetivos
        ) = 0

    # ===================== GRÁFICOS =====================
    try:
        fig_actividades = px.pie(
            names=["Cumplidas", "No Cumplidas"],
            values=[actividades_cumplidas, actividades_no_cumplidas],
            title=f"Estado de las Actividades ({ciclo_actual.nombre})",
            color_discrete_sequence=["#2ECC71", "#E74C3C"],
        )
        fig_metas = px.pie(
            names=["Cumplidas", "No Cumplidas"],
            values=[metas_cumplidas_count, metas_no_cumplidas],
            title=f"Estado de las Metas ({ciclo_actual.nombre})",
            color_discrete_sequence=["#2ECC71", "#E74C3C"],
        )
        fig_proyectos = px.pie(
            names=["Cumplidos", "No Cumplidos"],
            values=[proyectos_cumplidos_count, proyectos_no_cumplidos],
            title=f"Estado de los Proyectos ({ciclo_actual.nombre})",
            color_discrete_sequence=["#2ECC71", "#E74C3C"],
        )

        grafico_actividades_html = pio.to_html(
            fig_actividades, full_html=False, include_plotlyjs="cdn"
        )
        grafico_metas_html = pio.to_html(
            fig_metas, full_html=False, include_plotlyjs="cdn"
        )
        grafico_proyectos_html = pio.to_html(
            fig_proyectos, full_html=False, include_plotlyjs="cdn"
        )

    except Exception as e:
        logger.error(f"Error generando gráficos: {e}")
        grafico_actividades_html = grafico_metas_html = grafico_proyectos_html = (
            "<p>Error cargando gráfico</p>"
        )

    # ===================== CONTEXTO FINAL =====================
    context = {
        # Actividades
        "total_actividades": total_actividades,
        "actividades_cumplidas": actividades_cumplidas,
        "actividades_no_cumplidas": actividades_no_cumplidas,
        "porcentaje_actividades": porcentaje_actividades,
        "grafico_actividades_html": grafico_actividades_html,
        # Metas
        "total_metas": total_metas,
        "metas_cumplidas": metas_cumplidas_count,
        "metas_no_cumplidas": metas_no_cumplidas,
        "porcentaje_metas": porcentaje_metas,
        "grafico_metas_html": grafico_metas_html,
        # Proyectos
        "total_proyectos": total_proyectos,
        "proyectos_cumplidos": proyectos_cumplidos_count,
        "proyectos_no_cumplidos": proyectos_no_cumplidos,
        "porcentaje_proyectos": porcentaje_proyectos,
        "grafico_proyectos_html": grafico_proyectos_html,
        # Objetivos
        "total_objetivos": total_objetivos,
        "objetivos_cumplidos": objetivos_cumplidos_count,
        "objetivos_no_cumplidos": objetivos_no_cumplidos,
        "porcentaje_objetivos": porcentaje_objetivos,
        # Info del rol y ciclo
        "es_docente": es_docente,
        "es_admin": es_admin,
        "es_apoyo": es_apoyo,
        "filtro_aplicado": "Departamento" if es_docente or es_apoyo else "Global",
        "departamento_usuario": (
            getattr(usuario.departamento, "nombre", "No asignado")
            if es_docente or es_apoyo
            else None
        ),
        "ciclo_actual": ciclo_actual,
        "ciclos_disponibles": ciclos_disponibles,
    }

    return render(request, "core/dashboard.html", context)


def get_empty_context():
    """Retorna un contexto vacío para cuando no hay datos"""
    return {
        "total_actividades": 0,
        "actividades_cumplidas": 0,
        "actividades_no_cumplidas": 0,
        "porcentaje_actividades": 0,
        "total_metas": 0,
        "metas_cumplidas": 0,
        "metas_no_cumplidas": 0,
        "porcentaje_metas": 0,
        "total_proyectos": 0,
        "proyectos_cumplidos": 0,
        "proyectos_no_cumplidos": 0,
        "porcentaje_proyectos": 0,
        "total_objetivos": 0,
        "objetivos_cumplidos": 0,
        "objetivos_no_cumplidos": 0,
        "porcentaje_objetivos": 0,
        "grafico_actividades_html": "<p>No hay datos para mostrar</p>",
        "grafico_metas_html": "<p>No hay datos para mostrar</p>",
        "grafico_proyectos_html": "<p>No hay datos para mostrar</p>",
    }
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


def cambiar_ciclo_flecha(request):
    if request.method == "POST":
        accion = request.POST.get("accion")
        ciclos = list(Ciclo.objects.all().order_by("nombre"))

        ciclo_id = request.session.get("ciclo_id")

        if not ciclos:
            messages.warning(request, "No hay ciclos disponibles.")
            return redirect(request.META.get("HTTP_REFERER", "dashboard"))

        # Si no hay ciclo actual, usar el primero
        if not ciclo_id:
            ciclo_actual = ciclos[0]
        else:
            ciclo_actual = next((c for c in ciclos if c.id == ciclo_id), ciclos[0])

        # Obtener índice actual
        indice = ciclos.index(ciclo_actual)

        # Cambiar hacia atrás o adelante
        if accion == "atras" and indice > 0:
            nuevo_ciclo = ciclos[indice - 1]
        elif accion == "adelante" and indice < len(ciclos) - 1:
            nuevo_ciclo = ciclos[indice + 1]
        else:
            nuevo_ciclo = ciclo_actual  # No moverse si no hay más

        # Guardar en sesión
        request.session["ciclo_id"] = nuevo_ciclo.id
        request.session["ciclo_nombre"] = nuevo_ciclo.nombre
        messages.info(request, f"Ciclo cambiado a {nuevo_ciclo.nombre}.")

    return redirect(request.META.get("HTTP_REFERER", "dashboard"))
