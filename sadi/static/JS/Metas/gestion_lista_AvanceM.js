document.addEventListener('DOMContentLoaded', function () {
    // --- ACTUALIZAR DEPARTAMENTO SEGÚN META SELECCIONADA ---
    function actualizarDepartamento(
        metaSelect,
        departamentoSelectId,
        departamentoHiddenId
    ) {
        const departamentoSelect =
            document.getElementById(departamentoSelectId);
        const departamentoHidden =
            document.getElementById(departamentoHiddenId);
        const selectedOption = metaSelect.options[metaSelect.selectedIndex];
        const departamentoId = selectedOption.getAttribute(
            'data-departamento-id'
        );

        // Buscar la opción correspondiente en el select de departamentos
        const options = departamentoSelect.options;
        for (let i = 0; i < options.length; i++) {
            if (options[i].value === departamentoId) {
                departamentoSelect.value = departamentoId;
                departamentoHidden.value = departamentoId;
                return;
            }
        }

        // Si no se encuentra el departamento, limpiar los valores
        departamentoSelect.value = '';
        departamentoHidden.value = '';
    }

    // --- EVENTOS PARA ACTUALIZAR DEPARTAMENTO ---
    // Modal de creación
    document
        .getElementById('id_metaCumplir')
        .addEventListener('change', function () {
            actualizarDepartamento(
                this,
                'id_departamento',
                'id_departamento_hidden'
            );
            validarCampo(this, 'metaCumplir');
        });

    // Modal de edición
    document
        .getElementById('id_metaCumplir_editar')
        .addEventListener('change', function () {
            actualizarDepartamento(
                this,
                'id_departamento_editar',
                'id_departamento_hidden_editar'
            );
            validarCampo(this, 'metaCumplir', true);
        });

    // --- VALIDACIONES DE CAMPOS ---
    function validarCampo(campo, nombreCampo, esEdicion = false) {
        const sufijo = esEdicion ? '-editar' : '';
        const errorElement = document.getElementById(
            `error-${nombreCampo}${sufijo}`
        );

        // Limpiar mensajes de error previos
        campo.classList.remove('is-invalid');
        errorElement.textContent = '';

        let esValido = true;
        let mensajeError = '';

        switch (nombreCampo) {
            case 'metaCumplir':
                if (!campo.value) {
                    mensajeError = 'Debe seleccionar una meta.';
                    esValido = false;
                }
                break;

            case 'avance':
                const valorAvance = parseFloat(campo.value);
                if (isNaN(valorAvance)) {
                    mensajeError = 'El avance debe ser un número válido.';
                    esValido = false;
                } else if (valorAvance < 0 || valorAvance > 100) {
                    mensajeError = 'El avance debe estar entre 0% y 100%.';
                    esValido = false;
                }
                break;

            case 'fecha_registro':
                if (!campo.value) {
                    mensajeError = 'Debe seleccionar una fecha.';
                    esValido = false;
                } else {
                    const fechaSeleccionada = new Date(campo.value);
                    const hoy = new Date();
                    if (fechaSeleccionada > hoy) {
                        mensajeError = 'La fecha no puede ser futura.';
                        esValido = false;
                    }
                }
                break;
        }

        if (!esValido) {
            campo.classList.add('is-invalid');
            errorElement.textContent = mensajeError;
        } else {
            campo.classList.add('is-valid');
        }

        return esValido;
    }

    // Agregar eventos de validación a los campos
    document.getElementById('id_avance').addEventListener('blur', function () {
        validarCampo(this, 'avance');
    });

    document
        .getElementById('id_fecha_registro')
        .addEventListener('change', function () {
            validarCampo(this, 'fecha_registro');
        });

    document
        .getElementById('id_avance_editar')
        .addEventListener('blur', function () {
            validarCampo(this, 'avance', true);
        });

    // --- ABRIR MODAL DE EDICIÓN ---
    document.querySelectorAll('.btn-editar-avance').forEach((button) => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const avance = this.getAttribute('data-avance');
            const fecha = this.getAttribute('data-fecha');
            const meta = this.getAttribute('data-meta');
            const metaNombre = this.getAttribute('data-meta-nombre');
            const departamento = this.getAttribute('data-departamento');

            document.getElementById('avance_id_editar').value = id;
            document.getElementById('id_fecha_registro_editar').value = fecha;
            //document.getElementById('id_avance_editar').value = avance;
            document.getElementById('id_metaCumplir_editar').value = metaNombre;
            document.getElementById('id_metaCumplir_editar_hidden').value =
                meta;

            // Establecer el valor del departamento en el select deshabilitado y en el campo oculto
            document.getElementById('id_departamento_editar').value =
                departamento;
            document.getElementById('id_departamento_hidden_editar').value =
                departamento;

            const modal = new bootstrap.Modal(
                document.getElementById('modalEditarAvance')
            );
            modal.show();
        });
    });

    // --- VALIDACIÓN DE FORMULARIOS COMPLETOS ---
    function validarFormularioCompleto(formId, esEdicion = false) {
        const form = document.getElementById(formId);
        const sufijo = esEdicion ? '-editar' : '';
        let esValido = true;

        // Validar meta
        const metaSelect = form.querySelector('select[name="metaCumplir"]');
        if (!validarCampo(metaSelect, 'metaCumplir', esEdicion)) {
            esValido = false;
        }

        // Validar avance
        const avanceInput = form.querySelector('input[name="avance"]');
        if (!validarCampo(avanceInput, 'avance', esEdicion)) {
            esValido = false;
        }

        // Validar fecha
        const fechaInput = form.querySelector('input[name="fecha_registro"]');
        if (!validarCampo(fechaInput, 'fecha_registro', esEdicion)) {
            esValido = false;
        }

        return esValido;
    }

    // Validar formulario de creación al enviar
    document
        .getElementById('formCrearAvance')
        .addEventListener('submit', function (e) {
            if (!validarFormularioCompleto('formCrearAvance')) {
                e.preventDefault();
                // Mostrar mensaje general de error
                document.getElementById('erroresCrearAvance').textContent =
                    'Por favor, corrija los errores en el formulario.';
                document
                    .getElementById('erroresCrearAvance')
                    .classList.remove('d-none');
            }
        });

    // Validar formulario de edición al enviar
    document
        .getElementById('formEditarAvance')
        .addEventListener('submit', function (e) {
            if (!validarFormularioCompleto('formEditarAvance', true)) {
                e.preventDefault();
                // Mostrar mensaje general de error
                document.getElementById('erroresEditarAvance').textContent =
                    'Por favor, corrija los errores en el formulario.';
                document
                    .getElementById('erroresEditarAvance')
                    .classList.remove('d-none');
            }
        });

    // Limpiar validaciones al cerrar modales
    document
        .getElementById('modalCrearAvance')
        .addEventListener('hidden.bs.modal', function () {
            limpiarValidaciones('formCrearAvance');
            document
                .getElementById('erroresCrearAvance')
                .classList.add('d-none');
        });

    document
        .getElementById('modalEditarAvance')
        .addEventListener('hidden.bs.modal', function () {
            limpiarValidaciones('formEditarAvance', true);
            document
                .getElementById('erroresEditarAvance')
                .classList.add('d-none');
        });

    function limpiarValidaciones(formId, esEdicion = false) {
        const form = document.getElementById(formId);
        const sufijo = esEdicion ? '-editar' : '';

        // Limpiar clases de validación
        const campos = form.querySelectorAll('select, input');
        campos.forEach((campo) => {
            campo.classList.remove('is-invalid');
            campo.classList.remove('is-valid');
        });

        // Limpiar mensajes de error
        const errores = form.querySelectorAll('.invalid-feedback');
        errores.forEach((error) => {
            error.textContent = '';
        });
    }
});
