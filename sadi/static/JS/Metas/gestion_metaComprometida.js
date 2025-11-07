document.addEventListener('DOMContentLoaded', function () {
    // Botones Editar -> cargar datos al modal
    const btnEditarList = document.querySelectorAll('.btn-editar-comprometida');
    btnEditarList.forEach((btnEditar) => {
        btnEditar.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const valor = this.getAttribute('data-valor');
            const ciclo = this.getAttribute('data-ciclo');

            document.getElementById('comprometida_id').value = id;
            document.getElementById('id_valor_editar').value = valor;
            document.getElementById('ciclo_editar').value = ciclo;

            // Limpiar errores previos al abrir el modal
            document
                .getElementById('erroresEditarComprometida')
                .classList.add('d-none');
            document
                .getElementById('id_valor_editar')
                .classList.remove('is-invalid');
        });
    });

    // Botones Eliminar -> cargar datos al modal
    const btnEliminarList = document.querySelectorAll(
        '.btn-eliminar-comprometida'
    );
    btnEliminarList.forEach((btnEliminar) => {
        btnEliminar.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const valor = this.getAttribute('data-valor');

            document.getElementById('eliminar_id').value = id;
            document.getElementById('eliminar_valor').textContent = valor;
        });
    });

    // Validación de formularios (solo al enviar)
    function validarValor(valor) {
        if (!valor) {
            return 'El valor es obligatorio.';
        } else if (parseFloat(valor) < 0) {
            return 'El valor no puede ser negativo.';
        }
        return '';
    }

    // Validar formulario de creación al enviar
    const formCrear = document.getElementById('formCrearComprometida');
    if (formCrear) {
        formCrear.addEventListener('submit', function (e) {
            const valorInput = this.querySelector('input[name="valor"]');
            const cicloSelect = this.querySelector('select[name="ciclo"]');
            const errorDiv = document.getElementById(
                'erroresCrearComprometida'
            );
            let errorMsg = '';

            // Validar ciclo
            if (!cicloSelect.value) {
                errorMsg = 'El ciclo es obligatorio.';
                cicloSelect.classList.add('is-invalid');
            } else {
                cicloSelect.classList.remove('is-invalid');
            }

            // Validar valor
            const valorError = validarValor(valorInput.value);
            if (valorError) {
                errorMsg = errorMsg ? errorMsg + ' ' + valorError : valorError;
                valorInput.classList.add('is-invalid');
            } else {
                valorInput.classList.remove('is-invalid');
            }

            if (errorMsg) {
                e.preventDefault();
                errorDiv.textContent = errorMsg;
                errorDiv.classList.remove('d-none');
            } else {
                errorDiv.classList.add('d-none');
            }
        });
    }

    // Validar formulario de edición al enviar
    const formEditar = document.getElementById('formEditarComprometida');
    if (formEditar) {
        formEditar.addEventListener('submit', function (e) {
            const valorInput = document.getElementById('id_valor_editar');
            const errorDiv = document.getElementById(
                'erroresEditarComprometida'
            );
            const errorMsg = validarValor(valorInput.value);

            if (errorMsg) {
                e.preventDefault();
                errorDiv.textContent = errorMsg;
                errorDiv.classList.remove('d-none');
                valorInput.classList.add('is-invalid');
            } else {
                errorDiv.classList.add('d-none');
                valorInput.classList.remove('is-invalid');
            }
        });
    }

    // Limpiar errores al cerrar modales
    const modales = [
        'modalCrearComprometida',
        'modalEditarComprometida',
        'modalEliminarComprometida',
    ];
    modales.forEach(function (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.addEventListener('hidden.bs.modal', function () {
                // Limpiar mensajes de error
                const errorDivs = this.querySelectorAll('.alert-danger');
                errorDivs.forEach((div) => {
                    div.classList.add('d-none');
                    div.textContent = '';
                });

                // Limpiar clases de invalid
                const invalidElements = this.querySelectorAll('.is-invalid');
                invalidElements.forEach((el) => {
                    el.classList.remove('is-invalid');
                });

                // Limpiar campos del modal de crear
                if (modalId === 'modalCrearComprometida') {
                    const form = document.getElementById(
                        'formCrearComprometida'
                    );
                    if (form) {
                        form.reset();
                    }
                }
            });
        }
    });

    // Limpiar formulario de crear cuando se abre el modal
    const modalCrear = document.getElementById('modalCrearComprometida');
    if (modalCrear) {
        modalCrear.addEventListener('show.bs.modal', function () {
            const form = document.getElementById('formCrearComprometida');
            if (form) {
                form.reset();
            }
            document
                .getElementById('erroresCrearComprometida')
                .classList.add('d-none');
        });
    }
});
