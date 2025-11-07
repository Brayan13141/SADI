# mcp/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.utils import timezone
import json
import logging
import traceback
from .mcp_service import mcp_service

logger = logging.getLogger(__name__)
User = get_user_model()

def mcp_dashboard(request):
    return render(request, 'mcp/dashboard.html')

@csrf_exempt
@login_required
def mcp_api(request):
    """API sin límites artificiales"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt', '').strip()

            logger.info(f"📥 Petición recibida: '{prompt}'")

            # Obtener contexto REAL de la base de datos
            db_context = get_real_database_context(request, prompt)
            logger.info(f"📊 Contexto BD: {len(db_context)} caracteres")

            # Generar respuesta SIN limitaciones artificiales
            response = mcp_service.generate_contextual_response(prompt, db_context)
            logger.info(f"📤 Respuesta generada: {len(response)} caracteres")

            return JsonResponse({
                'success': True,
                'response': response,
                'prompt': prompt,
                'has_db_context': bool(db_context),
                'response_length': len(response)
            })

        except Exception as e:
            logger.error(f"❌ Error en mcp_api: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error en el servidor: {str(e)}'
            })

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def get_real_database_context(request, prompt):
    """Obtiene datos REALES y ESPECÍFICOS usando los modelos correctos"""
    prompt_lower = prompt.lower()
    context = ""

    try:
        # 1. PROYECTOS - Información específica
        if any(word in prompt_lower for word in ['proyecto', 'project']):
            try:
                from proyectos.models import Proyecto
                proyectos = Proyecto.objects.select_related('objetivo').all()[:8]

                if proyectos.exists():
                    proyectos_info = []
                    for i, proyecto in enumerate(proyectos, 1):
                        clave = getattr(proyecto, 'clave', 'N/A')
                        nombre = getattr(proyecto, 'nombre', f"Proyecto {proyecto.id}")
                        objetivo_nombre = getattr(proyecto.objetivo, 'clave', 'Objetivo no disponible') if proyecto.objetivo else 'Sin objetivo'

                        proyecto_text = f"{i}. {nombre}"
                        proyecto_text += f"\n   Clave: {clave}"
                        proyecto_text += f"\n   Objetivo: {objetivo_nombre}"

                        proyectos_info.append(proyecto_text)

                    context = "PROYECTOS REGISTRADOS:\n" + "\n\n".join(proyectos_info)
                else:
                    context = "No hay proyectos registrados en el sistema."

            except Exception as e:
                logger.error(f"Error al cargar proyectos: {e}")
                context = "Error al cargar proyectos."

        # 2. ACTIVIDADES - Información específica
        elif any(word in prompt_lower for word in ['actividad', 'activity', 'tarea']):
            try:
                from actividades.models import Actividad
                actividades = Actividad.objects.select_related('responsable', 'departamento', 'meta').all()[:6]

                if actividades.exists():
                    actividades_info = []
                    for i, actividad in enumerate(actividades, 1):
                        nombre = getattr(actividad, 'nombre', f"Actividad {actividad.id}")
                        descripcion = getattr(actividad, 'descripcion', 'Sin descripción')
                        estado = getattr(actividad, 'estado', 'Pendiente')
                        fecha_inicio = getattr(actividad, 'fecha_inicio', 'No especificada')
                        fecha_fin = getattr(actividad, 'fecha_fin', 'No especificada')
                        responsable = getattr(actividad.responsable, 'username', 'Sin responsable') if actividad.responsable else 'Sin responsable'

                        actividad_text = f"{i}. {nombre}"
                        actividad_text += f"\n   Estado: {estado}"
                        actividad_text += f"\n   Fechas: {fecha_inicio} a {fecha_fin}"
                        actividad_text += f"\n   Responsable: {responsable}"
                        actividad_text += f"\n   Descripción: {descripcion[:80]}{'...' if len(descripcion) > 80 else ''}"

                        actividades_info.append(actividad_text)

                    context = "ACTIVIDADES REGISTRADAS:\n" + "\n\n".join(actividades_info)
                else:
                    context = "No hay actividades registradas."

            except Exception as e:
                logger.error(f"Error al cargar actividades: {e}")
                context = "Error al cargar actividades."

        # 3. CICLOS - Información específica
        elif any(word in prompt_lower for word in ['ciclo', 'ciclos']):
            try:
                from programas.models import Ciclo
                ciclos = Ciclo.objects.select_related('programa').filter(activo=True)[:5]

                if ciclos.exists():
                    ciclos_info = []
                    for i, ciclo in enumerate(ciclos, 1):
                        nombre = getattr(ciclo, 'nombre', f"Ciclo {ciclo.id}")
                        fecha_inicio = getattr(ciclo, 'fecha_inicio', 'No especificada')
                        fecha_fin = getattr(ciclo, 'fecha_fin', 'No especificada')
                        programa = getattr(ciclo.programa, 'nombre', 'Sin programa') if ciclo.programa else 'Sin programa'
                        estado = "Activo" if getattr(ciclo, 'activo', False) else "Inactivo"

                        ciclo_text = f"{i}. {nombre}"
                        ciclo_text += f"\n   Estado: {estado}"
                        ciclo_text += f"\n   Programa: {programa}"
                        ciclo_text += f"\n   Fechas: {fecha_inicio} a {fecha_fin}"

                        ciclos_info.append(ciclo_text)

                    context = "CICLOS ACTIVOS:\n" + "\n\n".join(ciclos_info)
                else:
                    context = "No hay ciclos activos registrados."

            except Exception as e:
                logger.error(f"Error al cargar ciclos: {e}")
                context = "Error al cargar ciclos."

        # 4. METAS - Información específica
        elif any(word in prompt_lower for word in ['meta', 'metas', 'objetivo']):
            try:
                from metas.models import Meta
                metas = Meta.objects.select_related('proyecto', 'departamento', 'ciclo').filter(activa=True)[:6]

                if metas.exists():
                    metas_info = []
                    for i, meta in enumerate(metas, 1):
                        nombre = getattr(meta, 'nombre', f"Meta {meta.id}")
                        clave = getattr(meta, 'clave', 'N/A')
                        indicador = getattr(meta, 'indicador', 'Sin indicador')
                        unidad_medida = getattr(meta, 'unidadmedida', 'No especificada')
                        proyecto = getattr(meta.proyecto, 'nombre', 'Sin proyecto') if meta.proyecto else 'Sin proyecto'

                        meta_text = f"{i}. {nombre}"
                        meta_text += f"\n   Clave: {clave}"
                        meta_text += f"\n   Proyecto: {proyecto}"
                        meta_text += f"\n   Indicador: {indicador[:60]}{'...' if len(indicador) > 60 else ''}"
                        meta_text += f"\n   Unidad: {unidad_medida}"

                        metas_info.append(meta_text)

                    context = "METAS ACTIVAS:\n" + "\n\n".join(metas_info)
                else:
                    context = "No hay metas activas registradas."

            except Exception as e:
                logger.error(f"Error al cargar metas: {e}")
                context = "Error al cargar metas."

        # 5. PROGRAMAS ESTRATÉGICOS
        elif any(word in prompt_lower for word in ['programa', 'programas', 'estrategico']):
            try:
                from programas.models import ProgramaEstrategico
                programas = ProgramaEstrategico.objects.filter(estado=True)[:5]

                if programas.exists():
                    programas_info = []
                    for i, programa in enumerate(programas, 1):
                        nombre = getattr(programa, 'nombre', f"Programa {programa.id}")
                        clave = getattr(programa, 'clave', 'N/A')
                        fecha_inicio = getattr(programa, 'fecha_inicio', 'No especificada')
                        fecha_fin = getattr(programa, 'fecha_fin', 'No especificada')

                        programa_text = f"{i}. {nombre}"
                        programa_text += f"\n   Clave: {clave}"
                        programa_text += f"\n   Vigencia: {fecha_inicio} a {fecha_fin}"

                        programas_info.append(programa_text)

                    context = "PROGRAMAS ESTRATÉGICOS:\n" + "\n\n".join(programas_info)
                else:
                    context = "No hay programas estratégicos activos."

            except Exception as e:
                logger.error(f"Error al cargar programas: {e}")
                context = "Error al cargar programas."

        # 6. DEPARTAMENTOS
        elif any(word in prompt_lower for word in ['departamento', 'departamentos', 'área', 'area']):
            try:
                from departamentos.models import Departamento
                departamentos = Departamento.objects.all()[:10]

                if departamentos.exists():
                    departamentos_info = []
                    for i, depto in enumerate(departamentos, 1):
                        nombre = getattr(depto, 'nombre', f"Departamento {depto.id}")

                        depto_text = f"{i}. {nombre}"
                        departamentos_info.append(depto_text)

                    context = "DEPARTAMENTOS:\n" + "\n".join(departamentos_info)
                else:
                    context = "No hay departamentos registrados."

            except Exception as e:
                logger.error(f"Error al cargar departamentos: {e}")
                context = "Error al cargar departamentos."

        # 7. RIESGOS
        elif any(word in prompt_lower for word in ['riesgo', 'riesgos', 'mitigacion']):
            try:
                from riesgos.models import Riesgo
                riesgos = Riesgo.objects.select_related('meta').all()[:5]

                if riesgos.exists():
                    riesgos_info = []
                    for i, riesgo in enumerate(riesgos, 1):
                        enunciado = getattr(riesgo, 'enunciado', f"Riesgo {riesgo.id}")
                        probabilidad = getattr(riesgo, 'probabilidad', 0)
                        impacto = getattr(riesgo, 'impacto', 0)
                        riesgo_valor = getattr(riesgo, 'riesgo', 0)
                        meta = getattr(riesgo.meta, 'nombre', 'Meta no disponible') if riesgo.meta else 'Sin meta'

                        riesgo_text = f"{i}. {enunciado}"
                        riesgo_text += f"\n   Meta: {meta}"
                        riesgo_text += f"\n   Probabilidad: {probabilidad}, Impacto: {impacto}"
                        riesgo_text += f"\n   Nivel de riesgo: {riesgo_valor}"

                        riesgos_info.append(riesgo_text)

                    context = "RIESGOS IDENTIFICADOS:\n" + "\n\n".join(riesgos_info)
                else:
                    context = "No hay riesgos registrados."

            except Exception as e:
                logger.error(f"Error al cargar riesgos: {e}")
                context = "Error al cargar riesgos."

        # 8. AVANCE DE METAS
        elif any(word in prompt_lower for word in ['avance', 'progreso', 'cumplimiento']):
            try:
                from metas.models import AvanceMeta
                avances = AvanceMeta.objects.select_related('metacumplir', 'departamento').order_by('-fecha_registro')[:5]

                if avances.exists():
                    avances_info = []
                    for i, avance in enumerate(avances, 1):
                        avance_valor = getattr(avance, 'avance', 0)
                        fecha = getattr(avance, 'fecha_registro', 'Fecha no disponible')
                        meta = getattr(avance.metacumplir, 'nombre', 'Meta no disponible') if avance.metacumplir else 'Sin meta'
                        departamento = getattr(avance.departamento, 'nombre', 'Departamento no disponible') if avance.departamento else 'Sin departamento'

                        avance_text = f"{i}. {meta}"
                        avance_text += f"\n   Departamento: {departamento}"
                        avance_text += f"\n   Avance: {avance_valor}"
                        avance_text += f"\n   Fecha: {fecha}"

                        avances_info.append(avance_text)

                    context = "ÚLTIMOS AVANCES REGISTRADOS:\n" + "\n\n".join(avances_info)
                else:
                    context = "No hay avances registrados."

            except Exception as e:
                logger.error(f"Error al cargar avances: {e}")
                context = "Error al cargar avances."

        else:
            context = "Consulta no específica. Puedo ayudarte con: proyectos, metas, actividades, ciclos, programas, departamentos, riesgos, avances."

    except Exception as e:
        logger.error(f"Error general en get_real_database_context: {e}")
        context = "Error temporal del sistema al acceder a la base de datos."

    return context

@csrf_exempt
@login_required
def generate_report(request):
    """Generar reportes específicos del proyecto"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            report_type = data.get('report_type', 'general')

            # Obtener datos reales para el reporte
            report_data = obtener_datos_reporte_real(report_type)

            # Generar el reporte con el modelo
            prompt = f"Genera un reporte de {report_type} con estos datos: {json.dumps(report_data, indent=2)}"
            report = mcp_service.generate_response(prompt)

            return JsonResponse({
                'success': True,
                'report': report,
                'report_type': report_type,
                'data': report_data
            })

        except Exception as e:
            logger.error(f"Error en generate_report: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_datos_reporte_real(tipo_reporte):
    """Obtiene datos reales para reportes usando todos los modelos"""
    try:
        if tipo_reporte == 'metas':
            from metas.models import Meta
            metas = Meta.objects.filter(activa=True)
            return {
                'total_metas_activas': metas.count(),
                'metas_ejemplo': [
                    {
                        'nombre': m.nombre,
                        'clave': m.clave,
                        'indicador': m.indicador,
                        'unidad_medida': m.unidadmedida
                    } for m in metas[:5]
                ]
            }
        elif tipo_reporte == 'proyectos':
            from proyectos.models import Proyecto
            proyectos = Proyecto.objects.all()
            return {
                'total_proyectos': proyectos.count(),
                'proyectos_ejemplo': [
                    {
                        'nombre': p.nombre,
                        'clave': p.clave,
                        'objetivo': p.objetivo.clave if p.objetivo else 'Sin objetivo'
                    } for p in proyectos[:5]
                ]
            }
        elif tipo_reporte == 'actividades':
            from actividades.models import Actividad
            actividades = Actividad.objects.all()
            return {
                'total_actividades': actividades.count(),
                'actividades_por_estado': {
                    'pendientes': actividades.filter(estado='pendiente').count(),
                    'en_progreso': actividades.filter(estado='en_progreso').count(),
                    'completadas': actividades.filter(estado='completada').count()
                },
                'actividades_ejemplo': [
                    {
                        'nombre': a.nombre,
                        'estado': a.estado,
                        'fecha_inicio': str(a.fecha_inicio),
                        'fecha_fin': str(a.fecha_fin)
                    } for a in actividades[:5]
                ]
            }
        elif tipo_reporte == 'riesgos':
            from riesgos.models import Riesgo
            riesgos = Riesgo.objects.all()
            return {
                'total_riesgos': riesgos.count(),
                'niveles_riesgo': {
                    'alto': riesgos.filter(riesgo__gte=16).count(),
                    'medio': riesgos.filter(riesgo__range=[9, 15]).count(),
                    'bajo': riesgos.filter(riesgo__lt=9).count()
                },
                'riesgos_ejemplo': [
                    {
                        'enunciado': r.enunciado,
                        'probabilidad': r.probabilidad,
                        'impacto': r.impacto,
                        'nivel_riesgo': r.riesgo
                    } for r in riesgos[:5]
                ]
            }
        else:
            # Reporte general del sistema
            from proyectos.models import Proyecto
            from actividades.models import Actividad
            from metas.models import Meta
            from riesgos.models import Riesgo
            
            return {
                'sistema': 'SADI - Sistema de Administración Integral',
                'resumen_general': {
                    'total_proyectos': Proyecto.objects.count(),
                    'total_actividades': Actividad.objects.count(),
                    'total_metas_activas': Meta.objects.filter(activa=True).count(),
                    'total_riesgos': Riesgo.objects.count()
                }
            }
    except Exception as e:
        logger.error(f"Error en obtener_datos_reporte_real: {e}")
        return {'error': 'No se pudieron obtener datos del sistema'}

@login_required
def conversation_list(request):
    """Lista de conversaciones usando el modelo correcto"""
    from .models import MCPConversation
    conversations = MCPConversation.objects.filter(user=request.user).order_by('-updated_at')

    data = [{
        'id': conv.id,
        'title': conv.title,
        'updated_at': conv.updated_at,
        'message_count': conv.mcpmessage_set.count()  # Cambiado para usar el related_name correcto
    } for conv in conversations]

    return JsonResponse({'conversations': data})

@login_required
def conversation_detail(request, conversation_id):
    """Detalle de una conversación específica"""
    from .models import MCPConversation
    try:
        conversation = MCPConversation.objects.get(id=conversation_id, user=request.user)
        messages = conversation.mcpmessage_set.all().order_by('timestamp')  # Cambiado para usar el related_name correcto

        data = [{
            'id': msg.id,
            'content': msg.content,
            'is_user': msg.is_user,
            'timestamp': msg.timestamp
        } for msg in messages]

        return JsonResponse({'messages': data})

    except MCPConversation.DoesNotExist:
        return JsonResponse({'error': 'Conversación no encontrada'}, status=404)
