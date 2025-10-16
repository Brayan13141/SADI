from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from usuarios.decorators import role_required
import io
from openpyxl import Workbook
import pandas as pd
from django.db.models import Count, Sum
from django.utils import timezone
from metas.models import Meta, AvanceMeta
from programas.models import ProgramaEstrategico
from actividades.models import Actividad
from proyectos.models import Proyecto
from objetivos.models import ObjetivoEstrategico
from riesgos.models import Riesgo, Mitigacion
from departamentos.models import Departamento


# ========== VISTA PRINCIPAL ==========
@role_required("ADMIN", "APOYO", "DOCENTE")
def gestion_reportes(request):
    """
    Muestra la página principal donde se elige qué reporte generar.
    """
    objetivos = ObjetivoEstrategico.objects.count()
    proyectos = Proyecto.objects.count()
    metas = Meta.objects.filter(activa=True).count()
    departamentos = Departamento.objects.count()
    context = {
        "objetivos": objetivos,
        "proyectos": proyectos,
        "metas": metas,
        "departamentos": departamentos,
    }
    return render(request, "reportes/gestion_reportes.html", context)


# =================REPORTES=================
@role_required("ADMIN", "APOYO")
def reporte_metas_departamento(request):
    """
    Genera un reporte de metas filtradas por departamento.
    Si el usuario es docente, solo ve su departamento.
    """
    user = request.user

    # === Filtrado por rol ===
    if user.role == "DOCENTE":
        metas = (
            Meta.objects.select_related("proyecto", "departamento", "ciclo")
            .filter(departamento=user.departamento)
            .filter(activa=True)
        )
    else:
        metas = Meta.objects.all().filter(activa=True).order_by("id")

    # === Filtro opcional por departamento ===
    depto_id = request.GET.get("departamento")
    if depto_id:
        metas = metas.filter(departamento_id=depto_id)

    # === Construcción del reporte ===
    data = []
    total_progreso = Decimal("0")
    metas_completadas = 0
    metas_en_progreso = 0
    metas_rezagadas = 0

    for meta in metas:
        try:
            if meta.porcentages:
                total_acum = Decimal(meta.total_acumulado or 0) / 100
            else:
                total_acum = Decimal(meta.total_acumulado or 0)

            meta_cumplir = Decimal(meta.metacumplir or 0)
            # Cálculo del progreso
            progreso = (
                ((total_acum / meta_cumplir) * 100)
                if meta_cumplir > 0
                else Decimal("0")
            )

            progreso = progreso.quantize(Decimal("0.00"))

            if meta.porcentages:
                total_acum = total_acum * 100

            total_acum = total_acum.quantize(Decimal("0.00"))
            # Estadísticas
            total_progreso += progreso
            if progreso >= 100:
                metas_completadas += 1
                estado = "Cumplida"
            elif progreso > 0:
                metas_en_progreso += 1
                estado = "En progreso"
            else:
                metas_rezagadas += 1
                estado = "Rezagada"

        except (TypeError, InvalidOperation):
            progreso = Decimal("0.00")
            estado = "Rezagada"

        item = {
            "departamento": meta.departamento.nombre if meta.departamento else "-",
            "meta": meta.clave,
            "nombre": meta.nombre,
            "proyecto": meta.proyecto.nombre if meta.proyecto else "-",
            "objetivo": (
                meta.proyecto.objetivo.descripcion
                if meta.proyecto and meta.proyecto.objetivo
                else "-"
            ),
            "ciclo": meta.ciclo.nombre if meta.ciclo else "-",
            "indicador": meta.indicador,
            "lineabase": meta.lineabase_display,
            "metacumplir": meta.metacumplir_display,
            "total_acumulado": f"{total_acum} %",
            "cumplimiento": f"{progreso} %",
            "estado": estado,
        }
        data.append(item)

    # === Exportar a Excel ===
    if "exportar" in request.GET:
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Metas", index=False)
            workbook = writer.book
            worksheet = writer.sheets["Metas"]
            worksheet.set_column("A:L", 20)
            worksheet.set_column("F:F", 30)
            worksheet.set_column("E:E", 25)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            'attachment; filename="reporte_metas_departamento.xlsx"'
        )
        return response

    # === Renderizado HTML ===
    departamentos = Departamento.objects.all()
    context = {
        "metas": data,
        "departamentos": departamentos,
        "metas_completadas": metas_completadas,
        "metas_en_progreso": metas_en_progreso,
        "metas_rezagadas": metas_rezagadas,
    }
    return render(request, "reportes/reporte_metas.html", context)


