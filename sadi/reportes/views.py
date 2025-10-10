from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal, InvalidOperation
from usuarios.decorators import role_required
import io
import pandas as pd

from metas.models import Meta, AvanceMeta
from actividades.models import Actividad
from proyectos.models import Proyecto
from objetivos.models import ObjetivoEstrategico
from riesgos.models import Riesgo, Mitigacion
from departamentos.models import Departamento


# ========== VISTA PRINCIPAL ==========
@role_required("ADMIN", "APOYO", "DOCENTE", "INVITADO")
def gestion_reportes(request):
    """
    Muestra la página principal donde se elige qué reporte generar.
    """
    return render(request, "reportes/gestion_reportes.html")


@role_required("ADMIN", "APOYO", "DOCENTE")
def reporte_metas_departamento(request):
    """
    Genera un reporte de metas filtradas por departamento.
    Si el usuario es docente, solo ve su departamento.
    """
    user = request.user

    # === Filtrado por rol ===
    if user.role == "DOCENTE":
        metas = Meta.objects.filter(departamento=user.departamento)
    else:
        metas = Meta.objects.all()

    # === Filtros opcionales ===
    depto_id = request.GET.get("departamento")
    if depto_id:
        metas = metas.filter(departamento_id=depto_id)

    # === Construcción del reporte ===
    data = []
    total_progreso = 0
    metas_completadas = 0
    metas_en_progreso = 0

    for meta in metas:
        try:
            total_acum = meta.total_acumulado or Decimal("0")
            meta_cumplir = (
                Decimal(meta.metacumplir)
                if meta.metacumplir is not None
                else Decimal("0")
            )

            progreso = (
                (total_acum / meta_cumplir * Decimal("100"))
                if meta_cumplir != 0
                else Decimal("0")
            )
            progreso = progreso.quantize(Decimal("0.00"))

            # Estadísticas para las tarjetas
            total_progreso += float(progreso)
            if progreso >= 100:
                metas_completadas += 1
            elif progreso > 0:
                metas_en_progreso += 1

        except (TypeError, InvalidOperation):
            progreso = Decimal("0.00")

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
            "metacumplir_num": float(meta.metacumplir) if meta.metacumplir else 0,
            "total_acumulado": f"{total_acum} %",
            "total_acumulado_num": float(total_acum),
            "cumplimiento": f"{progreso} %",
            "progreso_num": float(progreso),
        }
        data.append(item)

    # === Cálculo de promedios ===
    promedio_cumplimiento = round(total_progreso / len(data), 1) if data else 0

    # === Exportar a Excel ===
    if "exportar" in request.GET:
        df = pd.DataFrame(data)
        # Eliminar campos numéricos temporales para la exportación
        df_export = df.drop(
            columns=["progreso_num", "total_acumulado_num", "metacumplir_num"],
            errors="ignore",
        )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_export.to_excel(writer, sheet_name="Metas", index=False)

            # Formato condicional para el libro de Excel
            workbook = writer.book
            worksheet = writer.sheets["Metas"]

            # Formato para porcentajes
            percent_format = workbook.add_format({"num_format": '0.00%" %"'})

            # Aplicar formatos
            worksheet.set_column("A:J", 15)  # Ancho de columnas
            worksheet.set_column("F:F", 25)  # Indicador más ancho
            worksheet.set_column("D:D", 30)  # Objetivo más ancho

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="reporte_metas.xlsx"'
        return response

    # === Renderizado HTML ===
    departamentos = Departamento.objects.all()
    context = {
        "metas": data,
        "departamentos": departamentos,
        "metas_completadas": metas_completadas,
        "metas_en_progreso": metas_en_progreso,
        "promedio_cumplimiento": promedio_cumplimiento,
    }
    return render(request, "reportes/reporte_metas.html", context)
