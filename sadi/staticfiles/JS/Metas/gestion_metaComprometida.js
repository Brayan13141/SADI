document.addEventListener('DOMContentLoaded', function () {
    // Botón Editar -> cargar datos al modal
    const btnEditar = document.querySelector('.btn-editar-comprometida');
    if (btnEditar) {
        btnEditar.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const valor = this.getAttribute('data-valor');

            document.getElementById('comprometida_id').value = id;
            document.getElementById('id_valor_editar').value = valor;

            // Limpiar errores previos al abrir el modal
            document
                .getElementById('erroresEditarComprometida')
                .classList.add('d-none');
            document
                .getElementById('id_valor_editar')
                .classList.remove('is-invalid');

            const modal = new bootstrap.Modal(
                document.getElementById('modalEditarComprometida')
            );
            modal.show();
        });
    }

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
            const errorDiv = document.getElementById(
                'erroresCrearComprometida'
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
    const modales = ['modalCrearComprometida', 'modalEditarComprometida'];
    modales.forEach(function (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.addEventListener('hidden.bs.modal', function () {
                const errorDiv = this.querySelector('.alert-danger');
                if (errorDiv) {
                    errorDiv.classList.add('d-none');
                    errorDiv.textContent = '';
                }

                const inputs = this.querySelectorAll('input');
                inputs.forEach((input) => {
                    input.classList.remove('is-invalid');
                });
            });
        }
    });
});
