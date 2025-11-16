from programas.models import ProgramaEstrategico, Ciclo
from objetivos.models import ObjetivoEstrategico
from proyectos.models import Proyecto
from metas.models import Meta

from .models import ConfiguracionGlobal


# Context processor para obtener el estado de captura global METAS(VARIABLE B)
def estado_captura(request):
    cfg = ConfiguracionGlobal.objects.first()

    # Si por algún motivo no existe, lo creamos (evita crashes)
    if cfg is None:
        cfg = ConfiguracionGlobal.objects.create(captura_activa=True)

    return {"captura_activa": cfg.captura_activa}


def estado_sistema(request):
    """
    Context processor global para determinar el estado de configuración
    del sistema. Se usa en base.html para filtrar accesos y botones.
    """
    try:
        # Obtener ciclo actual de sesión
        ciclo_id = request.session.get("ciclo_id")
        ciclo_activo = Ciclo.objects.filter(id=ciclo_id).exists() if ciclo_id else False

        # Estado general del sistema
        estado = {
            "hay_programas": ProgramaEstrategico.objects.exists(),
            "hay_ciclos": Ciclo.objects.exists(),
            "hay_objetivos": ObjetivoEstrategico.objects.exists(),
            "hay_proyectos": Proyecto.objects.exists(),
            "hay_metas": Meta.objects.exists(),
            "ciclo_activo": ciclo_activo,
        }

    except Exception:
        # Si hay error de migración o DB vacía, evitar que el sistema se rompa
        estado = {
            "hay_programas": False,
            "hay_ciclos": False,
            "hay_objetivos": False,
            "hay_proyectos": False,
            "hay_metas": False,
            "ciclo_activo": False,
        }

    return {"estado_sistema": estado}
