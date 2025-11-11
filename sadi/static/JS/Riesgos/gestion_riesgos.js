// ==========================
// FUNCIONES DE CÁLCULO
// ==========================
function calcularRiesgo() {
    const probabilidad = parseInt($('#id_probabilidad').val()) || 0;
    const impacto = parseInt($('#id_impacto').val()) || 0;
    const riesgo = probabilidad * impacto;
    const riesgoElement = $('#riesgo-calculado');

    riesgoElement.text(riesgo);
    riesgoElement.removeClass('text-success text-warning text-danger fw-bold');

    if (riesgo <= 25) {
        riesgoElement.addClass('text-success fw-bold');
    } else if (riesgo <= 50) {
        riesgoElement.addClass('text-warning fw-bold');
    } else {
        riesgoElement.addClass('text-danger fw-bold');
    }
}

function calcularRiesgoEditar() {
    const probabilidad = parseInt($('#eid_probabilidad_editar').val()) || 0;
    const impacto = parseInt($('#eid_impacto_editar').val()) || 0;
    const riesgo = probabilidad * impacto;
    const riesgoElement = $('#riesgo-calculado-editar');

    riesgoElement.text(riesgo);
    riesgoElement.removeClass('text-success text-warning text-danger fw-bold');

    if (riesgo <= 25) {
        riesgoElement.addClass('text-success fw-bold');
    } else if (riesgo <= 50) {
        riesgoElement.addClass('text-warning fw-bold');
    } else {
        riesgoElement.addClass('text-danger fw-bold');
    }
}

// ==========================
// EVENTOS DOCUMENT READY
// ==========================
$(document).ready(function () {
    var table = $('#riesgosTable').DataTable({
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

    // Cálculo en tiempo real
    $('#id_probabilidad, #id_impacto').on('input change', function () {
        calcularRiesgo();
    });
    $(document).on(
        'input change',
        '#eid_probabilidad_editar, #eid_impacto_editar',
        function () {
            calcularRiesgoEditar();
        }
    );

    // Bloquear valores decimales
    $('body').on(
        'input',
        '#id_probabilidad, #id_impacto, #eid_probabilidad_editar, #eid_impacto_editar',
        function () {
            const valor = $(this).val();
            if (valor.includes('.') || valor.includes(',')) {
                $(this).val(parseInt(valor) || '');
            }
        }
    );
    $('body').on(
        'keypress',
        '#id_probabilidad, #id_impacto, #eid_probabilidad_editar, #eid_impacto_editar',
        function (e) {
            if (e.key === '.' || e.key === ',') {
                e.preventDefault();
            }
        }
    );
    $('body').on(
        'paste',
        '#id_probabilidad, #id_impacto, #eid_probabilidad_editar, #eid_impacto_editar',
        function (e) {
            const textoPegado = e.originalEvent.clipboardData.getData('text');
            if (textoPegado.includes('.') || textoPegado.includes(',')) {
                e.preventDefault();
            }
        }
    );

    // Llenar modal de edición
    $(document).on('click', '.btn-editar', function () {
        $('#riesgo_id').val($(this).data('id'));
        $('#eid_enunciado').val($(this).data('enunciado'));
        $('#eid_probabilidad_editar').val($(this).data('probabilidad'));
        $('#eid_impacto_editar').val($(this).data('impacto'));
        $('#eid_actividad').val($(this).data('actividad'));
        calcularRiesgoEditar();
        $('#erroresEditar').addClass('d-none').empty();
        $('#formEditar input, #formEditar select').removeClass('is-invalid');
        $('#modalEditar').modal('show');
    });

    // Validar formulario crear
    $('#formCrear').on('submit', function (e) {
        $('#erroresCrear').addClass('d-none').empty();
        $('#formCrear input, #formCrear select').removeClass('is-invalid');
        let errores = [];
        let camposInvalidos = {};

        if (!$('#id_enunciado').val().trim()) {
            errores.push('El campo Enunciado es obligatorio.');
            camposInvalidos.enunciado = $('#id_enunciado');
        }

        const probabilidad = parseInt($('#id_probabilidad').val()) || 0;
        if (probabilidad < 1 || probabilidad > 10) {
            errores.push('La probabilidad debe estar entre 1 y 10.');
            camposInvalidos.probabilidad = $('#id_probabilidad');
        }

        const impacto = parseInt($('#id_impacto').val()) || 0;
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
            for (let campo in camposInvalidos) {
                camposInvalidos[campo].addClass('is-invalid');
            }
            $('#erroresCrear')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Validar formulario editar
    $('#formEditar').on('submit', function (e) {
        $('#erroresEditar').addClass('d-none').empty();
        $('#formEditar input, #formEditar select').removeClass('is-invalid');
        let errores = [];
        let camposInvalidos = {};

        if (!$('#eid_enunciado').val().trim()) {
            errores.push('El campo Enunciado es obligatorio.');
            camposInvalidos.enunciado = $('#eid_enunciado');
        }

        const probabilidad = parseInt($('#eid_probabilidad_editar').val()) || 0;
        if (probabilidad < 1 || probabilidad > 10) {
            errores.push('La probabilidad debe estar entre 1 y 10.');
            camposInvalidos.probabilidad = $('#eid_probabilidad_editar');
        }

        const impacto = parseInt($('#eid_impacto_editar').val()) || 0;
        if (impacto < 1 || impacto > 10) {
            errores.push('El impacto debe estar entre 1 y 10.');
            camposInvalidos.impacto = $('#eid_impacto_editar');
        }

        if (!$('#eid_actividad').val()) {
            errores.push('Debe seleccionar una actividad.');
            camposInvalidos.actividad = $('#eid_actividad');
        }

        if (errores.length > 0) {
            e.preventDefault();
            for (let campo in camposInvalidos) {
                camposInvalidos[campo].addClass('is-invalid');
            }
            $('#erroresEditar')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Quitar is-invalid al cambiar o escribir
    $('body').on(
        'input change',
        '#formCrear input, #formCrear select, #formEditar input, #formEditar select',
        function () {
            $(this).removeClass('is-invalid');
        }
    );

    calcularRiesgo();
});
