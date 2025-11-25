from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from django.db.models import Prefetch, Sum
from usuarios.decorators import role_required
import io
from datetime import datetime
import pandas as pd
from programas.models import Ciclo
from metas.models import Meta, AvanceMeta, MetaCiclo
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
    Reporte de Metas agrupadas por departamento y ciclo,
    con cálculo del avance en base a AvanceMeta y MetaCiclo.
    """
    # --- FILTROS ---
    departamento_id = request.GET.get("departamento")
    ciclo_id = request.session.get("ciclo_id")

    departamentos = Departamento.objects.all()
    ciclos = Ciclo.objects.all()

    # --- CONSULTA PRINCIPAL ---
    metas_ciclo = MetaCiclo.objects.select_related(
        "meta", "ciclo", "meta__proyecto", "meta__departamento"
    ).prefetch_related(
        Prefetch(
            "meta__actividad_set",
            queryset=Actividad.objects.select_related("responsable"),
        )
    )

    if departamento_id:
        metas_ciclo = metas_ciclo.filter(meta__departamento_id=departamento_id)
    if ciclo_id:
        metas_ciclo = metas_ciclo.filter(ciclo_id=ciclo_id)

    metas_ciclo = metas_ciclo.order_by("meta__departamento__nombre", "meta__nombre")

    resultados = []
    stats = {"completadas": 0, "en_progreso": 0, "rezagadas": 0}

    # --- PROCESAMIENTO PRINCIPAL ---
    for mc in metas_ciclo:
        meta = mc.meta
        ciclo = mc.ciclo

        # ----------------------------------------
        # CALCULO CORRECTO DEL AVANCE DE LA META
        # ----------------------------------------
        avances = AvanceMeta.objects.filter(metaCumplir=meta, ciclo=ciclo).order_by(
            "fecha_registro"
        )

        if not avances.exists():
            avance_real = Decimal("0")
        else:
            if meta.acumulable:
                avance_real = avances.last().avance or Decimal("0")
            else:
                # Acumulable = suma total
                avance_real = avances.aggregate(total=Sum("avance"))[
                    "total"
                ] or Decimal("0")

        # Valores del ciclo
        linea_base = mc.lineaBase or Decimal("0")
        meta_cumplir = mc.metaCumplir or Decimal("0")

        # Calcular % de avance
        if meta_cumplir > 0:
            porcentaje_avance = (avance_real / meta_cumplir) * Decimal("100")
        else:
            porcentaje_avance = Decimal("0")

        # Limitar entre 0-100
        porcentaje_avance = round(porcentaje_avance, 2)

        # ----------------------------------------
        # NUEVO: CÁLCULO DE ESTADO SEGÚN AVANCE VS META
        # ----------------------------------------
        if avance_real >= meta_cumplir:
            estado_avance = "Cumplida"
            stats["completadas"] += 1
        elif avance_real > Decimal("0"):
            estado_avance = "En progreso"
            stats["en_progreso"] += 1
        else:
            estado_avance = "Rezagada"
            stats["rezagadas"] += 1

        # ----------------------------------------
        # FORMATEOS DISPLAY
        # ----------------------------------------
        if meta.porcentages:
            avance_display = (
                f"{(avance_real * Decimal('100')).quantize(Decimal('0.00'))} %"
            )
            linea_base_display = (
                f"{(linea_base * Decimal('100')).quantize(Decimal('0.00'))} %"
            )
            meta_cumplir_display = (
                f"{(meta_cumplir * Decimal('100')).quantize(Decimal('0.00'))} %"
            )
        else:
            avance_display = f"{avance_real.quantize(Decimal('0.00'))}"
            linea_base_display = f"{linea_base.quantize(Decimal('0.00'))}"
            meta_cumplir_display = f"{meta_cumplir.quantize(Decimal('0.00'))}"

        # ----------------------------------------
        # ESTADO SEGÚN ACTIVIDADES (se mantiene para display)
        # ----------------------------------------
        actividades = meta.actividad_set.filter(ciclo_id=ciclo.id)
        total_acts = actividades.count()
        completadas = actividades.filter(estado__iexact="Cumplida").count()

        if total_acts == 0:
            estado_actividades = "Rezagada"
        elif completadas == total_acts:
            estado_actividades = "Cumplida"
        elif completadas == 0:
            estado_actividades = "Rezagada"
        else:
            estado_actividades = "En progreso"

        cumplimiento_actividades = (
            (completadas / total_acts) * 100 if total_acts > 0 else 0
        )

        resultados.append(
            {
                "id": meta.id,
                "clave": meta.clave,
                "nombre": meta.nombre,
                "indicador": meta.indicador,
                "metacumplir": meta_cumplir_display,
                "lineabase": linea_base_display,
                "total_acumulado": avance_display,
                "porcentaje_avance": float(porcentaje_avance),
                "proyecto": meta.proyecto.nombre if meta.proyecto else "N/A",
                "departamento": (
                    meta.departamento.nombre if meta.departamento else "N/A"
                ),
                "ciclo": ciclo.nombre if ciclo else "N/A",
                "estado": estado_avance,  # Ahora usa el estado por avance
                "estado_actividades": estado_actividades,  # Nuevo campo para estado de actividades
                "cumplimiento": round(cumplimiento_actividades, 2),
                "restante": round(100 - cumplimiento_actividades, 2),
                "total_actividades": total_acts,
                "actividades_cumplidas": completadas,
                "categoria": "Acumulable" if meta.acumulable else "Incremental",
                "avance_real": float(avance_real),  # Para referencia
                "meta_cumplir_valor": float(meta_cumplir),  # Para referencia
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

    total_metas = len(resultados)

    # ----------------------------------------
    # EXPORTACIÓN A EXCEL
    # ----------------------------------------
    if "exportar" in request.GET:

        excel_data = [
            {
                "Clave": r["clave"],
                "Nombre": r["nombre"],
                "Proyecto": r["proyecto"],
                "Departamento": r["departamento"],
                "Ciclo": r["ciclo"],
                "Indicador": r["indicador"],
                "Categoría": r["categoria"],
                "Línea Base": r["lineabase"],
                "Meta a Cumplir": r["metacumplir"],
                "Total Avance": r["total_acumulado"],
                "Porcentaje Avance (%)": r["porcentaje_avance"],
                "Estado (por Avance)": r["estado"],  # Actualizado
                "Estado (por Actividades)": r["estado_actividades"],  # Nuevo
                "Cumplimiento Actividades (%)": r["cumplimiento"],
                "Total Actividades": r["total_actividades"],
                "Actividades Cumplidas": r["actividades_cumplidas"],
            }
            for r in resultados
        ]

        df = pd.DataFrame(excel_data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Metas")
            writer.sheets["Metas"].set_column("A:P", 20)  # Ajustado por nueva columna

        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            'attachment; filename="reporte_metas_departamento.xlsx"'
        )
        return response

    # ----------------------------------------
    # CONTEXTO FINAL
    # ----------------------------------------
    context = {
        "metas": resultados,
        "departamentos": departamentos,
        "ciclos": ciclos,
        "departamento_seleccionado": int(departamento_id) if departamento_id else None,
        "ciclo_seleccionado": int(ciclo_id) if ciclo_id else None,
        "stats": stats,
        "total_metas": total_metas,
        "metas_cumplidas": stats["completadas"],
        "metas_pendientes": stats["en_progreso"] + stats["rezagadas"],
    }

    return render(request, "reportes/reporte_metas.html", context)


@role_required("ADMIN", "APOYO")
def reporte_proyectos(request):
    proyectos_cumplidos = 0
    proyectos_en_progreso = 0
    proyectos_rezagados = 0

    ciclo_id = request.session.get("ciclo_id")
    ciclo = Ciclo.objects.filter(id=ciclo_id).first()

    proyectos = Proyecto.objects.all().order_by("nombre")

    data = []
    total_cumplidas = total_en_progreso = total_rezagadas = 0

    for proyecto in proyectos:
        metas = Meta.objects.filter(proyecto=proyecto)

        metas_cumplidas = metas_en_progreso = metas_rezagadas = 0
        metas_data = []
        total_metas_validas = 0

        for meta in metas:
            mc = MetaCiclo.objects.filter(meta=meta, ciclo=ciclo).first()
            if not mc:
                continue

            total_metas_validas += 1
            meta_target = mc.metaCumplir or Decimal("0")

            avances = AvanceMeta.objects.filter(metaCumplir=meta, ciclo=ciclo).order_by(
                "fecha_registro"
            )

            if meta.acumulable:
                ultimo = avances.last()
                avance_real = (
                    ultimo.avance if ultimo and ultimo.avance else Decimal("0")
                )
            else:
                avance_real = avances.aggregate(suma=Sum("avance"))["suma"] or Decimal(
                    "0"
                )

            if meta_target == 0:
                porcentaje_real = 0.0
            else:
                porcentaje_real = float((avance_real / meta_target) * 100)
                porcentaje_real = round(porcentaje_real, 2)

            if porcentaje_real >= 100:
                estado_meta = "Cumplida"
                metas_cumplidas += 1
            elif porcentaje_real > 0:
                estado_meta = "En progreso"
                metas_en_progreso += 1
            else:
                estado_meta = "Rezagada"
                metas_rezagadas += 1

            metas_data.append(
                {
                    "clave": meta.clave,
                    "nombre": meta.nombre,
                    "meta_target": float(meta_target),
                    "avance_real": float(round(avance_real, 2)),
                    "porcentaje_real": porcentaje_real,
                    "estado": estado_meta,
                }
            )

        if total_metas_validas == 0:
            estado_proyecto = "Sin metas en este ciclo"
        elif metas_cumplidas == total_metas_validas:
            estado_proyecto = "Cumplido"
            proyectos_cumplidos += 1
        elif metas_en_progreso > 0:
            estado_proyecto = "En progreso"
            proyectos_en_progreso += 1
        else:
            estado_proyecto = "Rezago"
            proyectos_rezagados += 1

        total_cumplidas += metas_cumplidas
        total_en_progreso += metas_en_progreso
        total_rezagadas += metas_rezagadas

        data.append(
            {
                "proyecto": proyecto.nombre,
                "estado": estado_proyecto,
                "total_metas": total_metas_validas,
                "metas_cumplidas": metas_cumplidas,
                "metas_en_progreso": metas_en_progreso,
                "metas_rezagadas": metas_rezagadas,
                "metas": metas_data,
            }
        )

    proyectos_por_estado = {
        "Cumplido": proyectos_cumplidos,
        "En progreso": proyectos_en_progreso,
        "Rezago": proyectos_rezagados,
    }

    if "exportar" in request.GET:

        excel_rows = []

        for d in data:
            for m in d["metas"]:
                excel_rows.append(
                    {
                        "Proyecto": d["proyecto"],
                        "Estado Proyecto": d["estado"],
                        "Clave Meta": m["clave"],
                        "Nombre Meta": m["nombre"],
                        "Meta a Cumplir": m["meta_target"],
                        "Avance Real": m["avance_real"],
                        "Porcentaje (%)": m["porcentaje_real"],
                        "Estado Meta": m["estado"],
                    }
                )

        df = pd.DataFrame(excel_rows)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Proyectos")
            worksheet = writer.sheets["Proyectos"]
            worksheet.set_column("A:H", 25)

        buffer.seek(0)
        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            'attachment; filename="reporte_proyectos.xlsx"'
        )
        return response
    context = {
        "data": data,
        "nombres_proyectos": [d["proyecto"] for d in data],
        "estados_proyectos": [d["estado"] for d in data],
        "cumplidas": [d["metas_cumplidas"] for d in data],
        "rezagadas": [d["metas_rezagadas"] for d in data],
        "en_progreso": [d["metas_en_progreso"] for d in data],
        "total_cumplidas": total_cumplidas,
        "total_en_progreso": total_en_progreso,
        "total_rezagadas": total_rezagadas,
        "proyectos_cumplidos": proyectos_cumplidos,
        "proyectos_en_progreso": proyectos_en_progreso,
        "proyectos_rezagados": proyectos_rezagados,
        "proyectos_por_estado": proyectos_por_estado,
        "labels_estados": list(proyectos_por_estado.keys()),
        "valores_estados": list(proyectos_por_estado.values()),
        "ciclos": Ciclo.objects.all(),
        "ciclo_seleccionado": ciclo,
        "hay_datos": len(data) > 0,
    }

    return render(request, "reportes/reporte_proyectos.html", context)


@role_required("ADMIN", "APOYO")
def reporte_avances_metas(request):

    departamento_id = request.GET.get("departamento")
    ciclo_id = request.session.get("ciclo_id")

    departamentos = Departamento.objects.all()
    ciclos = Ciclo.objects.all()

    # === Consulta base ===
    metas_query = Meta.objects.select_related(
        "proyecto", "departamento"
    ).prefetch_related(
        Prefetch(
            "avancemeta_set",
            queryset=(
                AvanceMeta.objects.filter(ciclo_id=ciclo_id)
                if ciclo_id
                else AvanceMeta.objects.all()
            ),
            to_attr="avances_filtrados",
        ),
        Prefetch(
            "metas_ciclo",
            queryset=(
                MetaCiclo.objects.filter(ciclo_id=ciclo_id)
                if ciclo_id
                else MetaCiclo.objects.all()
            ),
            to_attr="meta_ciclo_actual",
        ),
    )

    # === Filtro por departamento (DE LA META) ===
    if departamento_id:
        metas_query = metas_query.filter(departamento_id=departamento_id)

    data = []

    for meta in metas_query:
        # Obtener meta_ciclo correspondiente
        meta_ciclo = None
        if hasattr(meta, "meta_ciclo_actual") and meta.meta_ciclo_actual:
            meta_ciclo = meta.meta_ciclo_actual[0]

        if not meta_ciclo:
            continue

        usa_porcentaje = meta.porcentages

        # Valores base
        linea_base = meta_ciclo.lineaBase or Decimal("0")
        meta_cumplir = meta_ciclo.metaCumplir or Decimal("0")

        # Sumar avances del ciclo
        avances = getattr(meta, "avances_filtrados", [])
        avance_total = sum((a.avance or Decimal("0")) for a in avances)

        # Normalización para mostrar
        def mostrar(valor):
            try:
                if usa_porcentaje:
                    valor = valor * Decimal("100")
                return float(valor.quantize(Decimal("0.01")))
            except:
                return 0.0

        # Calcular porcentaje de avance
        if meta_cumplir > 0:
            porcentaje_avance = (avance_total / meta_cumplir) * Decimal("100")
        else:
            porcentaje_avance = Decimal("0")

        porcentaje_avance = float(porcentaje_avance.quantize(Decimal("0.01")))

        # Estado de meta
        if avance_total >= meta_cumplir and meta_cumplir > 0:
            estado = "Cumplida"
        elif avance_total > 0:
            estado = "En progreso"
        else:
            estado = "Rezago"

        data.append(
            {
                "departamento": meta.departamento.nombre if meta.departamento else "-",
                "proyecto": meta.proyecto.nombre if meta.proyecto else "-",
                "clave_meta": meta.clave,
                "meta": meta.nombre or meta.clave,
                "linea_base": mostrar(linea_base),
                "meta_cumplir": mostrar(meta_cumplir),
                "avance_total": mostrar(avance_total),
                "porcentaje_avance": porcentaje_avance,
                "estado": estado,
                "tipo_meta": "Porcentaje" if usa_porcentaje else "Valor Absoluto",
                "acumulable": "Sí" if meta.acumulable else "No",
            }
        )

    # === Exportar a Excel ===
    if "exportar" in request.GET:
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Avances Metas", index=False)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            'attachment; filename="reporte_avances_metas.xlsx"'
        )
        return response

    context = {
        "data": data,
        "hay_datos": len(data) > 0,
        "departamentos": departamentos,
        "ciclos": ciclos,
        "departamento_seleccionado": int(departamento_id) if departamento_id else None,
        "ciclo_seleccionado": int(ciclo_id) if ciclo_id else None,
        "total_registros": len(data),
    }

    return render(request, "reportes/reporte_avances_metas.html", context)


@role_required("ADMIN", "APOYO")
def reporte_riesgos(request):
    """
    Reporte general de riesgos por actividad y meta.
    Filtrado por ciclo activo y exportable a Excel.
    """

    ciclo_id = request.session.get("ciclo_id")

    # === Query base ===
    riesgos = (
        Riesgo.objects.select_related("actividad", "actividad__meta")
        .prefetch_related("mitigacion_set")
        .order_by("actividad__meta__nombre", "actividad__nombre")
    )

    if ciclo_id:
        riesgos = riesgos.filter(actividad__ciclo_id=ciclo_id)

    data = []
    niveles = {"Bajo": 0, "Medio": 0, "Alto": 0, "Crítico": 0}

    for r in riesgos:

        meta_nombre = (
            r.actividad.meta.nombre if r.actividad and r.actividad.meta else "-"
        )
        actividad_nombre = r.actividad.nombre if r.actividad else "-"

        probabilidad = r.probabilidad or 0
        impacto = r.impacto or 0

        # === Cálculo seguro ===
        valor_riesgo = r.riesgo if r.riesgo is not None else (probabilidad * impacto)

        # === Clasificación ===
        if valor_riesgo <= 25:
            nivel_riesgo = "Bajo"
            color = "success"
        elif valor_riesgo <= 50:
            nivel_riesgo = "Medio"
            color = "warning"
        elif valor_riesgo <= 90:
            nivel_riesgo = "Alto"
            color = "danger"  # Para evitar clases inexistentes
        else:
            nivel_riesgo = "Crítico"
            color = "dark"

        niveles[nivel_riesgo] += 1

        # === Mitigaciones ===
        mitigaciones = r.mitigacion_set.all()

        ultima = mitigaciones.order_by(
            "-id"
        ).first()  # seguridad si no hay orden definido

        data.append(
            {
                "meta": meta_nombre,
                "actividad": actividad_nombre,
                "enunciado": r.enunciado,
                "probabilidad": probabilidad,
                "impacto": impacto,
                "valor_riesgo": valor_riesgo,
                "nivel_riesgo": nivel_riesgo,
                "color": color,
                "tiene_mitigaciones": mitigaciones.exists(),
                "total_mitigaciones": mitigaciones.count(),
                "ultima_mitigacion": ultima.accion if ultima else "Sin acciones",
            }
        )

    # === Ordenar Crítico → Bajo ===
    orden = {"Crítico": 4, "Alto": 3, "Medio": 2, "Bajo": 1}
    data.sort(key=lambda x: orden[x["nivel_riesgo"]], reverse=True)

    # === Excel ===
    if "exportar" in request.GET:
        export = [
            {
                "Meta": d["meta"],
                "Actividad": d["actividad"],
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

        df = pd.DataFrame(export)
        buffer = io.BytesIO()

        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Riesgos")
            sheet = writer.sheets["Riesgos"]
            sheet.set_column("A:I", 25)

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="reporte_riesgos.xlsx"'
        return response

    # === Contexto ===
    context = {
        "data": data,
        "hay_datos": len(data) > 0,
        "niveles_labels": list(niveles.keys()),
        "niveles_values": list(niveles.values()),
        "total_riesgos": riesgos.count(),
        "riesgos_bajos": niveles["Bajo"],
        "riesgos_medios": niveles["Medio"],
        "riesgos_altos": niveles["Alto"],
        "riesgos_criticos": niveles["Crítico"],
    }

    return render(request, "reportes/reporte_riesgos.html", context)


@role_required("DOCENTE")
def reporte_general_docente(request):
    """
    Reporte para docentes que muestra avances de metas (AvanceMeta)
    y estado basado en actividades, optimizado para cálculo correcto
    """
    from decimal import Decimal
    from django.db.models import Prefetch, Sum

    user = request.user
    departamento = user.departamento
    ciclo_id = request.session.get("ciclo_id")
    ciclo = Ciclo.objects.filter(id=ciclo_id).first()

    if not ciclo:
        return render(
            request,
            "reportes/reporte_docente.html",
            {
                "error": "No hay ciclo activo seleccionado",
                "metas": [],
                "total_metas": 0,
            },
        )

    # === CONSULTAS OPTIMIZADAS ===
    metas_ciclo_prefetch = Prefetch(
        "metas_ciclo",
        queryset=MetaCiclo.objects.filter(ciclo=ciclo),
        to_attr="meta_ciclo_actual",
    )

    avances_prefetch = Prefetch(
        "avancemeta_set",
        queryset=AvanceMeta.objects.filter(ciclo=ciclo).order_by("fecha_registro"),
        to_attr="avances_ciclo_actual",
    )

    actividades_prefetch = Prefetch(
        "actividad_set",
        queryset=Actividad.objects.filter(ciclo=ciclo).select_related("responsable"),
        to_attr="actividades_ciclo_actual",
    )

    # === CONSULTA PRINCIPAL OPTIMIZADA ===
    metas = (
        Meta.objects.filter(
            departamento=departamento,
            activa=True,
            metas_ciclo__ciclo=ciclo,  # Solo metas que participan en este ciclo
        )
        .select_related("proyecto")
        .prefetch_related(metas_ciclo_prefetch, avances_prefetch, actividades_prefetch)
        .distinct()  # Evitar duplicados por el join con metas_ciclo
        .order_by("clave")
    )

    resultados = []
    # Stats basadas en AVANCES de metas
    stats_avances = {"completadas": 0, "en_progreso": 0, "rezagadas": 0}
    # Stats basadas en ACTIVIDADES
    stats_actividades = {"completadas": 0, "en_progreso": 0, "rezagadas": 0}

    for meta in metas:
        # === OBTENER META CICLO ACTUAL ===
        meta_ciclo = None
        if hasattr(meta, "meta_ciclo_actual") and meta.meta_ciclo_actual:
            meta_ciclo = meta.meta_ciclo_actual[0]

        if not meta_ciclo:
            continue  # Meta no tiene configuración para este ciclo

        # === VALORES DEL CICLO ===
        linea_base = meta_ciclo.lineaBase or Decimal("0")
        meta_cumplir = meta_ciclo.metaCumplir or Decimal("0")

        # === CÁLCULO DE AVANCES (MANTENIENDO LÓGICA SOLICITADA) ===
        avances = getattr(meta, "avances_ciclo_actual", [])

        if not avances:
            avance_real = Decimal("0")
        else:
            # LÓGICA ACTUAL (como se solicitó)
            if meta.acumulable:
                # Para metas acumulables: tomar el ÚLTIMO avance
                avance_real = avances[-1].avance
            else:
                # Para metas no acumulables: SUMAR todos los avances
                avance_real = sum(a.avance for a in avances)

        # === PORCENTAJE DE AVANCE ===
        if meta_cumplir > 0:
            porcentaje_avance = (avance_real / meta_cumplir) * Decimal("100")
        else:
            porcentaje_avance = Decimal("0")

        # Limitar porcentaje entre 0-100
        porcentaje_avance = round(porcentaje_avance, 2)
        if porcentaje_avance > 100:
            porcentaje_avance = 100
        elif porcentaje_avance < 0:
            porcentaje_avance = 0

        # === ESTADO DE LA META SEGÚN AVANCES ===
        if meta_cumplir == 0:
            estado_avance = "Sin meta"
            stats_avances["rezagadas"] += 1
        elif porcentaje_avance >= 100:
            estado_avance = "Cumplida"
            stats_avances["completadas"] += 1
        elif porcentaje_avance > 0:
            estado_avance = "En progreso"
            stats_avances["en_progreso"] += 1
        else:
            estado_avance = "Rezagada"
            stats_avances["rezagadas"] += 1

        # === CÁLCULO DE ACTIVIDADES ===
        actividades = getattr(meta, "actividades_ciclo_actual", [])
        total_acts = len(actividades)

        # Contar actividades cumplidas (case-insensitive)
        completadas = sum(1 for act in actividades if act.estado.lower() == "cumplida")

        # Calcular porcentaje de cumplimiento de actividades
        if total_acts > 0:
            cumplimiento_actividades = (completadas / total_acts) * 100
        else:
            cumplimiento_actividades = 0

        # === ESTADO SEGÚN ACTIVIDADES ===
        if total_acts == 0:
            estado_actividades = "Sin actividades"
            stats_actividades["rezagadas"] += 1
        elif completadas == total_acts:
            estado_actividades = "Cumplida"
            stats_actividades["completadas"] += 1
        elif completadas == 0:
            estado_actividades = "Rezagada"
            stats_actividades["rezagadas"] += 1
        else:
            estado_actividades = "En progreso"
            stats_actividades["en_progreso"] += 1

        # === FORMATEO PARA DISPLAY ===
        if meta.porcentages:
            avance_display = (
                f"{(avance_real * Decimal('100')).quantize(Decimal('0.00'))} %"
            )
            linea_base_display = (
                f"{(linea_base * Decimal('100')).quantize(Decimal('0.00'))} %"
            )
            meta_cumplir_display = (
                f"{(meta_cumplir * Decimal('100')).quantize(Decimal('0.00'))} %"
            )
        else:
            avance_display = f"{avance_real.quantize(Decimal('0.00'))}"
            linea_base_display = f"{linea_base.quantize(Decimal('0.00'))}"
            meta_cumplir_display = f"{meta_cumplir.quantize(Decimal('0.00'))}"

        # === CONSTRUIR RESULTADO ===
        resultados.append(
            {
                "id": meta.id,
                "clave": meta.clave,
                "nombre": meta.nombre,
                "indicador": meta.indicador,
                "linea_base": linea_base_display,
                "meta_cumplir": meta_cumplir_display,
                "avance_real": avance_display,
                "avance_real_raw": float(avance_real.quantize(Decimal("0.00"))),
                "porcentaje_avance": float(porcentaje_avance),
                "proyecto": meta.proyecto.nombre if meta.proyecto else "N/A",
                # Estado principal: basado en AVANCES
                "estado": estado_avance,
                "estado_avance": estado_avance,  # Para claridad
                "estado_actividades": estado_actividades,  # Estado por actividades
                "cumplimiento_actividades": round(cumplimiento_actividades, 2),
                "restante_actividades": round(100 - cumplimiento_actividades, 2),
                "total_actividades": total_acts,
                "actividades_cumplidas": completadas,
                "categoria": "Acumulable" if meta.acumulable else "Incremental",
                "tipo_meta": "Porcentual" if meta.porcentages else "Numérica",
                "actividades": [
                    {
                        "nombre": act.nombre or "Sin nombre",
                        "descripcion": act.descripcion,
                        "fecha_inicio": (
                            act.fecha_inicio.strftime("%d/%m/%Y")
                            if act.fecha_inicio
                            else "Sin fecha"
                        ),
                        "fecha_fin": (
                            act.fecha_fin.strftime("%d/%m/%Y")
                            if act.fecha_fin
                            else "Sin fecha"
                        ),
                        "estado": act.estado,
                        "responsable": (
                            f"{act.responsable.first_name} {act.responsable.last_name}".strip()
                            if act.responsable and act.responsable.first_name
                            else getattr(act.responsable, "username", "Sin asignar")
                        ),
                    }
                    for act in actividades
                ],
            }
        )

    total_metas = len(resultados)

    # === EXPORTACIÓN A EXCEL ===
    if "exportar" in request.GET and resultados:
        excel_data = []
        for r in resultados:
            excel_data.append(
                {
                    "Clave": r["clave"],
                    "Nombre": r["nombre"],
                    "Proyecto": r["proyecto"],
                    "Indicador": r["indicador"],
                    "Categoría": r["categoria"],
                    "Tipo Meta": r["tipo_meta"],
                    "Línea Base": r["linea_base"],
                    "Meta a Cumplir": r["meta_cumplir"],
                    "Avance Real": r["avance_real"],
                    "Porcentaje Avance (%)": r["porcentaje_avance"],
                    "Estado (Avances)": r["estado_avance"],
                    "Estado (Actividades)": r["estado_actividades"],
                    "Cumplimiento Actividades (%)": r["cumplimiento_actividades"],
                    "Total Actividades": r["total_actividades"],
                    "Actividades Cumplidas": r["actividades_cumplidas"],
                }
            )

        df = pd.DataFrame(excel_data)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Metas Docente")
            worksheet = writer.sheets["Metas Docente"]

            # Formato de columnas automático
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                worksheet.set_column(idx, idx, min(max_len, 25))

        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="reporte_docente_{user.username}_{ciclo.nombre.replace(" ", "_")}.xlsx"'
        )
        return response

    # === RESUMEN GENERAL (basado en AVANCES) ===
    if total_metas == 0:
        estado_general = "Sin metas asignadas en este ciclo"
        color_estado = "secondary"
    elif stats_avances["completadas"] == total_metas:
        estado_general = "Excelente - Todas las metas cumplidas"
        color_estado = "success"
    elif stats_avances["rezagadas"] == 0:
        estado_general = "Buen progreso - Sin metas rezagadas"
        color_estado = "info"
    elif stats_avances["rezagadas"] > total_metas / 2:
        estado_general = "Atención - Múltiples metas rezagadas"
        color_estado = "danger"
    else:
        estado_general = "En progreso - Algunas metas requieren atención"
        color_estado = "warning"

    porcentaje_cumplimiento = (
        (stats_avances["completadas"] / total_metas) * 100 if total_metas > 0 else 0
    )

    resumen = {
        "estado_general": estado_general,
        "color_estado": color_estado,
        "total_metas": total_metas,
        "metas_cumplidas": stats_avances["completadas"],
        "metas_en_progreso": stats_avances["en_progreso"],
        "metas_rezagadas": stats_avances["rezagadas"],
        "porcentaje_cumplimiento": round(porcentaje_cumplimiento, 2),
        # Estadísticas adicionales de actividades
        "actividades_totales": sum(r["total_actividades"] for r in resultados),
        "actividades_cumplidas_total": sum(
            r["actividades_cumplidas"] for r in resultados
        ),
    }

    # Calcular porcentaje de actividades cumplidas
    if resumen["actividades_totales"] > 0:
        resumen["porcentaje_actividades"] = round(
            (resumen["actividades_cumplidas_total"] / resumen["actividades_totales"])
            * 100,
            2,
        )
    else:
        resumen["porcentaje_actividades"] = 0

    return render(
        request,
        "reportes/reporte_docente.html",
        {
            "metas": resultados,
            "resumen": resumen,
            "total_metas": total_metas,
            "ciclo_actual": ciclo,
            "departamento": departamento,
            "stats_avances": stats_avances,
            "stats_actividades": stats_actividades,
        },
    )
