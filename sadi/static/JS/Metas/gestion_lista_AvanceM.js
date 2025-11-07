document.addEventListener('DOMContentLoaded', function () {
    // --- FUNCIÓN PARA MOSTRAR ERRORES DEBAJO DE LOS CAMPOS ---
    function mostrarError(campo, mensaje) {
        let errorDiv = campo.parentElement.querySelector('.error-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.classList.add(
                'error-feedback',
                'text-danger',
                'mt-1',
                'small'
            );
            campo.parentElement.appendChild(errorDiv);
        }
        errorDiv.textContent = mensaje;
        campo.classList.add('is-invalid');
    }

    // --- FUNCIÓN PARA LIMPIAR ERROR DE UN CAMPO ---
    function limpiarError(campo) {
        campo.classList.remove('is-invalid');
        const errorDiv = campo.parentElement.querySelector('.error-feedback');
        if (errorDiv) errorDiv.remove();
    }

    // --- FUNCIÓN GENERAL DE VALIDACIÓN ---
    function validarFormulario(formId) {
        const form = document.getElementById(formId);
        let esValido = true;

        // Limpia errores previos
        form.querySelectorAll('.is-invalid').forEach((input) =>
            limpiarError(input)
        );

        // Validar meta
        const metaSelect = form.querySelector('select[name="metaCumplir"]');
        if (metaSelect && !metaSelect.value) {
            mostrarError(metaSelect, 'Debe seleccionar una meta.');
            esValido = false;
        }

        // Validar avance
        const avanceInput = form.querySelector('input[name="avance"]');
        const valorAvance = parseFloat(avanceInput.value);
        if (isNaN(valorAvance)) {
            mostrarError(avanceInput, 'El avance debe ser un número.');
            esValido = false;
        } else if (valorAvance < 0 || valorAvance > 100) {
            mostrarError(avanceInput, 'El avance debe estar entre 0 y 100.');
            esValido = false;
        }

        // Validar fecha
        const fechaInput = form.querySelector('input[name="fecha_registro"]');
        if (fechaInput && !fechaInput.value) {
            mostrarError(fechaInput, 'Debe seleccionar una fecha.');
            esValido = false;
        }

        return esValido;
    }

    // --- LIMPIAR ERROR AL CAMBIAR UN CAMPO ---
    function activarLimpiezaErrores(formId) {
        const form = document.getElementById(formId);
        form.querySelectorAll('input, select').forEach((campo) => {
            campo.addEventListener('input', () => limpiarError(campo));
            campo.addEventListener('change', () => limpiarError(campo));
        });
    }

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

        if (departamentoId) {
            departamentoSelect.value = departamentoId;
            departamentoHidden.value = departamentoId;
        } else {
            departamentoSelect.value = '';
            departamentoHidden.value = '';
        }
    }

    // --- EVENTO META CREAR ---
    const metaCrear = document.getElementById('id_metaCumplir');
    if (metaCrear) {
        metaCrear.addEventListener('change', function () {
            actualizarDepartamento(
                this,
                'id_departamento',
                'id_departamento_hidden'
            );
        });
    }

    // --- ABRIR MODAL DE EDICIÓN Y CARGAR DATOS ---
    document.querySelectorAll('.btn-editar-avance').forEach((button) => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const avance = this.getAttribute('data-avance');
            const fecha = this.getAttribute('data-fecha');
            const metaId = this.getAttribute('data-meta-id');
            const metaNombre = this.getAttribute('data-meta-nombre');
            const departamento = this.getAttribute('data-departamento');

            // Cargar datos en el formulario de edición
            document.getElementById('avance_id_editar').value = id;
            document.getElementById('id_avance_editar').value = avance;
            document.getElementById('id_fecha_registro_editar').value = fecha;
            document.getElementById('id_metaCumplir_editar').value = metaNombre;
            document.getElementById('id_metaCumplir_editar_hidden').value =
                metaId;
            document.getElementById('id_departamento_editar').value =
                departamento;
            document.getElementById('id_departamento_hidden_editar').value =
                departamento;

            // Limpiar errores previos
            const form = document.getElementById('formEditarAvance');
            form.querySelectorAll('.error-feedback').forEach((el) =>
                el.remove()
            );
            form.querySelectorAll('.is-invalid').forEach((el) =>
                el.classList.remove('is-invalid')
            );

            // Abrir modal de edición
            const modal = new bootstrap.Modal(
                document.getElementById('modalEditarAvance')
            );
            modal.show();
        });
    });

    // --- SUBMIT FORMULARIO CREAR ---
    const formCrear = document.getElementById('formCrearAvance');
    if (formCrear) {
        activarLimpiezaErrores('formCrearAvance');
        formCrear.addEventListener('submit', function (e) {
            if (!validarFormulario('formCrearAvance')) {
                e.preventDefault();
            }
        });
    }

    // --- SUBMIT FORMULARIO EDITAR ---
    const formEditar = document.getElementById('formEditarAvance');
    if (formEditar) {
        activarLimpiezaErrores('formEditarAvance');
        formEditar.addEventListener('submit', function (e) {
            if (!validarFormulario('formEditarAvance')) {
                e.preventDefault();
            }
        });
    }
});
