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
    # ================== ACTIVIDADES ==================
    total_actividades = Actividad.objects.count()
    actividades_cumplidas = Actividad.objects.filter(estado="Cumplida").count()
    actividades_no_cumplidas = total_actividades - actividades_cumplidas

    # Gráfico de actividades
    fig_actividades = px.pie(
        names=["Cumplidas", "No Cumplidas"],
        values=[actividades_cumplidas, actividades_no_cumplidas],
        title="Estado de las Actividades",
        color_discrete_sequence=["#E74C3C", "#2ECC71"],
    )
    fig_actividades.update_traces(textinfo="percent+label", pull=[0.05, 0])
    grafico_actividades_html = pio.to_html(
        fig_actividades, full_html=False, include_plotlyjs="cdn"
    )

    # ==================  METAS (según actividades) ==================
    metas = Meta.objects.all()
    metas_cumplidas = 0
    metas_con_actividades = 0

    for meta in metas:
        actividades_meta = Actividad.objects.filter(meta=meta)
        if actividades_meta.exists():
            metas_con_actividades += 1
            if all(a.estado == "Cumplida" for a in actividades_meta):
                metas_cumplidas += 1

    total_metas = metas_con_actividades  # Solo contamos metas que tienen actividades
    metas_no_cumplidas = total_metas - metas_cumplidas

    # Gráfico de metas
    fig_metas = px.bar(
        x=["Cumplidas", "No Cumplidas"],
        y=[metas_cumplidas, metas_no_cumplidas],
        color=["Cumplidas", "No Cumplidas"],
        title="Cumplimiento de Metas (en base a Actividades)",
        text=[metas_cumplidas, metas_no_cumplidas],
        color_discrete_sequence=["#1ABC9C", "#E74C3C"],
    )
    fig_metas.update_traces(textposition="outside")
    grafico_metas_html = pio.to_html(fig_metas, full_html=False, include_plotlyjs=False)

    # ==================  PROYECTOS (según metas) ==================
    proyectos = Proyecto.objects.all()
    proyectos_cumplidos = 0
    proyectos_con_metas = 0

    for proyecto in proyectos:
        metas_proyecto = Meta.objects.filter(proyecto=proyecto)
        if metas_proyecto.exists():
            proyecto_cumplido = True
            proyectos_con_metas += 1

            for meta in metas_proyecto:
                actividades_meta = Actividad.objects.filter(meta=meta)
                if actividades_meta.exists():
                    if not all(a.estado == "Cumplida" for a in actividades_meta):
                        proyecto_cumplido = False
                        break
                else:
                    # Si una meta no tiene actividades, no se considera cumplida
                    proyecto_cumplido = False
                    break

            if proyecto_cumplido:
                proyectos_cumplidos += 1

    total_proyectos = proyectos_con_metas  # Solo proyectos con metas
    proyectos_no_cumplidos = total_proyectos - proyectos_cumplidos

    # Gráfico de proyectos
    fig_proyectos = px.pie(
        names=["Completados", "En Proceso"],
        values=[proyectos_cumplidos, proyectos_no_cumplidos],
        title="Estado de los Proyectos (en base a Metas)",
        color_discrete_sequence=["#F39C12", "#3498DB"],
    )
    fig_proyectos.update_traces(textinfo="percent+label", pull=[0.05, 0])
    grafico_proyectos_html = pio.to_html(
        fig_proyectos, full_html=False, include_plotlyjs=False
    )

    # ================== OBJETIVOS (según proyectos) ==================
    objetivos = ObjetivoEstrategico.objects.all()
    objetivos_cumplidos = 0
    objetivos_con_proyectos = 0

    for objetivo in objetivos:
        proyectos_objetivo = Proyecto.objects.filter(objetivo=objetivo)
        if proyectos_objetivo.exists():
            objetivo_cumplido = True
            objetivos_con_proyectos += 1

            for proyecto in proyectos_objetivo:
                metas_proyecto = Meta.objects.filter(proyecto=proyecto)
                if metas_proyecto.exists():
                    proyecto_cumplido = True

                    for meta in metas_proyecto:
                        actividades_meta = Actividad.objects.filter(meta=meta)
                        if actividades_meta.exists():
                            if not all(
                                a.estado == "Cumplida" for a in actividades_meta
                            ):
                                proyecto_cumplido = False
                                break
                        else:
                            proyecto_cumplido = False
                            break

                    if not proyecto_cumplido:
                        objetivo_cumplido = False
                        break
                else:
                    # Si un proyecto no tiene metas, no se considera cumplido
                    objetivo_cumplido = False
                    break

            if objetivo_cumplido:
                objetivos_cumplidos += 1

    total_objetivos = objetivos_con_proyectos  # Solo objetivos con proyectos
    objetivos_no_cumplidos = total_objetivos - objetivos_cumplidos

    # Gráfico de objetivos
    fig_objetivos = px.bar(
        x=["Cumplidos", "En Proceso"],
        y=[objetivos_cumplidos, objetivos_no_cumplidos],
        color=["Cumplidos", "En Proceso"],
        title="Cumplimiento de Objetivos (en base a Proyectos)",
        text=[objetivos_cumplidos, objetivos_no_cumplidos],
        color_discrete_sequence=["#2E86C1", "#F5B041"],
    )
    fig_objetivos.update_traces(textposition="outside")
    grafico_objetivos_html = pio.to_html(
        fig_objetivos, full_html=False, include_plotlyjs=False
    )

    # ================== CÁLCULO DE PORCENTAJES ==================
    porcentaje_actividades = (
        round((actividades_cumplidas / total_actividades * 100), 1)
        if total_actividades > 0
        else 0
    )
    porcentaje_metas = (
        round((metas_cumplidas / total_metas * 100), 1) if total_metas > 0 else 0
    )
    porcentaje_proyectos = (
        round((proyectos_cumplidos / total_proyectos * 100), 1)
        if total_proyectos > 0
        else 0
    )
    porcentaje_objetivos = (
        round((objetivos_cumplidos / total_objetivos * 100), 1)
        if total_objetivos > 0
        else 0
    )

    # ================== CONTEXTO ==================
    context = {
        # Actividades
        "total_actividades": total_actividades,
        "cumplidas": actividades_cumplidas,
        "no_cumplidas": actividades_no_cumplidas,
        "grafico_actividades_html": grafico_actividades_html,
        "porcentaje_cumplidas": porcentaje_actividades,
        # Metas
        "total_metas": total_metas,
        "metas_cumplidas": metas_cumplidas,
        "metas_no_cumplidas": metas_no_cumplidas,
        "grafico_metas_html": grafico_metas_html,
        "porcentaje_metas_cumplidas": porcentaje_metas,
        # Proyectos
        "total_proyectos": total_proyectos,
        "proyectos_cumplidos": proyectos_cumplidos,
        "proyectos_no_cumplidos": proyectos_no_cumplidos,
        "porcentaje_proyectos_cumplidos": porcentaje_proyectos,
        "grafico_proyectos_html": grafico_proyectos_html,
        # Objetivos
        "total_objetivos": total_objetivos,
        "objetivos_cumplidos": objetivos_cumplidos,
        "objetivos_no_cumplidos": objetivos_no_cumplidos,
        "porcentaje_objetivos_cumplidos": porcentaje_objetivos,
        "grafico_objetivos_html": grafico_objetivos_html,
    }

    return render(request, "core/dashboard.html", context)


def index(request):
    return render(request, "index.html")
