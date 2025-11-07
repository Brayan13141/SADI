// Función para calcular el riesgo en el modal de creación
function calcularRiesgo() {
    const probabilidad = parseInt($('[name="probabilidad"]').val()) || 0;
    const impacto = parseInt($('[name="impacto"]').val()) || 0;
    const riesgo = probabilidad * impacto;
    $('#riesgo-calculado').text(riesgo);

    // Aplicar clase según el nivel de riesgo
    const riesgoElement = $('#riesgo-calculado');
    riesgoElement.removeClass('text-success text-warning text-danger');

    if (riesgo <= 25) {
        riesgoElement.addClass('text-success');
    } else if (riesgo <= 50) {
        riesgoElement.addClass('text-warning');
    } else {
        riesgoElement.addClass('text-danger');
    }
}

// Función para calcular el riesgo en el modal de edición
function calcularRiesgoEditar() {
    const probabilidad = parseInt($('#id_probabilidad').val()) || 0;
    const impacto = parseInt($('#id_impacto').val()) || 0;
    const riesgo = probabilidad * impacto;
    $('#riesgo-calculado-editar').text(riesgo);

    // Aplicar clase según el nivel de riesgo
    const riesgoElement = $('#riesgo-calculado-editar');
    riesgoElement.removeClass('text-success text-warning text-danger');

    if (riesgo <= 25) {
        riesgoElement.addClass('text-success');
    } else if (riesgo <= 50) {
        riesgoElement.addClass('text-warning');
    } else {
        riesgoElement.addClass('text-danger');
    }
}

$(document).ready(function () {
    // Inicializar DataTable
    $('#riesgosTable').DataTable({
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

    // Llenar modal de editar con datos del riesgo
    $('.btn-editar').on('click', function () {
        $('#riesgo_id').val($(this).data('id'));
        $('#id_enunciado').val($(this).data('enunciado'));
        $('#id_probabilidad').val($(this).data('probabilidad'));
        $('#id_impacto').val($(this).data('impacto'));
        $('#id_meta').val($(this).data('meta_id'));

        // Calcular riesgo inicial
        calcularRiesgoEditar();

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
        if (!$('[name="enunciado"]', this).val().trim()) {
            errores.push('El campo Enunciado es obligatorio.');
            camposInvalidos.enunciado = $('[name="enunciado"]', this);
        }
        if (!$('[name="probabilidad"]', this).val()) {
            errores.push('El campo Probabilidad es obligatorio.');
            camposInvalidos.probabilidad = $('[name="probabilidad"]', this);
        } else {
            const probabilidad = parseInt(
                $('[name="probabilidad"]', this).val()
            );
            if (probabilidad < 1 || probabilidad > 10) {
                errores.push('La probabilidad debe estar entre 1 y 10.');
                camposInvalidos.probabilidad = $('[name="probabilidad"]', this);
            }
        }
        if (!$('[name="impacto"]', this).val()) {
            errores.push('El campo Impacto es obligatorio.');
            camposInvalidos.impacto = $('[name="impacto"]', this);
        } else {
            const impacto = parseInt($('[name="impacto"]', this).val());
            if (impacto < 1 || impacto > 10) {
                errores.push('El impacto debe estar entre 1 y 10.');
                camposInvalidos.impacto = $('[name="impacto"]', this);
            }
        }
        if (!$('[name="meta"]', this).val()) {
            errores.push('Debe seleccionar una meta.');
            camposInvalidos.meta = $('[name="meta"]', this);
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
        if (!$('#id_enunciado').val().trim()) {
            errores.push('El campo Enunciado es obligatorio.');
            camposInvalidos.enunciado = $('#id_enunciado');
        }
        if (!$('#id_probabilidad').val()) {
            errores.push('El campo Probabilidad es obligatorio.');
            camposInvalidos.probabilidad = $('#id_probabilidad');
        } else {
            const probabilidad = parseInt($('#id_probabilidad').val());
            if (probabilidad < 1 || probabilidad > 10) {
                errores.push('La probabilidad debe estar entre 1 y 10.');
                camposInvalidos.probabilidad = $('#id_probabilidad');
            }
        }
        if (!$('#id_impacto').val()) {
            errores.push('El campo Impacto es obligatorio.');
            camposInvalidos.impacto = $('#id_impacto');
        } else {
            const impacto = parseInt($('#id_impacto').val());
            if (impacto < 1 || impacto > 10) {
                errores.push('El impacto debe estar entre 1 y 10.');
                camposInvalidos.impacto = $('#id_impacto');
            }
        }
        if (!$('#id_meta').val()) {
            errores.push('Debe seleccionar una meta.');
            camposInvalidos.meta = $('#id_meta');
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
