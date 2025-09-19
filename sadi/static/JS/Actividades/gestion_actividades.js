$(document).ready(function () {
    // Inicializar DataTable
    $('#actividadesTable').DataTable({
        scrollX: true,
        scrollY: '300px',
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
        // Obtener datos del botón
        var actividadId = $(this).data('id');
        var estado = $(this).data('estado');
        var descripcion = $(this).data('descripcion');
        var fechaInicio = $(this).data('fecha_inicio');
        var fechaFin = $(this).data('fecha_fin');
        var evidencia = $(this).data('evidencia'); // string "url|nombre,url|nombre"
        var metaId = $(this).data('meta_id');
        var responsableId = $(this).data('responsable_id');
        var editable = $(this).data('editable'); // true/false

        // Llenar el formulario
        $('#actividad_id').val(actividadId);
        $('#id_estado').val(estado);
        $('#id_descripcion').val(descripcion);
        $('#id_fecha_inicio').val(fechaInicio);
        $('#id_fecha_fin').val(fechaFin);
        $('#id_meta').val(metaId);
        $('#id_responsable').val(responsableId);

        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $(
            '#formEditar input, #formEditar select, #formEditar textarea'
        ).removeClass('is-invalid');

        // Mostrar evidencias en el modal
        var evidenciasHtml = '';
        if (evidencia && evidencia.length > 0) {
            var archivos = evidencia.split(',');
            archivos.forEach(function (item) {
                var partes = item.split('|');
                if (partes.length === 2) {
                    evidenciasHtml += `<li><a href="${partes[0]}" target="_blank">${partes[1]}</a></li>`;
                }
            });
        } else {
            evidenciasHtml =
                '<li><span class="text-muted">Sin evidencias</span></li>';
        }
        $('#listaEvidencias').html(evidenciasHtml);

        // Manejar editable
        if (editable) {
            $('#editarInputs').show();
            $('#noEditableMsg').hide();
            $('#btnGuardarEditar').show();
            $(
                '#formEditar input, #formEditar textarea, #formEditar select'
            ).prop('disabled', false);
        } else {
            $('#editarInputs').hide();
            $('#noEditableMsg').show();
            $('#btnGuardarEditar').hide();
            $(
                '#formEditar input, #formEditar textarea, #formEditar select'
            ).prop('disabled', true);
        }

        // Mostrar modal
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
        if (!$('[name="descripcion"]', this).val().trim()) {
            errores.push('El campo Descripción es obligatorio.');
            camposInvalidos.descripcion = $('[name="descripcion"]', this);
        }
        if (!$('[name="fecha_inicio"]', this).val()) {
            errores.push('El campo Fecha inicio es obligatorio.');
            camposInvalidos.fecha_inicio = $('[name="fecha_inicio"]', this);
        }
        if (!$('[name="fecha_fin"]', this).val()) {
            errores.push('El campo Fecha fin es obligatorio.');
            camposInvalidos.fecha_fin = $('[name="fecha_fin"]', this);
        }
        if (!$('[name="meta"]', this).val()) {
            errores.push('Debe seleccionar una meta.');
            camposInvalidos.meta = $('[name="meta"]', this);
        }
        if (!$('[name="responsable"]', this).val()) {
            errores.push('Debe seleccionar un responsable.');
            camposInvalidos.responsable = $('[name="responsable"]', this);
        }

        // Validar que fecha fin sea posterior a fecha inicio
        if (
            $('[name="fecha_inicio"]', this).val() &&
            $('[name="fecha_fin"]', this).val()
        ) {
            var fechaInicio = new Date($('[name="fecha_inicio"]', this).val());
            var fechaFin = new Date($('[name="fecha_fin"]', this).val());

            if (fechaFin <= fechaInicio) {
                errores.push(
                    'La fecha fin debe ser posterior a la fecha inicio.'
                );
                camposInvalidos.fecha_fin = $('[name="fecha_fin"]', this);
            }
        }

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            for (let campo in camposInvalidos) {
                camposInvalidos[campo].addClass('is-invalid');
            }

            // Mostrar errores generales
            $('#erroresCrear')
                .removeClass('d-none')
                .html(' <ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Validación del formulario de edición
    $('#formEditar').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $('input, select, textarea', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = {};

        if (!$('#id_descripcion').val().trim()) {
            errores.push('El campo Descripción es obligatorio.');
            camposInvalidos.descripcion = $('#id_descripcion');
        }
        if (!$('#id_fecha_inicio').val()) {
            errores.push('El campo Fecha inicio es obligatorio.');
            camposInvalidos.fecha_inicio = $('#id_fecha_inicio');
        }
        if (!$('#id_fecha_fin').val()) {
            errores.push('El campo Fecha fin es obligatorio.');
            camposInvalidos.fecha_fin = $('#id_fecha_fin');
        }
        if (!$('#id_meta').val()) {
            errores.push('Debe seleccionar una meta.');
            camposInvalidos.meta = $('#id_meta');
        }
        if (!$('#id_responsable').val()) {
            errores.push('Debe seleccionar un responsable.');
            camposInvalidos.responsable = $('#id_responsable');
        }

        // Validar que fecha fin sea posterior a fecha inicio
        if ($('#id_fecha_inicio').val() && $('#id_fecha_fin').val()) {
            var fechaInicio = new Date($('#id_fecha_inicio').val());
            var fechaFin = new Date($('#id_fecha_fin').val());

            if (fechaFin <= fechaInicio) {
                errores.push(
                    'La fecha fin debe ser posterior a la fecha inicio.'
                );
                camposInvalidos.fecha_fin = $('#id_fecha_fin');
            }
        }

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            for (let campo in camposInvalidos) {
                camposInvalidos[campo].addClass('is-invalid');
            }

            // Mostrar errores generales
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
