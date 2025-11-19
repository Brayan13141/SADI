import plotly.express as px
import plotly.io as pio
from django.db.models import Count, Q
import logging
from django.shortcuts import render
from metas.models import Meta, MetaCiclo, AvanceMeta
from proyectos.models import Proyecto
from django.db.models import Sum
from decimal import Decimal
from objetivos.models import ObjetivoEstrategico
from actividades.models import Actividad
from usuarios.decorators import role_required
from programas.models import Ciclo
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404


@role_required("ADMIN", "APOYO", "DOCENTE", "INVITADO")
def dashboard(request):
    """
    Dashboard general con métricas de cantidad basado en metas
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

    def calcular_avance_meta(meta, ciclo):
        """Calcula el avance real de una meta en un ciclo específico"""
        try:
            avances = AvanceMeta.objects.filter(metaCumplir=meta, ciclo=ciclo).order_by(
                "fecha_registro"
            )

            if not avances.exists():
                return Decimal("0")

            if meta.acumulable:
                # Acumulable: toma el último valor
                return avances.last().avance or Decimal("0")
            else:
                # Incremental: suma todos los avances
                return avances.aggregate(total=Sum("avance"))["total"] or Decimal("0")
        except Exception as e:
            logger.error(f"Error calculando avance para meta {meta.id}: {e}")
            return Decimal("0")

    def meta_esta_cumplida(meta, ciclo):
        """Determina si una meta está cumplida basado en su avance vs meta a cumplir"""
        try:
            meta_ciclo = MetaCiclo.objects.filter(meta=meta, ciclo=ciclo).first()
            if not meta_ciclo:
                return False

            avance_real = calcular_avance_meta(meta, ciclo)
            meta_cumplir = meta_ciclo.metaCumplir or Decimal("0")

            return avance_real >= meta_cumplir
        except Exception as e:
            logger.error(f"Error verificando cumplimiento de meta {meta.id}: {e}")
            return False

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
        if es_docente or es_apoyo:
            if not hasattr(usuario, "departamento") or not usuario.departamento:
                logger.warning(f"Usuario {usuario.id} sin departamento asignado")
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
            # ADMIN e INVITADO: todos los departamentos
            actividades_qs = Actividad.objects.filter(ciclo=ciclo_actual)
            metas_qs = Meta.objects.all()
            proyectos_qs = Proyecto.objects.all()
            objetivos_qs = ObjetivoEstrategico.objects.all()
            departamento_filtro = None

    except Exception as e:
        logger.error(f"Error cargando datos: {e}")
        return render(request, "core/error.html", {"error": "Error cargando datos"})

    # ===================== CONTADORES DE ACTIVIDADES CORREGIDOS =====================
    actividades_stats = safe_aggregate(
        actividades_qs,
        {
            "total": Count("id"),
            "cumplidas": Count("id", filter=Q(estado="Cumplida")),
            "no_cumplidas": Count("id", filter=Q(estado="No Cumplida")),
            "en_proceso": Count("id", filter=Q(estado="En Proceso")),
            "activas": Count("id", filter=Q(estado="Activa")),
        },
    )

    total_actividades = actividades_stats["total"]
    actividades_cumplidas = actividades_stats["cumplidas"]
    actividades_no_cumplidas = actividades_stats["no_cumplidas"]
    actividades_en_proceso = actividades_stats["en_proceso"]
    actividades_activas = actividades_stats["activas"]
    actividades_en_progreso_total = actividades_en_proceso + actividades_activas
    porcentaje_actividades = safe_porcentaje(actividades_cumplidas, total_actividades)

    # ===================== CONTADORES DE METAS CORREGIDOS =====================
    try:
        metas_con_ciclo = []
        metas_cumplidas_count = 0

        for meta in metas_qs:
            # Verificar si la meta tiene ciclo actual
            if MetaCiclo.objects.filter(meta=meta, ciclo=ciclo_actual).exists():
                metas_con_ciclo.append(meta)

                # Verificar si la meta está cumplida
                if meta_esta_cumplida(meta, ciclo_actual):
                    metas_cumplidas_count += 1

        total_metas = len(metas_con_ciclo)
        metas_no_cumplidas = total_metas - metas_cumplidas_count
        porcentaje_metas = safe_porcentaje(metas_cumplidas_count, total_metas)

    except Exception as e:
        logger.error(f"Error procesando metas: {e}")
        total_metas = metas_cumplidas_count = metas_no_cumplidas = porcentaje_metas = 0

    # ===================== CONTADORES DE PROYECTOS CORREGIDOS =====================
    try:
        proyectos_con_metas = []
        proyectos_cumplidos_count = 0

        for proyecto in proyectos_qs:
            # Obtener todas las metas del proyecto en este ciclo
            metas_proyecto = proyecto.meta_set.filter(
                metas_ciclo__ciclo=ciclo_actual
            ).distinct()

            if metas_proyecto.exists():
                proyectos_con_metas.append(proyecto)

                # Un proyecto está cumplido si TODAS sus metas están cumplidas
                proyecto_cumplido = True
                metas_en_proyecto_count = 0

                for meta in metas_proyecto:
                    if MetaCiclo.objects.filter(meta=meta, ciclo=ciclo_actual).exists():
                        metas_en_proyecto_count += 1
                        if not meta_esta_cumplida(meta, ciclo_actual):
                            proyecto_cumplido = False
                            break  # No need to check further if one meta is not cumplida

                # Solo considerar proyectos que tengan al menos una meta en el ciclo
                if metas_en_proyecto_count > 0 and proyecto_cumplido:
                    proyectos_cumplidos_count += 1

        total_proyectos = len(proyectos_con_metas)
        proyectos_no_cumplidos = total_proyectos - proyectos_cumplidos_count
        porcentaje_proyectos = safe_porcentaje(
            proyectos_cumplidos_count, total_proyectos
        )

    except Exception as e:
        logger.error(f"Error procesando proyectos: {e}")
        total_proyectos = proyectos_cumplidos_count = proyectos_no_cumplidos = (
            porcentaje_proyectos
        ) = 0

    # ===================== CONTADORES DE OBJETIVOS CORREGIDOS =====================
    try:
        objetivos_con_proyectos = []
        objetivos_cumplidos_count = 0

        for objetivo in objetivos_qs:
            # Obtener todos los proyectos del objetivo que tengan metas en este ciclo
            proyectos_objetivo = objetivo.proyecto_set.filter(
                meta__metas_ciclo__ciclo=ciclo_actual
            ).distinct()

            if proyectos_objetivo.exists():
                objetivos_con_proyectos.append(objetivo)

                # Un objetivo está cumplido si TODOS sus proyectos están cumplidos
                objetivo_cumplido = True
                proyectos_en_objetivo_count = 0

                for proyecto in proyectos_objetivo:
                    # Verificar si el proyecto tiene metas en este ciclo
                    metas_proyecto = proyecto.meta_set.filter(
                        metas_ciclo__ciclo=ciclo_actual
                    ).distinct()

                    if metas_proyecto.exists():
                        proyectos_en_objetivo_count += 1

                        # Verificar si el proyecto está cumplido
                        proyecto_cumplido = True
                        for meta in metas_proyecto:
                            if not meta_esta_cumplida(meta, ciclo_actual):
                                proyecto_cumplido = False
                                break

                        if not proyecto_cumplido:
                            objetivo_cumplido = False
                            break  # No need to check further if one project is not cumplido

                # Solo considerar objetivos que tengan al menos un proyecto con metas en el ciclo
                if proyectos_en_objetivo_count > 0 and objetivo_cumplido:
                    objetivos_cumplidos_count += 1

        total_objetivos = len(objetivos_con_proyectos)
        objetivos_no_cumplidos = total_objetivos - objetivos_cumplidos_count
        porcentaje_objetivos = safe_porcentaje(
            objetivos_cumplidos_count, total_objetivos
        )

    except Exception as e:
        logger.error(f"Error procesando objetivos: {e}")
        total_objetivos = objetivos_cumplidos_count = objetivos_no_cumplidos = (
            porcentaje_objetivos
        ) = 0

    # ===================== GRÁFICOS CORREGIDOS =====================
    try:
        # 1. GRÁFICO DE ACTIVIDADES - Donut Chart CORREGIDO
        fig_actividades = px.pie(
            names=["Cumplidas", "Activas", "En Proceso", "No Cumplidas"],
            values=[
                actividades_cumplidas,
                actividades_activas,
                actividades_en_proceso,
                actividades_no_cumplidas,
            ],
            title=f"Distribución de Actividades<br><sub>{ciclo_actual.nombre}</sub>",
            color_discrete_sequence=["#28a745", "#17a2b8", "#ffc107", "#dc3545"],
            hole=0.4,
        )
        fig_actividades.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Total: %{value}<br>Porcentaje: %{percent}",
        )
        fig_actividades.update_layout(
            font=dict(size=12), showlegend=False, margin=dict(t=80, b=40, l=40, r=40)
        )

        # 2. GRÁFICO DE METAS - Donut Chart mejorado
        fig_metas = px.pie(
            names=["Cumplidas", "En Progreso"],
            values=[metas_cumplidas_count, metas_no_cumplidas],
            title=f"Estado de Metas<br><sub>{ciclo_actual.nombre}</sub>",
            color_discrete_sequence=["#28a745", "#ffc107"],
            hole=0.4,
        )
        fig_metas.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Total: %{value}<br>Porcentaje: %{percent}",
        )
        fig_metas.update_layout(
            font=dict(size=12), showlegend=False, margin=dict(t=80, b=40, l=40, r=40)
        )

        # 3. GRÁFICO DE PROYECTOS - Donut Chart
        fig_proyectos = px.pie(
            names=["Cumplidos", "En Progreso"],
            values=[proyectos_cumplidos_count, proyectos_no_cumplidos],
            title=f"Estado de Proyectos<br><sub>{ciclo_actual.nombre}</sub>",
            color_discrete_sequence=["#28a745", "#ffc107"],
            hole=0.4,
        )
        fig_proyectos.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Total: %{value}<br>Porcentaje: %{percent}",
        )
        fig_proyectos.update_layout(
            font=dict(size=12), showlegend=False, margin=dict(t=80, b=40, l=40, r=40)
        )

        # 4. GRÁFICO DE OBJETIVOS - Donut Chart
        fig_objetivos = px.pie(
            names=["Cumplidos", "En Progreso"],
            values=[objetivos_cumplidos_count, objetivos_no_cumplidos],
            title=f"Estado de Objetivos<br><sub>{ciclo_actual.nombre}</sub>",
            color_discrete_sequence=["#17a2b8", "#6c757d"],
            hole=0.4,
        )
        fig_objetivos.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Total: %{value}<br>Porcentaje: %{percent}",
        )
        fig_objetivos.update_layout(
            font=dict(size=12), showlegend=False, margin=dict(t=80, b=40, l=40, r=40)
        )

        # 5. GRÁFICO DE PROGRESO GENERAL - Bar Chart vertical mejorado
        categorias = ["Actividades", "Metas", "Proyectos", "Objetivos"]
        porcentajes = [
            porcentaje_actividades,
            porcentaje_metas,
            porcentaje_proyectos,
            porcentaje_objetivos,
        ]
        totales = [total_actividades, total_metas, total_proyectos, total_objetivos]
        cumplidos = [
            actividades_cumplidas,
            metas_cumplidas_count,
            proyectos_cumplidos_count,
            objetivos_cumplidos_count,
        ]

        # Texto para las barras
        textos_barras = [f"{c}/{t}" for c, t in zip(cumplidos, totales)]

        fig_progreso = px.bar(
            x=categorias,
            y=porcentajes,
            title=f"Progreso General por Nivel<br><sub>{ciclo_actual.nombre}</sub>",
            color=categorias,
            color_discrete_sequence=["#3498DB", "#9B59B6", "#F1C40F", "#1ABC9C"],
            text=textos_barras,
        )
        fig_progreso.update_layout(
            showlegend=False,
            xaxis_title="Categorías",
            yaxis_title="Porcentaje de Cumplimiento (%)",
            yaxis_range=[0, 100],
            margin=dict(t=80, b=60, l=60, r=40),
        )
        fig_progreso.update_traces(
            texttemplate="%{text}",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Porcentaje: %{y:.1f}%<br>Cumplidos: %{text}",
        )

        # Convertir a HTML
        grafico_actividades_html = pio.to_html(
            fig_actividades, full_html=False, include_plotlyjs="cdn"
        )
        grafico_metas_html = pio.to_html(
            fig_metas, full_html=False, include_plotlyjs="cdn"
        )
        grafico_proyectos_html = pio.to_html(
            fig_proyectos, full_html=False, include_plotlyjs="cdn"
        )
        grafico_objetivos_html = pio.to_html(
            fig_objetivos, full_html=False, include_plotlyjs="cdn"
        )
        grafico_progreso_html = pio.to_html(
            fig_progreso, full_html=False, include_plotlyjs="cdn"
        )

    except Exception as e:
        logger.error(f"Error generando gráficos: {e}")
        grafico_actividades_html = grafico_metas_html = grafico_proyectos_html = (
            grafico_objetivos_html
        ) = grafico_progreso_html = "<p>Error cargando gráfico</p>"

    # ===================== CONTEXTO FINAL CORREGIDO =====================
    context = {
        # Actividades - Contadores CORREGIDOS
        "total_actividades": total_actividades,
        "actividades_cumplidas": actividades_cumplidas,
        "actividades_no_cumplidas": actividades_no_cumplidas,
        "actividades_en_proceso": actividades_en_proceso,
        "actividades_activas": actividades_activas,
        "actividades_en_progreso": actividades_en_progreso_total,
        "porcentaje_actividades": porcentaje_actividades,
        # Metas - Contadores
        "total_metas": total_metas,
        "metas_cumplidas": metas_cumplidas_count,
        "metas_no_cumplidas": metas_no_cumplidas,
        "porcentaje_metas": porcentaje_metas,
        # Proyectos - Contadores
        "total_proyectos": total_proyectos,
        "proyectos_cumplidos": proyectos_cumplidos_count,
        "proyectos_no_cumplidos": proyectos_no_cumplidos,
        "porcentaje_proyectos": porcentaje_proyectos,
        # Objetivos - Contadores
        "total_objetivos": total_objetivos,
        "objetivos_cumplidos": objetivos_cumplidos_count,
        "objetivos_no_cumplidos": objetivos_no_cumplidos,
        "porcentaje_objetivos": porcentaje_objetivos,
        # Gráficos
        "grafico_actividades_html": grafico_actividades_html,
        "grafico_metas_html": grafico_metas_html,
        "grafico_proyectos_html": grafico_proyectos_html,
        "grafico_objetivos_html": grafico_objetivos_html,
        "grafico_progreso_html": grafico_progreso_html,
        # Información del rol y ciclo
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
        "actividades_en_progreso": 0,
        "actividades_pendientes": 0,
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
        "grafico_progreso_html": "<p>No hay datos para mostrar</p>",
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
