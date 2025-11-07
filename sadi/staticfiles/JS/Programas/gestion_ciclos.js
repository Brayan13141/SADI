// gestion_ciclos.js
$(document).ready(function () {
    // Inicializar DataTable
    $('#ciclosTable').DataTable({
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

    // ========================
    // Función para calcular duración
    // ========================
    function calcularDuracion(tipo) {
        let fechaInicio, fechaFin, duracionField;

        if (tipo === 'crear') {
            fechaInicio = new Date($('#id_fecha_inicio_crear').val());
            fechaFin = new Date($('#id_fecha_fin_crear').val());
            duracionField = $('#id_duracion_crear');
        } else {
            fechaInicio = new Date($('#id_fecha_inicio').val());
            fechaFin = new Date($('#id_fecha_fin').val());
            duracionField = $('#id_duracion');
        }

        if (
            fechaInicio &&
            fechaFin &&
            !isNaN(fechaInicio) &&
            !isNaN(fechaFin)
        ) {
            if (fechaFin < fechaInicio) {
                (tipo === 'crear'
                    ? $('#id_fecha_fin_crear')
                    : $('#id_fecha_fin')
                ).val('');
                duracionField.val('0');
                return;
            }

            const diffTime = Math.abs(fechaFin - fechaInicio);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            const diffYears = (diffDays / 365.25).toFixed(1);

            duracionField.val(diffYears);
        } else {
            duracionField.val('0');
        }
    }

    $('#id_fecha_inicio_crear, #id_fecha_fin_crear').on('change', () =>
        calcularDuracion('crear')
    );
    $('#id_fecha_inicio, #id_fecha_fin').on('change', () =>
        calcularDuracion('editar')
    );

    // ========================
    // Abrir modal Editar con datos
    // ========================
    $('.btn-editar').on('click', function () {
        $('#ciclo_id').val($(this).data('id'));
        $('#id_activo').val($(this).data('activo'));
        $('#id_fecha_inicio').val($(this).data('fecha_inicio'));
        $('#id_fecha_fin').val($(this).data('fecha_fin'));
        $('#id_duracion').val($(this).data('duracion'));
        $('#id_programa').val($(this).data('programa_id'));

        $('#erroresEditar').addClass('d-none').empty();
        $('#formEditar input, #formEditar select')
            .removeClass('is-invalid')
            .siblings('.field-error')
            .remove();

        $('#modalEditar').modal('show');
    });

    // ========================
    // Función de validación genérica
    // ========================
    function validarFormulario(formId, erroresDivId) {
        let errores = [];
        let camposInvalidos = [];

        // Limpiar errores previos
        $(erroresDivId).addClass('d-none').empty();
        $(`${formId} input, ${formId} select`)
            .removeClass('is-invalid')
            .siblings('.field-error')
            .remove();

        // Validaciones comunes
        const programa = $(`${formId} select[name="programa"]`);
        const fechaInicio = $(`${formId} input[name="fecha_inicio"]`);
        const fechaFin = $(`${formId} input[name="fecha_fin"]`);

        if (!programa.val()) {
            errores.push('El campo Programa es obligatorio.');
            camposInvalidos.push(programa);
        }
        if (!fechaInicio.val()) {
            errores.push('El campo Fecha Inicio es obligatorio.');
            camposInvalidos.push(fechaInicio);
        }
        if (!fechaFin.val()) {
            errores.push('El campo Fecha Fin es obligatorio.');
            camposInvalidos.push(fechaFin);
        }

        // Validar fechas
        if (fechaInicio.val() && fechaFin.val()) {
            let fi = new Date(fechaInicio.val());
            let ff = new Date(fechaFin.val());
            if (ff <= fi) {
                errores.push(
                    'La fecha fin debe ser posterior a la fecha inicio.'
                );
                camposInvalidos.push(fechaFin);
            }
        }

        // Mostrar errores
        if (errores.length > 0) {
            // Mostrar listado en el alert superior
            $(erroresDivId)
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');

            // Agregar mensajes debajo de los campos
            camposInvalidos.forEach((campo) => {
                campo.addClass('is-invalid');
                campo.after('<div class="field-error">Campo inválido</div>');
            });

            return false;
        }
        return true;
    }

    // ========================
    // Validación al enviar
    // ========================
    $('#formCrear').on('submit', function (e) {
        if (!validarFormulario('#formCrear', '#erroresCrear')) {
            e.preventDefault();
        }
    });

    $('#formEditar').on('submit', function (e) {
        if (!validarFormulario('#formEditar', '#erroresEditar')) {
            e.preventDefault();
        }
    });

    // ========================
    // Reset modal al cerrar
    // ========================
    $('.modal').on('hidden.bs.modal', function () {
        $(this).find('form')[0].reset();
        $(this).find('.is-invalid').removeClass('is-invalid');
        $(this).find('.field-error').remove();
        $(this).find('.alert-danger').addClass('d-none').empty();
    });
});
