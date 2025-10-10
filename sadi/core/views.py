import plotly.express as px
import plotly.io as pio
import plotly.graph_objs as go
from plotly.offline import plot
from django.shortcuts import render
from django.db import models
from actividades.models import Actividad
from riesgos.models import Riesgo
from programas.models import ProgramaEstrategico
from metas.models import Meta
from objetivos.models import ObjetivoEstrategico
from proyectos.models import Proyecto
from usuarios.decorators import role_required


@role_required("ADMIN", "APOYO", "DOCENTE", "INVITADO")
def dashboard(request):
    """
    Vista del panel principal.
    - ADMIN, APOYO, INVITADO: muestran estadísticas globales.
    - DOCENTE: ve solo sus metas y actividades (según su departamento),
      pero los proyectos y objetivos siguen siendo globales.
    """

    usuario = request.user
    es_docente = usuario.role == "DOCENTE"

    # ===================== FUNCIONES AUXILIARES =====================
    def es_meta_cumplida(meta):
        """Una meta se cumple si todas sus actividades están cumplidas."""
        actividades = meta.actividad_set.all()
        return actividades.exists() and all(a.estado == "Cumplida" for a in actividades)

    def es_proyecto_cumplido(proyecto):
        """Un proyecto se cumple si todas sus metas están cumplidas."""
        metas = proyecto.meta_set.all()
        if not metas.exists():
            return False
        return all(es_meta_cumplida(meta) for meta in metas)

    def es_objetivo_cumplido(objetivo):
        """Un objetivo se cumple si todos sus proyectos están cumplidos."""
        proyectos = objetivo.proyecto_set.all()
        if not proyectos.exists():
            return False
        return all(es_proyecto_cumplido(proy) for proy in proyectos)

    # ===================== FILTROS BASE =====================
    # Si es docente, solo se filtran las actividades y metas de su departamento
    if es_docente:
        actividades_qs = Actividad.objects.filter(
            meta__departamento=usuario.departamento
        )
        metas_qs = Meta.objects.filter(departamento=usuario.departamento)
    else:
        actividades_qs = Actividad.objects.all()
        metas_qs = Meta.objects.all()

    # ===================== ACTIVIDADES =====================
    total_actividades = actividades_qs.count()
    actividades_cumplidas = actividades_qs.filter(estado="Cumplida").count()
    actividades_no_cumplidas = total_actividades - actividades_cumplidas

    fig_actividades = px.pie(
        names=["Cumplidas", "No Cumplidas"],
        values=[actividades_cumplidas, actividades_no_cumplidas],
        title="Estado de las Actividades",
        color_discrete_sequence=["#2ECC71", "#E74C3C"],
    )
    fig_actividades.update_traces(textinfo="percent+label", pull=[0.05, 0])
    grafico_actividades_html = pio.to_html(
        fig_actividades, full_html=False, include_plotlyjs="cdn"
    )

    # ===================== METAS =====================
    metas = metas_qs.prefetch_related("actividad_set").all()
    metas_con_actividades = [m for m in metas if m.actividad_set.exists()]
    metas_cumplidas = [m for m in metas_con_actividades if es_meta_cumplida(m)]

    total_metas = len(metas_con_actividades)
    metas_no_cumplidas = total_metas - len(metas_cumplidas)

    fig_metas = px.bar(
        x=["Cumplidas", "No Cumplidas"],
        y=[len(metas_cumplidas), metas_no_cumplidas],
        color=["Cumplidas", "No Cumplidas"],
        title="Cumplimiento de Metas (basado en Actividades)",
        text=[len(metas_cumplidas), metas_no_cumplidas],
        color_discrete_sequence=["#1ABC9C", "#E74C3C"],
    )
    fig_metas.update_traces(textposition="outside")
    grafico_metas_html = pio.to_html(fig_metas, full_html=False, include_plotlyjs=False)

    # ===================== PROYECTOS (Globales) =====================
    proyectos = Proyecto.objects.prefetch_related("meta_set__actividad_set").all()
    proyectos_con_metas = [p for p in proyectos if p.meta_set.exists()]
    proyectos_cumplidos = [p for p in proyectos_con_metas if es_proyecto_cumplido(p)]

    total_proyectos = len(proyectos_con_metas)
    proyectos_no_cumplidos = total_proyectos - len(proyectos_cumplidos)

    fig_proyectos = px.pie(
        names=["Completados", "En Proceso"],
        values=[len(proyectos_cumplidos), proyectos_no_cumplidos],
        title="Estado de los Proyectos (basado en Metas)",
        color_discrete_sequence=["#F39C12", "#3498DB"],
    )
    fig_proyectos.update_traces(textinfo="percent+label", pull=[0.05, 0])
    grafico_proyectos_html = pio.to_html(
        fig_proyectos, full_html=False, include_plotlyjs=False
    )

    # ===================== OBJETIVOS (Globales) =====================
    objetivos = ObjetivoEstrategico.objects.prefetch_related(
        "proyecto_set__meta_set__actividad_set"
    ).all()
    objetivos_con_proyectos = [o for o in objetivos if o.proyecto_set.exists()]
    objetivos_cumplidos = [
        o for o in objetivos_con_proyectos if es_objetivo_cumplido(o)
    ]

    total_objetivos = len(objetivos_con_proyectos)
    objetivos_no_cumplidos = total_objetivos - len(objetivos_cumplidos)

    fig_objetivos = px.bar(
        x=["Cumplidos", "En Proceso"],
        y=[len(objetivos_cumplidos), objetivos_no_cumplidos],
        color=["Cumplidos", "En Proceso"],
        title="Cumplimiento de Objetivos (basado en Proyectos)",
        text=[len(objetivos_cumplidos), objetivos_no_cumplidos],
        color_discrete_sequence=["#2E86C1", "#F5B041"],
    )
    fig_objetivos.update_traces(textposition="outside")
    grafico_objetivos_html = pio.to_html(
        fig_objetivos, full_html=False, include_plotlyjs=False
    )

    # ===================== PORCENTAJES =====================
    def porcentaje(cumplidas, total):
        return round((cumplidas / total * 100), 1) if total > 0 else 0

    porcentaje_actividades = porcentaje(actividades_cumplidas, total_actividades)
    porcentaje_metas = porcentaje(len(metas_cumplidas), total_metas)
    porcentaje_proyectos = porcentaje(len(proyectos_cumplidos), total_proyectos)
    porcentaje_objetivos = porcentaje(len(objetivos_cumplidos), total_objetivos)

    # ===================== CONTEXTO =====================
    context = {
        # Actividades
        "total_actividades": total_actividades,
        "cumplidas": actividades_cumplidas,
        "no_cumplidas": actividades_no_cumplidas,
        "grafico_actividades_html": grafico_actividades_html,
        "porcentaje_cumplidas": porcentaje_actividades,
        # Metas
        "total_metas": total_metas,
        "metas_cumplidas": len(metas_cumplidas),
        "metas_no_cumplidas": metas_no_cumplidas,
        "grafico_metas_html": grafico_metas_html,
        "porcentaje_metas_cumplidas": porcentaje_metas,
        # Proyectos
        "total_proyectos": total_proyectos,
        "proyectos_cumplidos": len(proyectos_cumplidos),
        "proyectos_no_cumplidos": proyectos_no_cumplidos,
        "grafico_proyectos_html": grafico_proyectos_html,
        "porcentaje_proyectos_cumplidos": porcentaje_proyectos,
        # Objetivos
        "total_objetivos": total_objetivos,
        "objetivos_cumplidos": len(objetivos_cumplidos),
        "objetivos_no_cumplidos": objetivos_no_cumplidos,
        "grafico_objetivos_html": grafico_objetivos_html,
        "porcentaje_objetivos_cumplidos": porcentaje_objetivos,
    }

    return render(request, "core/dashboard.html", context)


def index(request):
    return render(request, "index.html")
