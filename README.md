# SADI – Sistema de Administración y Dirección Institucional

SADI es una plataforma de gestión institucional que permite administrar programas estratégicos, objetivos, proyectos, metas, actividades, avances y evidencias dentro de un marco jerárquico anual basado en ciclos.  
El sistema está desarrollado con Django, PostgreSQL y una arquitectura modular que separa componentes globales y dependientes del tiempo.

## Características principales

### 1. Estructura jerárquica global
- **Programa Estratégico**: agrupa ciclos 
- **Objetivo Estratégico**: asociado a un programa, organiza proyectos.
- **Proyecto**: depende de un objetivo, agrupa metas.
- **Meta**: elemento global que define un indicador, unidad de medida, método de cálculo y parámetros base.

### 2. Componentes dependientes del ciclo
Cada ciclo (por ejemplo 2024 o 2025) agrega valores y registros específicos:

- **MetaCiclo**: asigna `lineaBase` y `metaCumplir` a cada Meta según el año.
- **MetaComprometida**: registra valores comprometidos anuales. #YA NO SE USA
- **AvanceMeta**: guarda avances por ciclo.
- **Actividad**: acciones específicas vinculadas a una Meta y un ciclo.
- **Evidencia**: documentos cargados por cada actividad.
- **SolicitudReapertura**: solicitudes para reabrir actividades cerradas.
- **Riesgo y Mitigación**: análisis de riesgos por actividad.

### 3. Usuarios y departamentos
- **Usuario** basado en `AbstractUser`.
- Roles: Administrador, Apoyo, Docente, Invitado.
- Relación 1:1 con **Departamento**.
- Control de acceso basado en rol y departamento.

### 4. Validación jerárquica del avance
- Un objetivo se completa cuando todos sus proyectos lo están.
- Un proyecto se completa cuando todas sus metas lo están.
- Una meta se completa cuando sus avances superen la metaCumplir en base al ciclo.

### 5. Modelos principales
Incluye:
- Departamento
- Usuario
- ProgramaEstrategico
- ObjetivoEstrategico
- Proyecto
- Meta
- MetaCiclo
- MetaComprometida #YA NO SE USA
- AvanceMeta
- Actividad
- Evidencia
- SolicitudReapertura
- Riesgo
- Mitigación

Todos los modelos críticos incluyen control de cambios mediante históricos.

### 6. Base de datos
Backend en **PostgreSQL**, compatible con la estructura generada por Django ORM.

### 8. Arquitectura Frontend
- Templates Django con Bootstrap.
- Dashboard con gráficos dinámicos.
- Integración de filtros por departamento y ciclo.

### 9. Seguridad
- Autenticación estándar de Django.
- Roles y permisos por departamento.
- Control de edición basado en estado.
- Histórico de cambios para auditoría.

### 10. Próximas mejoras
- Reportes PDF automáticos.



