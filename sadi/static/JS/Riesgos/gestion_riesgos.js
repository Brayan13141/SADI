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
    const probabilidad = parseInt($('#eid_probabilidad').val()) || 0;
    const impacto = parseInt($('#eid_impacto').val()) || 0;
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

    // Cálculo en tiempo real para modal crear
    $('#id_probabilidad, #id_impacto').on('input change', function () {
        calcularRiesgo();
    });

    // Cálculo en tiempo real para modal editar
    $(document).on(
        'input change',
        '#eid_probabilidad, #eid_impacto',
        function () {
            calcularRiesgoEditar();
        }
    );

    // Bloquear valores decimales
    $('body').on(
        'input',
        '#id_probabilidad, #id_impacto, #eid_probabilidad, #eid_impacto',
        function () {
            const valor = $(this).val();
            if (valor.includes('.') || valor.includes(',')) {
                $(this).val(parseInt(valor) || '');
            }
        }
    );

    $('body').on(
        'keypress',
        '#id_probabilidad, #id_impacto, #eid_probabilidad, #eid_impacto',
        function (e) {
            if (e.key === '.' || e.key === ',') {
                e.preventDefault();
            }
        }
    );

    $('body').on(
        'paste',
        '#id_probabilidad, #id_impacto, #eid_probabilidad, #eid_impacto',
        function (e) {
            const textoPegado = e.originalEvent.clipboardData.getData('text');
            if (textoPegado.includes('.') || textoPegado.includes(',')) {
                e.preventDefault();
            }
        }
    );
    // Debugging adicional
    $(document).on('click', '.btn-editar', function () {
        console.log('Botón editar clickeado');
        console.log('Datos:', {
            id: $(this).data('id'),
            probabilidad: $(this).data('probabilidad'),
            impacto: $(this).data('impacto'),
        });
    });
    // Llenar modal de edición - CORREGIDO
    $(document).on('click', '.btn-editar', function () {
        const $btn = $(this);
        const id = $btn.data('id');
        const enunciado = $btn.data('enunciado');
        const probabilidad = $btn.data('probabilidad');
        const impacto = $btn.data('impacto');
        const actividad = $btn.data('actividad');

        console.log('Datos del riesgo:', {
            id,
            enunciado,
            probabilidad,
            impacto,
            actividad,
        });

        // Llenar los campos del formulario
        $('#riesgo_id').val(id);
        $('#eid_enunciado').val(enunciado);
        $('#eid_probabilidad').val(probabilidad);
        $('#eid_impacto').val(impacto);
        $('#eid_actividad').val(actividad);

        // Calcular y mostrar el nivel de riesgo
        calcularRiesgoEditar();

        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $('#formEditar input, #formEditar select').removeClass('is-invalid');

        // Mostrar el modal
        $('#modalEditar').modal('show');
    });

    // Validar formulario crear
    $('#formCrear').on('submit', function (e) {
        $('#erroresCrear').addClass('d-none').empty();
        $('#formCrear input, #formCrear select').removeClass('is-invalid');
        let errores = [];
        let camposInvalidos = {};

        // Validar enunciado
        if (!$('#id_enunciado').val().trim()) {
            errores.push('El campo Enunciado es obligatorio.');
            camposInvalidos.enunciado = $('#id_enunciado');
        }

        // Validar probabilidad
        const probabilidad = parseInt($('#id_probabilidad').val());
        if (isNaN(probabilidad) || probabilidad < 1 || probabilidad > 10) {
            errores.push('La probabilidad debe ser un número entre 1 y 10.');
            camposInvalidos.probabilidad = $('#id_probabilidad');
        }

        // Validar impacto
        const impacto = parseInt($('#id_impacto').val());
        if (isNaN(impacto) || impacto < 1 || impacto > 10) {
            errores.push('El impacto debe ser un número entre 1 y 10.');
            camposInvalidos.impacto = $('#id_impacto');
        }

        // Validar actividad
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

    // Validar formulario editar - CORREGIDO
    $('#formEditar').on('submit', function (e) {
        $('#erroresEditar').addClass('d-none').empty();
        $('#formEditar input, #formEditar select').removeClass('is-invalid');
        let errores = [];
        let camposInvalidos = {};

        // Validar enunciado
        if (!$('#eid_enunciado').val().trim()) {
            errores.push('El campo Enunciado es obligatorio.');
            camposInvalidos.enunciado = $('#eid_enunciado');
        }

        // Validar probabilidad
        const probabilidad = parseInt($('#eid_probabilidad').val());
        if (isNaN(probabilidad) || probabilidad < 1 || probabilidad > 10) {
            errores.push('La probabilidad debe ser un número entre 1 y 10.');
            camposInvalidos.probabilidad = $('#eid_probabilidad');
        }

        // Validar impacto
        const impacto = parseInt($('#eid_impacto').val());
        if (isNaN(impacto) || impacto < 1 || impacto > 10) {
            errores.push('El impacto debe ser un número entre 1 y 10.');
            camposInvalidos.impacto = $('#eid_impacto');
        }

        // Validar actividad
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

    // Inicializar cálculo
    calcularRiesgo();
});
