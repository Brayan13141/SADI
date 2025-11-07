$(document).ready(function () {
    // --- ABRIR MODAL DE EDICIÓN ---
    $('.btn-editar-comprometida').on('click', function () {
        const id = $(this).data('id');
        const valor = $(this).data('valor');
        const meta = $(this).data('meta');
        const metaNombre = $(this).data('meta-nombre');

        // Llenar campos del formulario de edición
        $('#comprometida_id_editar').val(id);
        $('#id_meta_editar').val(meta);
        $('#meta_nombre_editar').val(metaNombre);
        $('#id_valor_editar').val(valor);

        // Limpiar errores anteriores
        $('#formEditarComprometida input').removeClass('is-invalid');
        $('#erroresEditarComprometida').addClass('d-none').empty();

        // Mostrar modal
        $('#modalEditarComprometida').modal('show');
    });

    // --- VALIDACIÓN DE FORMULARIO CREAR ---
    $('#formCrearComprometida').on('submit', function (e) {
        $('#erroresCrearComprometida').addClass('d-none').empty();
        $(
            '#formCrearComprometida input, #formCrearComprometida select'
        ).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        // Validar meta
        if (!$('#id_meta').val()) {
            errores.push('Debe seleccionar una meta.');
            camposInvalidos.push($('#id_meta'));
        }

        // Validar valor
        const valorVal = parseFloat($('#id_valor').val());
        if (isNaN(valorVal)) {
            errores.push('El valor debe ser un número válido.');
            camposInvalidos.push($('#id_valor'));
        } else if (valorVal <= 0) {
            errores.push('El valor debe ser mayor a 0.');
            camposInvalidos.push($('#id_valor'));
        }

        // Mostrar errores si hay
        if (errores.length > 0) {
            e.preventDefault();
            camposInvalidos.forEach((campo) => campo.addClass('is-invalid'));
            $('#erroresCrearComprometida')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // --- VALIDACIÓN DE FORMULARIO EDITAR ---
    $('#formEditarComprometida').on('submit', function (e) {
        $('#erroresEditarComprometida').addClass('d-none').empty();
        $('#formEditarComprometida input').removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        const valorVal = parseFloat($('#id_valor_editar').val());
        if (isNaN(valorVal)) {
            errores.push('El valor debe ser un número válido.');
            camposInvalidos.push($('#id_valor_editar'));
        } else if (valorVal <= 0) {
            errores.push('El valor debe ser mayor a 0.');
            camposInvalidos.push($('#id_valor_editar'));
        }

        if (errores.length > 0) {
            e.preventDefault();
            camposInvalidos.forEach((campo) => campo.addClass('is-invalid'));
            $('#erroresEditarComprometida')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // --- LIMPIAR FORMULARIOS AL CERRAR MODALES ---
    $('#modalCrearComprometida').on('hidden.bs.modal', function () {
        $('#formCrearComprometida')[0].reset();
        $(
            '#formCrearComprometida input, #formCrearComprometida select'
        ).removeClass('is-invalid');
        $('#erroresCrearComprometida').addClass('d-none').empty();
    });

    $('#modalEditarComprometida').on('hidden.bs.modal', function () {
        $('#formEditarComprometida input').removeClass('is-invalid');
        $('#erroresEditarComprometida').addClass('d-none').empty();
    });

    // --- DESHABILITAR ACCIONES PARA DOCENTE ---
    const userRole = '{{ request.user.role|default:"" }}';
    if (userRole === 'DOCENTE' || userRole === 'INVITADO') {
        $('.btn-editar-comprometida').prop('disabled', true);
        $('#formCrearComprometida button[type="submit"]').prop(
            'disabled',
            true
        );
        $(
            '#modalCrearComprometida button, #modalEditarComprometida button'
        ).prop('disabled', true);
    }
});
