$(document).ready(function () {
    $('#tabla-metas').DataTable({
        scrollX: true,
        scrollY: '500px',
        scrollCollapse: true,
        fixedColumns: {
            left: 1,
        },
        lengthMenu: [5, 10, 15, 20, 50],
        autoWidth: false,
        paging: true,
        searching: true,
        info: true,
        pageLength: 5,
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json',
        },
        // Configuración adicional para mejorar el rendimiento con muchas columnas
        deferRender: true,
        scroller: true,
        stateSave: true,
    });

    let carrito = [];
    let selectedRow = null;

    function actualizarCarrito() {
        const lista = $('#carrito-lista');
        const empty = $('#empty-cart');
        const count = $('#cart-count');

        count.text(carrito.length);
        lista.find('.list-group-item').not('#empty-cart').remove();

        if (carrito.length === 0) {
            empty.show();
        } else {
            empty.hide();
            carrito.forEach((item) => {
                lista.append(`
                    <li class="list-group-item" data-id="${item.id}">
                        <div><strong>${item.clave}</strong> - ${item.nombre}</div>
                        <button class="btn-remove" data-id="${item.id}">
                            <i class="fas fa-times"></i>
                        </button>
                    </li>
                `);
            });
        }
    }

    // Función para mostrar detalles de la fila seleccionada
    function mostrarDetalles(row) {
        const ciclo = row.data('ciclo') || '-';
        const departamento = row.data('departamento') || '-';

        $('#detail-ciclo').text(ciclo);
        $('#detail-departamento').text(departamento);
        $('#details-panel').slideDown();
    }

    // Evento para seleccionar fila y mostrar detalles
    $(document).on('click', '#tabla-metas tbody tr', function (e) {
        // No activar si se hace clic en el botón de agregar
        if ($(e.target).is('button') || $(e.target).closest('button').length) {
            return;
        }

        // Quitar selección anterior
        if (selectedRow) {
            selectedRow.removeClass('selected');
        }

        // Seleccionar nueva fila
        selectedRow = $(this);
        selectedRow.addClass('selected');

        // Mostrar detalles
        mostrarDetalles(selectedRow);
    });

    $(document).on('click', '.btn-add', function () {
        const id = $(this).data('id');
        const clave = $(this).data('clave');
        const nombre = $(this).data('nombre');

        if (carrito.some((m) => m.id == id)) {
            Toastify({
                text: 'Ya está en la lista',
                duration: 2000,
                backgroundColor: '#e74a3b',
            }).showToast();
            return;
        }

        carrito.push({ id, clave, nombre });
        actualizarCarrito();

        $(this)
            .prop('disabled', true)
            .html('<i class="fas fa-check"></i> Agregada');

        Toastify({
            text: 'Meta agregada ✅',
            duration: 2000,
            backgroundColor: '#1cc88a',
        }).showToast();
    });

    $(document).on('click', '.btn-remove', function () {
        const id = $(this).data('id');
        carrito = carrito.filter((m) => m.id != id);
        actualizarCarrito();

        $(`.btn-add[data-id="${id}"]`)
            .prop('disabled', false)
            .html('<i class="fas fa-plus"></i> Agregar');

        Toastify({
            text: 'Meta eliminada ⚠️',
            duration: 2000,
            backgroundColor: '#f6c23e',
        }).showToast();
    });

    $('#aplicar-cambios').click(function () {
        const ciclo = $('#ciclo').val();
        const departamento = $('#departamento').val();

        if (carrito.length === 0) {
            Toastify({
                text: 'Debe agregar metas',
                duration: 2000,
                backgroundColor: '#e74a3b',
            }).showToast();
            return;
        }

        fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                action: 'apply',
                ciclo,
                departamento,
                metas: carrito.map((m) => m.id),
            }),
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.status === 'success') {
                    Toastify({
                        text: data.message,
                        duration: 2000,
                        backgroundColor: '#1cc88a',
                    }).showToast();

                    carrito = [];
                    actualizarCarrito();
                    $('.btn-add')
                        .prop('disabled', false)
                        .html('<i class="fas fa-plus"></i> Agregar');

                    setTimeout(() => {
                        location.reload();
                    }, 1000);
                } else {
                    Toastify({
                        text: data.message || 'Error',
                        duration: 3000,
                        backgroundColor: '#e74a3b',
                    }).showToast();
                }
            })
            .catch(() => {
                Toastify({
                    text: 'Error de conexión',
                    duration: 3000,
                    backgroundColor: '#e74a3b',
                }).showToast();
            });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === name + '=') {
                    cookieValue = decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );
                    break;
                }
            }
        }
        return cookieValue;
    }
});
