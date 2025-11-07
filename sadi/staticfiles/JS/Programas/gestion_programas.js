// gestion_programas.js
$(document).ready(function () {
    $('#programasTable').DataTable({
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

    // Función para calcular la duración en años
    function calcularDuracion(tipo) {
        let fechaInicio, fechaFin, duracionField;

        if (tipo === 'crear') {
            fechaInicio = new Date($('#fecha_inicio_crear').val());
            fechaFin = new Date($('#fecha_fin_crear').val());
            duracionField = $('#duracion_crear');
        } else {
            fechaInicio = new Date($('#id_fecha_inicio_editar').val());
            fechaFin = new Date($('#id_fecha_fin_editar').val());
            duracionField = $('#id_duracion_editar');
        }

        // Validar que ambas fechas estén seleccionadas
        if (
            fechaInicio &&
            fechaFin &&
            !isNaN(fechaInicio) &&
            !isNaN(fechaFin)
        ) {
            if (fechaFin < fechaInicio) {
                // Si la fecha fin es anterior a la fecha inicio
                if (tipo === 'crear') {
                    $('#fecha_fin_crear').val('');
                } else {
                    $('#id_fecha_fin_editar').val('');
                }
                duracionField.val('0');
                return;
            }

            // Calcular diferencia en milisegundos
            const diffTime = Math.abs(fechaFin - fechaInicio);

            // Convertir a días y luego a años (considerando años bisiestos)
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            const diffYears = (diffDays / 365.25).toFixed(1);

            // Actualizar el campo de duración
            duracionField.val(diffYears);
        } else {
            // Si falta alguna fecha
            duracionField.val('0');
        }
    }

    // Eventos para calcular la duración al cambiar las fechas
    $('#fecha_inicio_crear, #fecha_fin_crear').on('change', function () {
        calcularDuracion('crear');
    });

    $('#id_fecha_inicio_editar, #id_fecha_fin_editar').on(
        'change',
        function () {
            calcularDuracion('editar');
        }
    );

    // Llenar modal de editar con datos del programa
    $('.btn-editar').on('click', function () {
        var id = $(this).data('id');
        var clave = $(this).data('clave');
        var nombre = $(this).data('nombre');
        var nombre_corto = $(this).data('nombre_corto');
        var estado = $(this).data('estado');
        var fecha_inicio = $(this).data('fecha_inicio');
        var fecha_fin = $(this).data('fecha_fin');
        var duracion = $(this).data('duracion');

        $('#programa_id').val(id);
        $('#id_clave_editar').val(clave);
        $('#id_nombre_editar').val(nombre);
        $('#id_nombre_corto_editar').val(nombre_corto);
        $('#id_estado_editar').val(estado.toString());
        $('#id_fecha_inicio_editar').val(fecha_inicio);
        $('#id_fecha_fin_editar').val(fecha_fin);
        $('#id_duracion_editar').val(duracion);

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
        let camposInvalidos = [];

        // Validar campos obligatorios
        if (!$('[name="clave"]', this).val().trim()) {
            errores.push('El campo Clave es obligatorio.');
            camposInvalidos.push($('[name="clave"]', this));
        }
        if (!$('[name="nombre"]', this).val().trim()) {
            errores.push('El campo Nombre es obligatorio.');
            camposInvalidos.push($('[name="nombre"]', this));
        }
        if (!$('[name="nombre_corto"]', this).val().trim()) {
            errores.push('El campo Nombre Corto es obligatorio.');
            camposInvalidos.push($('[name="nombre_corto"]', this));
        }
        if (!$('[name="fecha_inicio"]', this).val()) {
            errores.push('El campo Fecha Inicio es obligatorio.');
            camposInvalidos.push($('[name="fecha_inicio"]', this));
        }
        if (!$('[name="fecha_fin"]', this).val()) {
            errores.push('El campo Fecha Fin es obligatorio.');
            camposInvalidos.push($('[name="fecha_fin"]', this));
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
                camposInvalidos.push($('[name="fecha_fin"]', this));
            }
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
        }
    });

    // Validación del formulario de edición
    $('#formEditar').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $('input, select', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        // Validar campos obligatorios
        if (!$('#id_clave_editar').val().trim()) {
            errores.push('El campo Clave es obligatorio.');
            camposInvalidos.push($('#id_clave_editar'));
        }
        if (!$('#id_nombre_editar').val().trim()) {
            errores.push('El campo Nombre es obligatorio.');
            camposInvalidos.push($('#id_nombre_editar'));
        }
        if (!$('#id_nombre_corto_editar').val().trim()) {
            errores.push('El campo Nombre Corto es obligatorio.');
            camposInvalidos.push($('#id_nombre_corto_editar'));
        }
        if (!$('#id_fecha_inicio_editar').val()) {
            errores.push('El campo Fecha Inicio es obligatorio.');
            camposInvalidos.push($('#id_fecha_inicio_editar'));
        }
        if (!$('#id_fecha_fin_editar').val()) {
            errores.push('El campo Fecha Fin es obligatorio.');
            camposInvalidos.push($('#id_fecha_fin_editar'));
        }

        // Validar que fecha fin sea posterior a fecha inicio
        if (
            $('#id_fecha_inicio_editar').val() &&
            $('#id_fecha_fin_editar').val()
        ) {
            var fechaInicio = new Date($('#id_fecha_inicio_editar').val());
            var fechaFin = new Date($('#id_fecha_fin_editar').val());

            if (fechaFin <= fechaInicio) {
                errores.push(
                    'La fecha fin debe ser posterior a la fecha inicio.'
                );
                camposInvalidos.push($('#id_fecha_fin_editar'));
            }
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
        }
    });
});