@role_required("ADMIN", "APOYO")
def reporte_proyectos(request):
    """
    Reporte general de Proyectos con sus respectivas Metas.
    Muestra el cumplimiento, promedios y permite exportar a Excel.
    """

    proyectos = Proyecto.objects.prefetch_related("meta_set").all()

    data = []
    total_cumplidas = total_progreso = total_rezagadas = total_en_progreso = 0

    for proyecto in proyectos:
        metas = Meta.objects.filter(proyecto=proyecto)
        total_metas = metas.count()
        metas_cumplidas = metas_en_progreso = metas_rezagadas = 0
        porcentaje_total = Decimal("0")
        metas_data = []

        for meta in metas:
            total_acum = Decimal(meta.total_acumulado or 0)
            meta_cumplir = Decimal(meta.metacumplir or 0)

            if meta_cumplir > 0:
                progreso = (total_acum / meta_cumplir) * Decimal("100")
            else:
                progreso = Decimal("0")

            progreso = progreso.quantize(Decimal("0.00"))
            porcentaje_total += progreso

            # Clasificar meta
            if progreso >= 100:
                estado = "Cumplida"
                metas_cumplidas += 1
            elif progreso > 0:
                estado = "En progreso"
                metas_en_progreso += 1
            else:
                estado = "Rezago"
                metas_rezagadas += 1

            metas_data.append(
                {
                    "clave": meta.clave,
                    "nombre": meta.nombre,
                    "meta_cumplir": meta.metacumplir,
                    "total_acumulado": meta.total_acumulado,
                    "progreso": f"{progreso} %",
                    "estado": estado,
                }
            )

        # Promedio de cumplimiento por proyecto
        promedio_cumplimiento = (
            round(porcentaje_total / total_metas, 2) if total_metas else 0
        )

        total_cumplidas += metas_cumplidas
        total_en_progreso += metas_en_progreso
        total_rezagadas += metas_rezagadas
        total_progreso += porcentaje_total

        data.append(
            {
                "proyecto": proyecto.nombre,
                "total_metas": total_metas,
                "promedio_cumplimiento": f"{promedio_cumplimiento} %",
                "metas_cumplidas": metas_cumplidas,
                "metas_en_progreso": metas_en_progreso,
                "metas_rezagadas": metas_rezagadas,
                "metas": metas_data,  # Metas anidadas
            }
        )

    # === Exportar a Excel ===
    if "exportar" in request.GET:
        export_data = []
        for p in data:
            for m in p["metas"]:
                export_data.append(
                    {
                        "Proyecto": p["proyecto"],
                        "Clave Meta": m["clave"],
                        "Nombre Meta": m["nombre"],
                        "Meta a cumplir": m["meta_cumplir"],
                        "Total acumulado": m["total_acumulado"],
                        "Progreso": m["progreso"],
                        "Estado": m["estado"],
                    }
                )

        df = pd.DataFrame(export_data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Proyectos", index=False)
            worksheet = writer.sheets["Proyectos"]
            worksheet.set_column("A:G", 20)

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            'attachment; filename="reporte_proyectos.xlsx"'
        )
        return response

    # === Datos para gráficos ===
    nombres_proyectos = [d["proyecto"] for d in data]
    promedios = [
        float(d["promedio_cumplimiento"].replace("%", "").strip()) for d in data
    ]

    context = {
        "data": data,
        "nombres_proyectos": nombres_proyectos,
        "promedios": promedios,
        "total_cumplidas": total_cumplidas,
        "total_en_progreso": total_en_progreso,
        "total_rezagadas": total_rezagadas,
    }

    return render(request, "reportes/reporte_proyectos.html", context)


