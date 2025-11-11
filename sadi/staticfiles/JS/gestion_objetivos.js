$(document).ready(function () {
    // Inicializar DataTable
    $('#objetivosTable').DataTable({
        scrollX: true,
        autoWidth: false,
        paging: true,
        searching: true,
        info: true,
        pageLength: 5,
        lengthMenu: [5, 10, 20],
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json',
        },
    });

    // Llenar modal de editar con datos del objetivo
    $('.btn-editar').on('click', function () {
        $('#objetivo_id').val($(this).data('id'));
        $('#id_descripcion').val($(this).data('descripcion'));
        $('#id_programa').val($(this).data('programa_id'));

        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $(
            '#formEditar input, #formEditar select, #formEditar textarea'
        ).removeClass('is-invalid');

        $('#modalEditar').modal('show');
    });

    // Validación del formulario de creación
    $('#formCrear').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresCrear').addClass('d-none').empty();
        $('input, select, textarea', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = {};

        // Validar campos obligatorios
        if (!$('[name="programa"]', this).val()) {
            errores.push('Debe seleccionar un programa.');
            camposInvalidos.programa = $('[name="programa"]', this);
        }
        if (!$('[name="descripcion"]', this).val().trim()) {
            errores.push('El campo Descripción es obligatorio.');
            camposInvalidos.descripcion = $('[name="descripcion"]', this);
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
        $('input, select, textarea', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = {};

        // Validar campos obligatorios
        if (!$('#id_programa').val()) {
            errores.push('Debe seleccionar un programa.');
            camposInvalidos.programa = $('#id_programa');
        }
        if (!$('#id_descripcion').val().trim()) {
            errores.push('El campo Descripción es obligatorio.');
            camposInvalidos.descripcion = $('#id_descripcion');
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
        '#formCrear input, #formCrear select, #formCrear textarea, #formEditar input, #formEditar select, #formEditar textarea'
    ).on('input change', function () {
        $(this).removeClass('is-invalid');
    });
});
