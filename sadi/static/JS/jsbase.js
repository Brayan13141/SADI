// Script para mejorar la interacción del menú
document.addEventListener('DOMContentLoaded', function () {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach((link) => {
        link.addEventListener('click', function () {
            // Remover la clase active de todos los elementos
            navLinks.forEach((item) => {
                item.classList.remove('active');
                item.classList.add('text-dark');
            });

            // Agregar la clase active al elemento clickeado
            this.classList.add('active');
            this.classList.remove('text-dark');
        });
    });
});
