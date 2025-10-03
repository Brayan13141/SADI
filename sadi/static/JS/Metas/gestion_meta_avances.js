// gestion_meta_avances.js
$(document).ready(function () {
    // DataTable
    $('#avancesTable').DataTable({
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

    // Editar avance -> cargar datos
    $('.btn-editar-avance').on('click', function () {
        $('#avance_id').val($(this).data('id'));
        $('#id_avance_editar').val($(this).data('avance'));
        $('#id_fecha_registro_editar').val($(this).data('fecha'));
        $('#id_departamento_editar').val($(this).data('departamento'));
        $('#erroresEditarAvance').addClass('d-none').empty();

        $('#formEditarAvance input, #formEditarAvance select').removeClass(
            'is-invalid'
        );
        $('#modalEditarAvance').modal('show');
    });

    // Validación genérica mejorada
    function validarFormularioAvance(form, errorDivId) {
        let errores = [];
        let camposInvalidos = [];

        // Obtener campos por sus nombres (funciona para ambos formularios)
        const avance = form.find('[name="avance"]');
        const fecha = form.find('[name="fecha_registro"]');
        const departamento = form.find('[name="departamento"]');

        // Validar avance
        if (!avance.val().trim()) {
            errores.push('El campo Avance es obligatorio.');
            camposInvalidos.push(avance);
        }

        // Validar fecha
        if (!fecha.val().trim()) {
            errores.push('El campo Fecha es obligatorio.');
            camposInvalidos.push(fecha);
        }

        // Validar departamento (solo si no es hidden)
        if (departamento.is(':visible') && !departamento.val()) {
            errores.push('Debe seleccionar un Departamento.');
            camposInvalidos.push(departamento);
        }

        if (errores.length > 0) {
            $('#' + errorDivId)
                .removeClass('d-none')
                .html(
                    '<strong>Errores:</strong><ul><li>' +
                        errores.join('</li><li>') +
                        '</li></ul>'
                );
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });
            return false;
        } else {
            $('#' + errorDivId)
                .addClass('d-none')
                .empty();
            return true;
        }
    }

    // Validación Crear
    $('#formCrearAvance').on('submit', function (e) {
        const form = $(this);
        if (!validarFormularioAvance(form, 'erroresCrearAvance')) {
            e.preventDefault();
        }
    });

    // Validación Editar
    $('#formEditarAvance').on('submit', function (e) {
        const form = $(this);
        if (!validarFormularioAvance(form, 'erroresEditarAvance')) {
            e.preventDefault();
        }
    });

    // Quitar errores al escribir/seleccionar
    $(document).on('input change', 'input, select', function () {
        $(this).removeClass('is-invalid');
        // Ocultar errores generales cuando se corrige un campo
        $(this).closest('form').find('.alert-danger').addClass('d-none');
    });
});
