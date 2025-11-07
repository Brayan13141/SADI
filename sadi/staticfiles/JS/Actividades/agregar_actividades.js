$(document).ready(function () {
    $('#formActividad').on('submit', function (e) {
        // limpiar errores previos
        $('#erroresActividad').addClass('d-none').empty();
        $('input, textarea, select').removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        // Validar campos obligatorios
        if (!$('[name="descripcion"]').val().trim()) {
            errores.push('La descripción es obligatoria.');
            camposInvalidos.push($('[name="descripcion"]'));
        }
        if (!$('[name="fecha_inicio"]').val()) {
            errores.push('La fecha de inicio es obligatoria.');
            camposInvalidos.push($('[name="fecha_inicio"]'));
        }
        if (!$('[name="fecha_fin"]').val()) {
            errores.push('La fecha de fin es obligatoria.');
            camposInvalidos.push($('[name="fecha_fin"]'));
        }
        if (!$('[name="responsable"]').val()) {
            errores.push('Debe seleccionar un responsable.');
            camposInvalidos.push($('[name="responsable"]'));
        }

        // Validar que fecha_fin no sea menor que fecha_inicio
        let inicio = new Date($('[name="fecha_inicio"]').val());
        let fin = new Date($('[name="fecha_fin"]').val());
        if (inicio && fin && fin < inicio) {
            errores.push(
                'La fecha de fin no puede ser anterior a la fecha de inicio.'
            );
            camposInvalidos.push($('[name="fecha_fin"]'));
        }

        // Si hay errores, detener envío y mostrarlos
        if (errores.length > 0) {
            e.preventDefault();
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });
            $('#erroresActividad')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Quitar la clase de error cuando el usuario escribe o cambia
    $('input, textarea, select').on('input change', function () {
        $(this).removeClass('is-invalid');
    });
});
