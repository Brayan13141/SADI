from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal
from django.db.models import Prefetch, Sum
from usuarios.decorators import role_required
import io
from openpyxl import Workbook
import pandas as pd
from django.utils import timezone
from metas.models import Meta, AvanceMeta

from actividades.models import Actividad
from proyectos.models import Proyecto
from objetivos.models import ObjetivoEstrategico
from riesgos.models import Riesgo
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
    Reporte de Metas agrupadas por departamento.
    Una meta se marca como 'Cumplida' solo si TODAS sus actividades están cumplidas.
    """

    # --- FILTRO POR DEPARTAMENTO ---
    departamento_id = request.GET.get("departamento")
    departamentos = Departamento.objects.all()

    # Prefetch actividades para optimizar consultas - CORREGIDO
    metas_query = Meta.objects.prefetch_related(
        Prefetch(
            "actividad_set", queryset=Actividad.objects.select_related("responsable")
        )
    ).select_related(
        "proyecto", "ciclo", "departamento"
    )  # Incluir departamento en select_related

    # Filtrar por departamento - CORREGIDO (usando el campo departamento directo de Meta)
    if departamento_id:
        metas_query = metas_query.filter(departamento_id=departamento_id)

    metas = metas_query.order_by("departamento__nombre", "nombre")

    # --- PROCESAMIENTO DE METAS ---
    resultados = []
    stats = {"completadas": 0, "en_progreso": 0, "rezagadas": 0}

    for meta in metas:
        actividades = meta.actividad_set.all()
        total_acts = actividades.count()

        # INICIALIZAR VARIABLES PARA TODOS LOS CASOS
        completadas = 0
        cumplimiento = 0
        estado = "Rezagada"

        if total_acts > 0:
            completadas = actividades.filter(estado__iexact="Cumplida").count()
            cumplimiento = (completadas / total_acts) * 100

            # Estado general de la meta según actividades
            if completadas == total_acts:
                estado = "Cumplida"
                stats["completadas"] += 1
            elif completadas == 0:
                estado = "Rezagada"
                stats["rezagadas"] += 1
            else:
                estado = "En progreso"
                stats["en_progreso"] += 1
        else:
            # Si no hay actividades, se considera rezagada
            stats["rezagadas"] += 1

        restante = max(0, 100 - cumplimiento)

        resultados.append(
            {
                "id": meta.id,
                "clave": meta.clave,
                "nombre": meta.nombre,
                "indicador": meta.indicador,
                "metacumplir": meta.metacumplir_display,  # Usar property display
                "total_acumulado": meta.total_acumulado,  # Usar property
                "proyecto": meta.proyecto.nombre if meta.proyecto else "N/A",
                "departamento": (
                    meta.departamento.nombre if meta.departamento else "N/A"
                ),  # Campo directo
                "ciclo": meta.ciclo.nombre if meta.ciclo else "N/A",
                "estado": estado,
                "cumplimiento": round(cumplimiento, 2),
                "restante": round(restante, 2),
                "total_actividades": total_acts,
                "actividades_cumplidas": completadas,  # Ahora siempre definida
                "actividades": [
                    {
                        "nombre": act.nombre,
                        "descripcion": act.descripcion,
                        "fecha_inicio": act.fecha_inicio,
                        "fecha_fin": act.fecha_fin,
                        "estado": act.estado,
                        "responsable": (
                            f"{act.responsable.first_name} {act.responsable.last_name}".strip()
                            if act.responsable
                            else "Sin asignar"
                        ),
                    }
                    for act in actividades
                ],
            }
        )

    # Calcular totales para el resumen
    total_metas = len(resultados)
    porcentaje_cumplimiento = (
        (stats["completadas"] / total_metas * 100) if total_metas > 0 else 0
    )

    # === EXPORTAR A EXCEL ===
    if "exportar" in request.GET:
        import pandas as pd
        import io
        from django.http import HttpResponse

        # Preparar datos para Excel
        excel_data = []
        for meta in resultados:
            excel_data.append(
                {
                    "Clave": meta["clave"],
                    "Nombre": meta["nombre"],
                    "Proyecto": meta["proyecto"],
                    "Departamento": meta["departamento"],
                    "Ciclo": meta["ciclo"],
                    "Indicador": meta["indicador"],
                    "Meta a Cumplir": meta["metacumplir"],
                    "Total Acumulado": meta["total_acumulado"],
                    "Estado": meta["estado"],
                    "Cumplimiento (%)": meta["cumplimiento"],
                    "Total Actividades": meta["total_actividades"],
                    "Actividades Cumplidas": meta["actividades_cumplidas"],
                    "Porcentaje Actividades": f"{(meta['actividades_cumplidas']/meta['total_actividades']*100) if meta['total_actividades'] > 0 else 0:.2f}%",
                }
            )

        # Crear DataFrame
        df = pd.DataFrame(excel_data)

        # Crear buffer en memoria
        buffer = io.BytesIO()

        # Usar ExcelWriter con xlsxwriter
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            # Exportar datos principales
            df.to_excel(writer, index=False, sheet_name="Metas")

            # Obtener el worksheet y ajustar columnas
            worksheet = writer.sheets["Metas"]

            # Ajustar el ancho de las columnas
            worksheet.set_column("A:A", 15)  # Clave
            worksheet.set_column("B:B", 30)  # Nombre
            worksheet.set_column("C:C", 25)  # Proyecto
            worksheet.set_column("D:D", 20)  # Departamento
            worksheet.set_column("E:E", 15)  # Ciclo
            worksheet.set_column("F:F", 40)  # Indicador
            worksheet.set_column("G:H", 15)  # Meta a Cumplir y Total Acumulado
            worksheet.set_column("I:I", 15)  # Estado
            worksheet.set_column("J:J", 15)  # Cumplimiento
            worksheet.set_column("K:L", 15)  # Actividades
            worksheet.set_column("M:M", 20)  # Porcentaje Actividades

        # Preparar respuesta
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            'attachment; filename="reporte_metas_departamento.xlsx"'
        )
        return response

    context = {
        "metas": resultados,
        "departamentos": departamentos,
        "departamento_seleccionado": int(departamento_id) if departamento_id else None,
        "stats": stats,
        "total_metas": total_metas,
        "metas_cumplidas": stats["completadas"],
        "metas_pendientes": stats["en_progreso"] + stats["rezagadas"],
        "porcentaje_cumplimiento": round(porcentaje_cumplimiento, 1),
    }

    return render(request, "reportes/reporte_metas.html", context)


@role_required("ADMIN", "APOYO")
def reporte_proyectos(request):
    """
    Reporte general de Proyectos con sus respectivas Metas.
    Muestra el total de metas, cuántas están cumplidas o rezagadas,
    y exporta los resultados a Excel.
    """

    proyectos = Proyecto.objects.prefetch_related("meta_set").all()
    data = []
    total_cumplidas = total_rezagadas = total_en_progreso = 0

    for proyecto in proyectos:
        metas = Meta.objects.filter(proyecto=proyecto)
        total_metas = metas.count()

        metas_cumplidas = metas_en_progreso = metas_rezagadas = 0
        metas_data = []

        for meta in metas:
            actividades = Actividad.objects.filter(meta=meta)
            total_actividades = actividades.count()

            # === Determinar estado de la meta según sus actividades ===
            if total_actividades == 0:
                estado_meta = "Rezago"
                metas_rezagadas += 1
            else:
                cumplidas = actividades.filter(estado="Cumplida").count()
                no_cumplidas = actividades.exclude(estado="Cumplida").count()

                if cumplidas == total_actividades:
                    estado_meta = "Cumplida"
                    metas_cumplidas += 1
                elif cumplidas == 0:
                    estado_meta = "Rezago"
                    metas_rezagadas += 1
                else:
                    estado_meta = "En progreso"
                    metas_en_progreso += 1

            metas_data.append(
                {
                    "clave": meta.clave,
                    "nombre": meta.nombre,
                    "total_actividades": total_actividades,
                    "estado": estado_meta,
                }
            )

        # === Totales por proyecto ===
        total_cumplidas += metas_cumplidas
        total_en_progreso += metas_en_progreso
        total_rezagadas += metas_rezagadas

        data.append(
            {
                "proyecto": proyecto.nombre,
                "total_metas": total_metas,
                "metas_cumplidas": metas_cumplidas,
                "metas_en_progreso": metas_en_progreso,
                "metas_rezagadas": metas_rezagadas,
                "metas": metas_data,
            }
        )

    # === EXPORTAR A EXCEL ===
    if "exportar" in request.GET:
        export_data = []
        for p in data:
            for m in p["metas"]:
                export_data.append(
                    {
                        "Proyecto": p["proyecto"],
                        "Clave Meta": m["clave"],
                        "Nombre Meta": m["nombre"],
                        "Total Actividades": m["total_actividades"],
                        "Estado": m["estado"],
                    }
                )

        df = pd.DataFrame(export_data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Proyectos", index=False)
            worksheet = writer.sheets["Proyectos"]
            worksheet.set_column("A:E", 25)

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
    cumplidas = [d["metas_cumplidas"] for d in data]
    rezagadas = [d["metas_rezagadas"] for d in data]
    en_progreso = [d["metas_en_progreso"] for d in data]

    context = {
        "data": data,
        "nombres_proyectos": nombres_proyectos,
        "cumplidas": cumplidas,
        "rezagadas": rezagadas,
        "en_progreso": en_progreso,
        "total_cumplidas": total_cumplidas,
        "total_en_progreso": total_en_progreso,
        "total_rezagadas": total_rezagadas,
    }

    return render(request, "reportes/reporte_proyectos.html", context)


@role_required("ADMIN", "APOYO")
def reporte_avances_metas(request):
    """
    Reporte de avances de metas por departamento.
    Muestra los avances y permite exportar a Excel.
    """
    departamento_id = request.GET.get("departamento")
    departamentos = Departamento.objects.all()

    # Filtro por departamento
    avances = AvanceMeta.objects.all().select_related(
        "metaCumplir__proyecto", "metaCumplir__ciclo", "departamento"
    )
    if departamento_id:
        avances = avances.filter(departamento_id=departamento_id)

    data = []
    for a in avances:
        meta = a.metaCumplir
        if not meta:
            continue

        usa_porcentaje = getattr(meta, "porcentages", False)

        # Cálculo de porcentaje real
        try:
            porcentaje_avance = (
                (a.avance / meta.metacumplir) * 100
                if meta.metacumplir and meta.metacumplir != 0
                else 0
            )
        except (TypeError, ZeroDivisionError):
            porcentaje_avance = 0

        data.append(
            {
                "departamento": a.departamento.nombre if a.departamento else "-",
                "meta": meta.nombre or meta.clave,
                "proyecto": meta.proyecto.nombre if meta.proyecto else "-",
                "ciclo": meta.ciclo.nombre if meta.ciclo else "-",
                "fecha_registro": a.fecha_registro.strftime("%d/%m/%Y"),
                "avance": (
                    round(a.avance * 100, 2) if usa_porcentaje else round(a.avance, 2)
                ),
                "meta_cumplir": (
                    round(meta.metacumplir * 100, 2)
                    if usa_porcentaje
                    else round(meta.metacumplir or 0, 2)
                ),
                "porcentaje_cumplimiento": round(porcentaje_avance, 2),
            }
        )

    # === EXPORTAR A EXCEL ===
    if "exportar" in request.GET:
        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        )
        response["Content-Disposition"] = (
            'attachment; filename="reporte_avances_metas.xlsx"'
        )
        df.to_excel(response, index=False)
        return response

    context = {
        "data": data,
        "departamentos": departamentos,
        "departamento_seleccionado": int(departamento_id) if departamento_id else None,
    }
    return render(request, "reportes/reporte_avances_metas.html", context)


@role_required("ADMIN", "APOYO")
def reporte_riesgos(request):
    """
    Reporte general de riesgos con sus niveles y mitigaciones.
    Permite exportar a Excel.
    """
    riesgos = (
        Riesgo.objects.select_related("meta").prefetch_related("mitigacion_set").all()
    )

    data = []
    niveles = {"Bajo": 0, "Medio": 0, "Alto": 0, "Crítico": 0}

    for r in riesgos:
        meta_nombre = r.meta.nombre if r.meta else "-"
        probabilidad = r.probabilidad or 0
        impacto = r.impacto or 0
        valor_riesgo = r.riesgo or (probabilidad * impacto)

        # Clasificación correcta del riesgo
        if valor_riesgo <= 25:
            nivel_riesgo = "Bajo"
            color = "success"
            icono = "🟢"
        elif valor_riesgo <= 50:
            nivel_riesgo = "Medio"
            color = "warning"
            icono = "🟡"
        elif valor_riesgo <= 90:
            nivel_riesgo = "Alto"
            color = "orange"
            icono = "🟠"
        else:
            nivel_riesgo = "Crítico"
            color = "danger"
            icono = "🔴"

        niveles[nivel_riesgo] += 1

        mitigaciones = r.mitigacion_set.all()
        ultima_mitigacion = mitigaciones.last()

        data.append(
            {
                "meta": meta_nombre,
                "enunciado": r.enunciado,
                "probabilidad": probabilidad,
                "impacto": impacto,
                "valor_riesgo": valor_riesgo,
                "nivel_riesgo": nivel_riesgo,
                "color": color,
                "icono": icono,
                "tiene_mitigaciones": mitigaciones.exists(),
                "total_mitigaciones": mitigaciones.count(),
                "ultima_mitigacion": (
                    ultima_mitigacion.accion if ultima_mitigacion else "Sin acciones"
                ),
            }
        )

    # Ordenar datos por nivel de riesgo (Crítico primero)
    orden = {"Crítico": 4, "Alto": 3, "Medio": 2, "Bajo": 1}
    data.sort(key=lambda x: orden.get(x["nivel_riesgo"], 0), reverse=True)

    # === EXPORTAR A EXCEL ===
    if "exportar" in request.GET:
        excel_data = [
            {
                "Meta": d["meta"],
                "Riesgo": d["enunciado"],
                "Probabilidad": d["probabilidad"],
                "Impacto": d["impacto"],
                "Valor Riesgo": d["valor_riesgo"],
                "Nivel": d["nivel_riesgo"],
                "Mitigaciones": d["total_mitigaciones"],
                "Última Acción": d["ultima_mitigacion"],
            }
            for d in data
        ]

        df = pd.DataFrame(excel_data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Riesgos")
            worksheet = writer.sheets["Riesgos"]
            worksheet.set_column("A:H", 25)

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
        "riesgos_bajos": niveles["Bajo"],
        "riesgos_medios": niveles["Medio"],
        "riesgos_altos": niveles["Alto"],
        "riesgos_criticos": niveles["Crítico"],
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
        Meta.objects.filter(departamento=user.departamento, activa=True)
        .select_related("proyecto", "ciclo")
        .prefetch_related("actividad_set")
        .order_by("id")
    )

    total_metas = metas.count()
    metas_cumplidas = 0
    metas_en_progreso = 0
    metas_rezagadas = 0
    total_avance = Decimal("0")

    data = []
    for meta in metas:
        # Calcular progreso basado en actividades (como en la vista anterior)
        actividades = meta.actividad_set.all()
        total_acts = actividades.count()

        # INICIALIZAR VARIABLES PARA TODOS LOS CASOS
        completadas = 0
        cumplimiento = Decimal("0")  # Cambiado a Decimal
        estado = "Rezagada"

        if total_acts > 0:
            completadas = actividades.filter(estado__iexact="Cumplida").count()
            # Convertir a Decimal para operaciones consistentes
            cumplimiento = Decimal(completadas / total_acts * 100)

            # Estado general de la meta según actividades
            if completadas == total_acts:
                estado = "Cumplida"
                metas_cumplidas += 1
            elif completadas == 0:
                estado = "Rezagada"
                metas_rezagadas += 1
            else:
                estado = "En progreso"
                metas_en_progreso += 1
        else:
            # Si no hay actividades, se considera rezagada
            estado = "Rezagada"
            metas_rezagadas += 1

        # Calcular también el avance tradicional (para compatibilidad)
        meta_cumplir = Decimal(meta.metacumplir if meta.metacumplir is not None else 0)
        avances = meta.avancemeta_set.all()

        if meta.porcentages:
            meta_cumplirF = meta_cumplir * Decimal("100")
            total_acum = avances.aggregate(total=Sum("avance"))["total"] or Decimal("0")
        else:
            meta_cumplirF = meta_cumplir
            total_acum = avances.aggregate(total=Sum("avance"))["total"] or Decimal("0")

        if meta_cumplir > 0:
            progreso_tradicional = (total_acum / meta_cumplir) * Decimal("100")
        else:
            progreso_tradicional = Decimal("0")

        progreso_tradicional = progreso_tradicional.quantize(Decimal("0.00"))
        acumulado = (
            (total_acum * Decimal("100")).quantize(Decimal("0.00"))
            if meta.porcentages
            else total_acum.quantize(Decimal("0.00"))
        )

        # CORREGIDO: Sumar Decimal con Decimal
        total_avance += cumplimiento

        data.append(
            {
                "meta": meta.nombre or meta.clave,
                "clave": meta.clave,
                "proyecto": meta.proyecto.nombre if meta.proyecto else "-",
                "objetivo": (
                    meta.proyecto.objetivo.descripcion
                    if meta.proyecto and meta.proyecto.objetivo
                    else "-"
                ),
                "indicador": meta.indicador,
                "meta_a_cumplir": float(
                    meta_cumplirF.quantize(Decimal("0.00"))
                ),  # Convertir a float para template
                "acumulado": float(acumulado),  # Convertir a float para template
                "cumplimiento": float(
                    cumplimiento.quantize(Decimal("0.00"))
                ),  # Convertir a float para template
                "estado": estado,
                "total_actividades": total_acts,
                "actividades_cumplidas": completadas,
                "actividades": [
                    {
                        "nombre": act.nombre,
                        "descripcion": act.descripcion,
                        "fecha_inicio": act.fecha_inicio,
                        "fecha_fin": act.fecha_fin,
                        "estado": act.estado,
                        "responsable": (
                            f"{act.responsable.first_name} {act.responsable.last_name}".strip()
                            if act.responsable
                            else "Sin asignar"
                        ),
                    }
                    for act in actividades
                ],
            }
        )

    # === EXPORTAR A EXCEL (actualizado) ===
    if "exportar" in request.GET:
        import pandas as pd
        import io
        from django.http import HttpResponse

        # Preparar datos para Excel
        excel_data = []
        for meta in data:
            excel_data.append(
                {
                    "Clave": meta["clave"],
                    "Meta": meta["meta"],
                    "Proyecto": meta["proyecto"],
                    "Objetivo": meta["objetivo"],
                    "Indicador": meta["indicador"],
                    "Meta a Cumplir": meta["meta_a_cumplir"],
                    "Acumulado": meta["acumulado"],
                    "Cumplimiento (%)": meta["cumplimiento"],
                    "Estado": meta["estado"],
                    "Total Actividades": meta["total_actividades"],
                    "Actividades Cumplidas": meta["actividades_cumplidas"],
                    "Porcentaje Actividades": f"{(meta['actividades_cumplidas']/meta['total_actividades']*100) if meta['total_actividades'] > 0 else 0:.2f}%",
                }
            )

        # Crear DataFrame
        df = pd.DataFrame(excel_data)

        # Crear buffer en memoria
        buffer = io.BytesIO()

        # Usar ExcelWriter con xlsxwriter
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            # Exportar datos principales
            df.to_excel(writer, index=False, sheet_name="Metas Docente")

            # Obtener el worksheet y ajustar columnas
            worksheet = writer.sheets["Metas Docente"]

            # Ajustar el ancho de las columnas
            worksheet.set_column("A:A", 15)  # Clave
            worksheet.set_column("B:B", 30)  # Meta
            worksheet.set_column("C:C", 25)  # Proyecto
            worksheet.set_column("D:D", 40)  # Objetivo
            worksheet.set_column("E:E", 40)  # Indicador
            worksheet.set_column("F:G", 15)  # Meta a Cumplir y Acumulado
            worksheet.set_column("H:H", 15)  # Cumplimiento
            worksheet.set_column("I:I", 15)  # Estado
            worksheet.set_column("J:K", 15)  # Actividades
            worksheet.set_column("L:L", 20)  # Porcentaje Actividades

        # Preparar respuesta
        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="reporte_docente_{user.username}_{timezone.now().strftime("%Y%m%d")}.xlsx"'
        )
        return response

    # === Determinar estado general tipo semáforo ===
    if total_metas == 0:
        estado_general = "⚪ Sin metas asignadas"
    elif metas_rezagadas == 0 and metas_cumplidas == total_metas:
        estado_general = "🟢 Excelente desempeño"
    elif metas_rezagadas == 0:
        estado_general = "🟢 Buen desempeño"
    elif metas_rezagadas > total_metas / 2:
        estado_general = "🔴 Crítico"
    else:
        estado_general = "🟡 En riesgo"

    # Calcular porcentajes para el resumen
    porcentaje_cumplimiento = (
        (metas_cumplidas / total_metas * 100) if total_metas > 0 else 0
    )

    resumen_ejecutivo = {
        "estado_general": estado_general,
        "logros_principales": f"Se completaron {metas_cumplidas} metas de un total de {total_metas} ({porcentaje_cumplimiento:.1f}%).",
        "problemas_criticos": (
            f"Existen {metas_rezagadas} metas rezagadas que requieren revisión y apoyo adicional."
            if metas_rezagadas > 0
            else "Sin incidencias críticas en el periodo."
        ),
        "recomendacion": (
            "Continuar con el ritmo actual y reforzar el seguimiento de metas en progreso."
            if estado_general in ["🟢 Excelente desempeño", "🟢 Buen desempeño"]
            else "Revisar las metas con menor avance y ajustar las estrategias de ejecución."
        ),
    }

    # === Contexto para la plantilla ===
    context = {
        "resumen": resumen_ejecutivo,
        "departamento": departamento.nombre if departamento else "-",
        "metas": data,  # Cambiado de "data" a "metas" para consistencia con el template
        "total_metas": total_metas,
        "metas_cumplidas": metas_cumplidas,
        "metas_en_progreso": metas_en_progreso,
        "metas_rezagadas": metas_rezagadas,
        "porcentaje_cumplimiento": round(porcentaje_cumplimiento, 1),
        "stats": {  # Para compatibilidad con el template
            "completadas": metas_cumplidas,
            "en_progreso": metas_en_progreso,
            "rezagadas": metas_rezagadas,
        },
    }

    return render(request, "reportes/reporte_docente.html", context)