@role_required("ADMIN", "APOYO")
def reporte_avances_metas(request):
    """
    Reporte de avances de metas por departamento.
    Permite exportar a Excel.
    """
    departamento_id = request.GET.get("departamento")
    departamentos = Departamento.objects.all()

    if departamento_id:
        avances = AvanceMeta.objects.filter(departamento_id=departamento_id)
    else:
        avances = AvanceMeta.objects.all()

    data = []
    for a in avances.select_related("metaCumplir", "departamento"):
        meta = a.metaCumplir
        if not meta:
            continue

        data.append(
            {
                "departamento": a.departamento.nombre if a.departamento else "-",
                "meta": meta.nombre or meta.clave,
                "proyecto": meta.proyecto.nombre,
                "ciclo": meta.ciclo.nombre if meta.ciclo else "-",
                "fecha_registro": a.fecha_registro,
                "avance": (
                    float(a.avance * 100) if meta.porcentages else float(a.avance)
                ),
                "meta_cumplir": (
                    float(meta.metacumplir * 100)
                    if meta.porcentages
                    else float(meta.metacumplir or 0)
                ),
            }
        )

    # === EXPORTAR A EXCEL ===
    if "exportar" in request.GET:
        df = pd.DataFrame(data)
        response = HttpResponse(content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = (
            'attachment; filename="reporte_avances_metas.xlsx"'
        )
        df.to_excel(response, index=False)
        return response

    context = {
        "data": data,
        "departamentos": departamentos,
    }
    return render(request, "reportes/reporte_avances_metas.html", context)


@role_required("ADMIN", "APOYO")
def reporte_riesgos(request):
    """
    Reporte general de riesgos con sus niveles y mitigaciones.
    Permite exportar a Excel.
    """

    riesgos = Riesgo.objects.select_related("meta").all()

    data = []
    niveles = {"Bajo": 0, "Medio": 0, "Alto": 0}

    for r in riesgos:
        meta_nombre = r.meta.nombre if r.meta else "-"
        probabilidad = r.probabilidad or 0
        impacto = r.impacto or 0
        nivel_riesgo = r.riesgo or "Sin clasificar"

        # Contabilizar niveles de riesgo para el gráfico
        if nivel_riesgo in niveles:
            niveles[nivel_riesgo] += 1
        else:
            niveles["Bajo"] += 1  # Por defecto

        data.append(
            {
                "meta": meta_nombre,
                "enunciado": r.enunciado,
                "probabilidad": probabilidad,
                "impacto": impacto,
                "nivel_riesgo": nivel_riesgo,
            }
        )

    # === EXPORTAR A EXCEL ===
    if "exportar" in request.GET:
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Riesgos")
            workbook = writer.book
            worksheet = writer.sheets["Riesgos"]
            worksheet.set_column("A:E", 25)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="reporte_riesgos.xlsx"'
        return response

    # === Contexto para template ===
    context = {
        "data": data,
        "niveles_labels": list(niveles.keys()),
        "niveles_values": list(niveles.values()),
        "total_riesgos": len(riesgos),
    }
    return render(request, "reportes/reporte_riesgos.html", context)


@role_required("DOCENTE")
def reporte_general_docente(request):
    """
    Reporte de seguimiento general para DOCENTES.
    Incluye resumen y permite exportar a Excel.
    """

    user = request.user
    departamento = user.departamento

    # === Datos base ===
    metas = (
        Meta.objects.filter(departamento=user.departamento)
        .filter(activa=True)
        .order_by("id")
    )
    total_metas = metas.count()
    metas_cumplidas = 0
    metas_en_progreso = 0
    metas_rezagadas = 0
    total_avance = Decimal("0")

    data = []
    for meta in metas:

        meta_cumplir = Decimal(meta.metacumplir if meta.metacumplir is not None else 0)
        avances = AvanceMeta.objects.filter(metaCumplir=meta)

        if meta.porcentages:
            meta_cumplirF = meta_cumplir * Decimal("100")
            total_acum = avances.aggregate(total=Sum("avance"))["total"] or Decimal("0")
        else:
            meta_cumplirF = meta_cumplir
            total_acum = avances.aggregate(total=Sum("avance"))["total"] or Decimal("0")

        meta_cumplir = Decimal(meta.metacumplir or 0)

        if meta_cumplir > 0:
            progreso = (total_acum / meta_cumplir) * Decimal("100")
        else:
            progreso = Decimal("0")

        progreso = progreso.quantize(Decimal("0.00"))

        acumulado = (total_acum * Decimal("100")).quantize(Decimal("0.00"))
        total_avance += progreso

        # Clasificación
        if progreso >= 100:
            estado = "Cumplida"
            metas_cumplidas += 1
        elif progreso >= 50:
            estado = "En progreso"
            metas_en_progreso += 1
        else:
            estado = "Rezagada"
            metas_rezagadas += 1

        data.append(
            {
                "meta": meta.nombre,
                "proyecto": meta.proyecto.nombre if meta.proyecto else "-",
                "objetivo": (
                    meta.proyecto.objetivo.descripcion
                    if meta.proyecto and meta.proyecto.objetivo
                    else "-"
                ),
                "indicador": meta.indicador,
                "meta_a_cumplir": meta_cumplirF,
                "acumulado": acumulado,
                "cumplimiento": progreso,
                "estado": estado,
            }
        )

    # === Exportar a Excel ===
    if "export" in request.GET:
        wb = Workbook()
        ws = wb.active
        ws.title = "Reporte General Docente"

        # Encabezado
        ws.append(
            [
                "Meta",
                "Proyecto",
                "Objetivo",
                "Indicador",
                "Meta a Cumplir",
                "Acumulado",
                "Cumplimiento (%)",
                "Estado",
            ]
        )

        # Contenido
        for row in data:
            ws.append(
                [
                    row["meta"],
                    row["proyecto"],
                    row["objetivo"],
                    row["indicador"],
                    float(row["meta_a_cumplir"]),
                    float(row["acumulado"]),
                    float(row["cumplimiento"]),
                    row["estado"],
                ]
            )

        # Nombre del archivo
        filename = f"Reporte_Docente_{timezone.now().strftime('%Y%m%d_%H%M')}.xlsx"
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response

    # === Determinar estado general tipo semáforo ===
    if metas_rezagadas == 0:
        estado_general = "🟢 Buen Desempeño"
    elif metas_rezagadas > metas.count() / 2:
        estado_general = "🟡 En riesgo"
    else:
        estado_general = "🔴 Crítico"

    # === Encabezado y resumen ejecutivo ===
    encabezado = {
        "titulo": f"Reporte de Seguimiento - {departamento.nombre if departamento else 'Departamento'}",
        "fecha_emision": timezone.now().strftime("%d/%m/%Y"),
        "preparado_por": f"{user.get_full_name()} ({user.role})",
        "destinatarios": "Coordinador Académico, Jefatura de Departamento, Dirección Académica",
        "objetivo_proyecto": "Dar seguimiento al avance de las metas asignadas al docente y su contribución al logro de los objetivos institucionales.",
    }

    resumen_ejecutivo = {
        "estado_general": estado_general,
        "logros_principales": f"Se completaron {metas_cumplidas} metas de un total de {total_metas}.",
        "problemas_criticos": (
            "Existen metas rezagadas que requieren revisión y apoyo adicional."
            if metas_rezagadas > 0
            else "Sin incidencias críticas en el periodo."
        ),
        "recomendacion": (
            "Continuar con el ritmo actual y reforzar el seguimiento de metas en progreso."
            if estado_general == "🟢 Buen Desempeño"
            else "Revisar las metas con menor avance y ajustar las estrategias de ejecución."
        ),
    }

    # === Contexto para la plantilla ===
    context = {
        "encabezado": encabezado,
        "resumen": resumen_ejecutivo,
        "data": data,
        "total_metas": total_metas,
        "metas_cumplidas": metas_cumplidas,
        "metas_en_progreso": metas_en_progreso,
        "metas_rezagadas": metas_rezagadas,
    }

    return render(request, "reportes/reporte_docente.html", context)
