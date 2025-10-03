$(document).ready(function () {
    // DataTable
    $('#usuariosTable').DataTable({
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

    // Botón Editar -> cargar datos al modal
    $('.btn-editar').on('click', function () {
        $('#usuario_id').val($(this).data('id'));
        $('#id_username').val($(this).data('username'));
        $('#id_first_name').val($(this).data('first_name'));
        $('#id_last_name').val($(this).data('last_name'));
        $('#id_email').val($(this).data('email'));

        if ($('#is_active').val() === 'true') {
            $('#is_active').prop('checked', true);
        } else {
            $('#is_active').prop('checked', false);
        }
        $('#id_role').val($(this).data('role'));
        $('#id_departamento').val($(this).data('departamento'));
        $('#erroresEditar').addClass('d-none').empty();

        // Limpiar clases de error al abrir el modal
        $('#formEditar input, #formEditar select').removeClass('is-invalid');

        $('#modalEditar').modal('show');
    });

    // Validación Crear
    $('#formCrear').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresCrear').addClass('d-none').empty();
        $('input, select', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        if (!$('[name="username"]', this).val().trim()) {
            errores.push('El campo Usuario es obligatorio.');
            camposInvalidos.push($('[name="username"]', this));
        }
        if (!$('[name="first_name"]', this).val().trim()) {
            errores.push('El campo Nombre es obligatorio.');
            camposInvalidos.push($('[name="first_name"]', this));
        }
        if (!$('[name="last_name"]', this).val().trim()) {
            errores.push('El campo Apellido es obligatorio.');
            camposInvalidos.push($('[name="last_name"]', this));
        }
        if (!$('[name="email"]', this).val().trim()) {
            errores.push('El campo Correo es obligatorio.');
            camposInvalidos.push($('[name="email"]', this));
        }
        if (!$('[name="password"]', this).val().trim()) {
            errores.push('El campo Contraseña es obligatorio.');
            camposInvalidos.push($('[name="password"]', this));
        }
        if (!$('[name="role"]', this).val()) {
            errores.push('Debe seleccionar un rol.');
            camposInvalidos.push($('[name="role"]', this));
        }

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });

            $('#erroresCrear')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        } else {
            $('#erroresCrear').addClass('d-none').empty();
        }
    });

    // Validación Editar
    $('#formEditar').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $('input, select', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        if (!$('#id_username').val().trim()) {
            errores.push('El campo Usuario es obligatorio.');
            camposInvalidos.push($('#id_username'));
        }
        if (!$('#id_first_name').val().trim()) {
            errores.push('El campo Nombre es obligatorio.');
            camposInvalidos.push($('#id_first_name'));
        }
        if (!$('#id_last_name').val().trim()) {
            errores.push('El campo Apellido es obligatorio.');
            camposInvalidos.push($('#id_last_name'));
        }
        if (!$('#id_email').val().trim()) {
            errores.push('El campo Correo es obligatorio.');
            camposInvalidos.push($('#id_email'));
        }

        if (!$('#id_role').val()) {
            errores.push('Debe seleccionar un rol.');
            camposInvalidos.push($('#id_role'));
        }

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });

            $('#erroresEditar')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        } else {
            $('#erroresEditar').addClass('d-none').empty();
        }
    });

    // Quitar el resaltado de error cuando el usuario empiece a escribir
    $('input, select').on('input change', function () {
        $(this).removeClass('is-invalid');
    });
});
