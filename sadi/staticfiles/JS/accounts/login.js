document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const loginInput = form.querySelector("input[name='login']");
    const passwordInput = form.querySelector("input[name='password']");

    form.addEventListener('submit', (e) => {
        let valido = true;
        let mensajes = [];

        // Validar login
        if (loginInput.value.trim() === '') {
            valido = false;
            mensajes.push('El campo de usuario/correo es obligatorio.');
            loginInput.classList.add('is-invalid');
        } else {
            loginInput.classList.remove('is-invalid');
        }

        // Validar contraseña
        if (passwordInput.value.trim() === '') {
            valido = false;
            mensajes.push('La contraseña es obligatoria.');
            passwordInput.classList.add('is-invalid');
        } else if (passwordInput.value.length < 4) {
            valido = false;
            mensajes.push('La contraseña debe tener al menos 4 caracteres.');
            passwordInput.classList.add('is-invalid');
        } else {
            passwordInput.classList.remove('is-invalid');
        }

        if (!valido) {
            e.preventDefault(); // no enviamos el formulario
            mostrarErrores(mensajes);
        }
    });

    function mostrarErrores(errores) {
        // Limpiar alertas previas
        document
            .querySelectorAll('.alert-cliente')
            .forEach((el) => el.remove());

        const contenedor = document.createElement('div');
        contenedor.className = 'alert alert-danger alert-cliente mt-2';
        contenedor.innerHTML = errores.join('<br>');
        form.prepend(contenedor);
    }
});
