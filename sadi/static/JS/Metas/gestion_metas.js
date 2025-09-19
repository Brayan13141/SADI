$(document).ready(function () {
    // DataTable
    $('#metasTable').DataTable({
        scrollX: true,
        scrollY: '500px',
        scrollCollapse: true,
        fixedColumns: {
            left: 1,
        },
        lengthMenu: [5, 10, 15, 20, 50],
        autoWidth: false,
        paging: true,
        searching: true,
        info: true,
        pageLength: 5,
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json',
        },
        // Configuración adicional para mejorar el rendimiento con muchas columnas
        deferRender: true,
        scroller: true,
        stateSave: true,
    });

    // Variable para guardar la fila seleccionada
    var selectedRow = null;

    // Cuando el usuario haga clic en una fila de la tabla
    $('#metasTable tbody').on('click', 'tr.fila-meta', function () {
        // Quitar selección previa
        $('#metasTable tbody tr').removeClass('fila-seleccionada');

        // Marcar la fila actual
        $(this).addClass('fila-seleccionada');

        // --- Tu lógica para mostrar la meta comprometida ---
        let metaId = $(this).data('id');
        let clave = $(this).data('clave');
        let nombre = $(this).data('nombre');
        let compId = $(this).data('comprometida-id');
        let compValor = $(this).data('comprometida-valor');

        if (compId) {
            $('#infoComprometida').html(`
            <p><strong>Meta:</strong> ${clave} - ${nombre}</p>
            <p><strong>Valor comprometido:</strong> ${compValor}</p>
        `);
        } else {
            $('#infoComprometida').html(`
            <p><strong>Meta:</strong> ${clave} - ${nombre}</p>
            <p class="text-danger">No tiene meta comprometida registrada.</p>
        `);
        }

        $('#btnVerComprometida')
            .removeClass('d-none')
            .attr('href', `/metas/${metaId}/comprometida/`);
    });

    // Botón Editar -> cargar datos al modal de actividades
    $('.btn-editar').on('click', function () {
        // Obtener datos de la actividad
        const actividadId = $(this).data('id');
        const estado = $(this).data('estado');
        const descripcion = $(this).data('descripcion');
        const fechaInicio = $(this).data('fecha_inicio');
        const fechaFin = $(this).data('fecha_fin');
        const metaId = $(this).data('meta_id');
        const responsableId = $(this).data('responsable_id');
        const departamentoId = $(this).data('departamento_id');

        // Llenar el formulario
        $('#actividad_id').val(actividadId);
        $('#id_estado').val(estado);
        $('#id_descripcion').val(descripcion);
        $('#id_fecha_inicio').val(fechaInicio);
        $('#id_fecha_fin').val(fechaFin);
        $('#id_meta').val(metaId);
        $('#id_responsable').val(responsableId);
        $('#id_departamento').val(departamentoId);

        // Obtener evidencias via AJAX
        $.ajax({
            url: `/actividades/${actividadId}/evidencias/`,
            method: 'GET',
            success: function (data) {
                const evidenciasContainer = $('#evidencias-existentes');
                evidenciasContainer.empty();

                if (data.evidencias && data.evidencias.length > 0) {
                    data.evidencias.forEach(function (evidencia) {
                        evidenciasContainer.append(`
                        <li class="d-flex justify-content-between align-items-center mb-2">
                            <a href="${evidencia.url}" target="_blank" class="text-truncate" style="max-width: 70%;">
                                <i class="fas fa-file-pdf text-danger me-2"></i>
                                ${evidencia.nombre}
                            </a>
                            <button type="button" class="btn btn-sm btn-outline-danger btn-eliminar-evidencia" 
                                    data-evidencia-id="${evidencia.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </li>
                    `);
                    });
                } else {
                    evidenciasContainer.append(
                        '<li class="text-muted">No hay evidencias subidas.</li>'
                    );
                }
            },
            error: function () {
                $('#evidencias-existentes').html(
                    '<li class="text-danger">Error al cargar evidencias</li>'
                );
            },
        });

        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $(
            '#formEditar input, #formEditar select, #formEditar textarea'
        ).removeClass('is-invalid');

        $('#modalEditar').modal('show');
    });

    // Validación Crear
    $('#formCrear').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresCrear').addClass('d-none').empty();
        $('input, select, textarea', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        // Validar campos requeridos
        const camposRequeridos = [
            'clave',
            'nombre',
            'enunciado',
            'proyecto',
            'indicador',
            'unidadMedida',
            'metodoCalculo',
        ];

        camposRequeridos.forEach(
            function (campo) {
                if (
                    !$('[name="' + campo + '"]', this)
                        .val()
                        .trim()
                ) {
                    errores.push('El campo ' + campo + ' es obligatorio.');
                    camposInvalidos.push($('[name="' + campo + '"]', this));
                }
            }.bind(this)
        );

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });

            $('#erroresCrear')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Validación Editar
    $('#formEditar').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $('input, select, textarea', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        // Validar campos requeridos
        const camposRequeridos = [
            'clave',
            'nombre',
            'enunciado',
            'proyecto',

            'indicador',
            'unidadMedida',
            'metodoCalculo',
        ];

        camposRequeridos.forEach(function (campo) {
            const field = $('#id_' + campo.toLowerCase());
            if (!field.val().trim()) {
                errores.push('El campo ' + campo + ' es obligatorio.');
                camposInvalidos.push(field);
            }
        });

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });

            $('#erroresEditar')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Quitar el resaltado de error cuando el usuario empiece a escribir
    $('input, select, textarea').on('input change', function () {
        $(this).removeClass('is-invalid');
    });

    // Limpiar formularios al cerrar modales
    $('#modalCrear').on('hidden.bs.modal', function () {
        $(this).find('form')[0].reset();
        $(this).find('.is-invalid').removeClass('is-invalid');
        $('#erroresCrear').addClass('d-none').empty();
    });

    $('#modalEditar').on('hidden.bs.modal', function () {
        $(this).find('.is-invalid').removeClass('is-invalid');
        $('#erroresEditar').addClass('d-none').empty();
    });
});
