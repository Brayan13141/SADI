$(document).ready(function () {
    // Inicializar DataTable
    $('#proyectosTable').DataTable({
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

    // Manejar clic en botón Editar
    $('.btn-editar').on('click', function () {
        var proyectoId = $(this).data('id');
        var nombre = $(this).data('nombre');
        var objetivoId = $(this).data('objetivo_id');

        $('#proyecto_id').val(proyectoId);
        $('#id_nombre').val(nombre);
        $('#id_objetivo').val(objetivoId);

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
        if (!$('[name="objetivo"]', this).val()) {
            errores.push('Debe seleccionar un objetivo.');
            camposInvalidos.objetivo = $('[name="objetivo"]', this);
        }
        if (!$('[name="nombre"]', this).val().trim()) {
            errores.push('El campo Nombre es obligatorio.');
            camposInvalidos.nombre = $('[name="nombre"]', this);
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
        if (!$('#id_objetivo').val()) {
            errores.push('Debe seleccionar un objetivo.');
            camposInvalidos.objetivo = $('#id_objetivo');
        }
        if (!$('#id_nombre').val().trim()) {
            errores.push('El campo Nombre es obligatorio.');
            camposInvalidos.nombre = $('#id_nombre');
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
