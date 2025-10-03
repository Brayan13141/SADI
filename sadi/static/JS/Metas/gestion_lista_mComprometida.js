$(document).ready(function () {
    // DataTable
    $('#comprometidasTable').DataTable({
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

    // --- ABRIR MODAL DE EDICIÓN ---
    $('.btn-editar-comprometida').on('click', function () {
        const id = $(this).data('id');
        const programa = $(this).data('programa');
        const valor = $(this).data('valor');
        const meta = $(this).data('meta');
        const metaNombre = $(this).data('meta-nombre');

        $('#comprometida_id_editar').val(id);
        $('#id_programa_editar').val(programa);
        $('#id_valor_editar').val(valor);
        $('#id_meta_editar').val(meta);
        $('#meta_nombre_editar').val(metaNombre);

        // Limpiar clases de error al abrir el modal
        $(
            '#formEditarComprometida input, #formEditarComprometida select'
        ).removeClass('is-invalid');
        $('#erroresEditarComprometida').addClass('d-none').empty();

        $('#modalEditarComprometida').modal('show');
    });

    // --- VALIDACIÓN DE FORMULARIOS ---
    // Validación Crear
    $('#formCrearComprometida').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresCrearComprometida').addClass('d-none').empty();
        $('input, select', this).removeClass('is-invalid');

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

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });

            $('#erroresCrearComprometida')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        } else {
            $('#erroresCrearComprometida').addClass('d-none').empty();
        }
    });

    // Validación Editar
    $('#formEditarComprometida').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresEditarComprometida').addClass('d-none').empty();
        $('input, select', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        // Validar valor
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

            // Aplicar clase is-invalid a los campos con error
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });

            $('#erroresEditarComprometida')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        } else {
            $('#erroresEditarComprometida').addClass('d-none').empty();
        }
    });

    // Quitar el resaltado de error cuando el usuario empiece a escribir
    $('input, select').on('input change', function () {
        $(this).removeClass('is-invalid');
    });

    // Limpiar validaciones al cerrar modales
    $('#modalCrearComprometida').on('hidden.bs.modal', function () {
        $('#formCrearComprometida')[0].reset();
        $('input, select', '#formCrearComprometida').removeClass('is-invalid');
        $('#erroresCrearComprometida').addClass('d-none').empty();
    });

    $('#modalEditarComprometida').on('hidden.bs.modal', function () {
        $('input, select', '#formEditarComprometida').removeClass('is-invalid');
        $('#erroresEditarComprometida').addClass('d-none').empty();
    });
});
