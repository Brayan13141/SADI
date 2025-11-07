// ==========================
// FUNCIONES DE CÁLCULO
// ==========================

// Cálculo en modal de creación
function calcularRiesgo() {
    const probabilidad = parseInt($('[name="probabilidad"]').val()) || 0;
    const impacto = parseInt($('[name="impacto"]').val()) || 0;
    const riesgo = probabilidad * impacto;
    const riesgoElement = $('#riesgo-calculado');

    riesgoElement.text(riesgo);
    riesgoElement.removeClass('text-success text-warning text-danger fw-bold');

    if (riesgo <= 25) riesgoElement.addClass('text-success fw-bold');
    else if (riesgo <= 50) riesgoElement.addClass('text-warning fw-bold');
    else riesgoElement.addClass('text-danger fw-bold');
}

// Cálculo en modal de edición
function calcularRiesgoEditar() {
    const probabilidad = parseInt($('#id_probabilidad').val()) || 0;
    const impacto = parseInt($('#id_impacto').val()) || 0;
    const riesgo = probabilidad * impacto;
    const riesgoElement = $('#riesgo-calculado-editar');

    riesgoElement.text(riesgo);
    riesgoElement.removeClass('text-success text-warning text-danger fw-bold');

    if (riesgo <= 25) riesgoElement.addClass('text-success fw-bold');
    else if (riesgo <= 50) riesgoElement.addClass('text-warning fw-bold');
    else riesgoElement.addClass('text-danger fw-bold');
}

// ==========================
// EVENTOS DOCUMENT READY
// ==========================
$(document).ready(function () {
    // Inicializar DataTable
    $('#riesgosTable').DataTable({
        scrollX: true,
        scrollY: '250px',
        scrollCollapse: true,
        lengthMenu: [5, 10, 15, 20, 50],
        pageLength: 5,
        autoWidth: false,
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json',
        },
    });

    // Llenar modal de edición
    $('.btn-editar').on('click', function () {
        $('#riesgo_id').val($(this).data('id'));
        $('#id_enunciado').val($(this).data('enunciado'));
        $('#id_probabilidad').val($(this).data('probabilidad'));
        $('#id_impacto').val($(this).data('impacto'));
        $('#id_actividad').val($(this).data('actividad_id'));

        calcularRiesgoEditar();

        $('#erroresEditar').addClass('d-none').empty();
        $('#formEditar input, #formEditar select').removeClass('is-invalid');

        $('#modalEditar').modal('show');
    });

    // ==========================
    // VALIDACIÓN FORM CREAR
    // ==========================
    $('#formCrear').on('submit', function (e) {
        $('#erroresCrear').addClass('d-none').empty();
        $('input, select', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = {};

        if (!$('[name="enunciado"]', this).val().trim()) {
            errores.push('El campo Enunciado es obligatorio.');
            camposInvalidos.enunciado = $('[name="enunciado"]', this);
        }

        const probabilidad =
            parseInt($('[name="probabilidad"]', this).val()) || 0;
        const impacto = parseInt($('[name="impacto"]', this).val()) || 0;

        if (probabilidad < 1 || probabilidad > 10) {
            errores.push('La probabilidad debe estar entre 1 y 10.');
            camposInvalidos.probabilidad = $('[name="probabilidad"]', this);
        }

        if (impacto < 1 || impacto > 10) {
            errores.push('El impacto debe estar entre 1 y 10.');
            camposInvalidos.impacto = $('[name="impacto"]', this);
        }

        if (!$('[name="actividad"]', this).val()) {
            errores.push('Debe seleccionar una actividad.');
            camposInvalidos.actividad = $('[name="actividad"]', this);
        }

        if (errores.length > 0) {
            e.preventDefault();
            for (let campo in camposInvalidos)
                camposInvalidos[campo].addClass('is-invalid');
            $('#erroresCrear')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // ==========================
    // VALIDACIÓN FORM EDITAR
    // ==========================
    $('#formEditar').on('submit', function (e) {
        $('#erroresEditar').addClass('d-none').empty();
        $('input, select', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = {};

        if (!$('#id_enunciado').val().trim()) {
            errores.push('El campo Enunciado es obligatorio.');
            camposInvalidos.enunciado = $('#id_enunciado');
        }

        const probabilidad = parseInt($('#id_probabilidad').val()) || 0;
        const impacto = parseInt($('#id_impacto').val()) || 0;

        if (probabilidad < 1 || probabilidad > 10) {
            errores.push('La probabilidad debe estar entre 1 y 10.');
            camposInvalidos.probabilidad = $('#id_probabilidad');
        }

        if (impacto < 1 || impacto > 10) {
            errores.push('El impacto debe estar entre 1 y 10.');
            camposInvalidos.impacto = $('#id_impacto');
        }

        if (!$('#id_actividad').val()) {
            errores.push('Debe seleccionar una actividad.');
            camposInvalidos.actividad = $('#id_actividad');
        }

        if (errores.length > 0) {
            e.preventDefault();
            for (let campo in camposInvalidos)
                camposInvalidos[campo].addClass('is-invalid');
            $('#erroresEditar')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Quitar is-invalid al cambiar o escribir
    $(
        '#formCrear input, #formCrear select, #formEditar input, #formEditar select'
    ).on('input change', function () {
        $(this).removeClass('is-invalid');
    });
});
