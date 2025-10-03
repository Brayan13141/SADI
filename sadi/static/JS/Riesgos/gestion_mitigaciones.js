$(document).ready(function () {
    // Inicializar DataTable
    $('#mitigacionesTable').DataTable({
        scrollX: true,
        scrollY: '250px',
        scrollCollapse: true,
        lengthMenu: [5, 10, 15, 20, 50],
        autoWidth: false,
        paging: true,
        searching: true,
        info: true,
        pageLength: 5,
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json',
        },
    });

    // Llenar modal de editar con datos de la mitigación
    $('.btn-editar').on('click', function () {
        $('#mitigacion_id').val($(this).data('id'));
        $('#id_accion').val($(this).data('accion'));
        $('#id_fecha_accion').val($(this).data('fecha_accion'));
        $('#id_responsable').val($(this).data('responsable_id'));
        $('#id_riesgo').val($(this).data('riesgo_id'));

        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $('#formEditar input, #formEditar select').removeClass('is-invalid');

        $('#modalEditar').modal('show');
    });

    // Validación del formulario de creación
    $('#formCrear').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresCrear').addClass('d-none').empty();
        $('input, select', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = {};

        // Validar campos obligatorios
        if (!$('[name="accion"]', this).val().trim()) {
            errores.push('El campo Acción es obligatorio.');
            camposInvalidos.accion = $('[name="accion"]', this);
        }
        if (!$('[name="fecha_accion"]', this).val()) {
            errores.push('El campo Fecha Acción es obligatorio.');
            camposInvalidos.fecha_accion = $('[name="fecha_accion"]', this);
        }
        if (!$('[name="responsable"]', this).val()) {
            errores.push('Debe seleccionar un responsable.');
            camposInvalidos.responsable = $('[name="responsable"]', this);
        }
        if (!$('[name="riesgo"]', this).val()) {
            errores.push('Debe seleccionar un riesgo.');
            camposInvalidos.riesgo = $('[name="riesgo"]', this);
        }

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            for (let campo in camposInvalidos) {
                camposInvalidos[campo].addClass('is-invalid');
            }

            $('#erroresCrear')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Validación del formulario de edición
    $('#formEditar').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $('input, select', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = {};

        // Validar campos obligatorios
        if (!$('#id_accion').val().trim()) {
            errores.push('El campo Acción es obligatorio.');
            camposInvalidos.accion = $('#id_accion');
        }
        if (!$('#id_fecha_accion').val()) {
            errores.push('El campo Fecha Acción es obligatorio.');
            camposInvalidos.fecha_accion = $('#id_fecha_accion');
        }
        if (!$('#id_responsable').val()) {
            errores.push('Debe seleccionar un responsable.');
            camposInvalidos.responsable = $('#id_responsable');
        }
        if (!$('#id_riesgo').val()) {
            errores.push('Debe seleccionar un riesgo.');
            camposInvalidos.riesgo = $('#id_riesgo');
        }

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            for (let campo in camposInvalidos) {
                camposInvalidos[campo].addClass('is-invalid');
            }

            $('#erroresEditar')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Quitar el resaltado de error cuando el usuario empiece a escribir
    $(
        '#formCrear input, #formCrear select, #formEditar input, #formEditar select'
    ).on('input change', function () {
        $(this).removeClass('is-invalid');
    });
});
