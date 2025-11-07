$(document).ready(function () {
    // Inicializar DataTable
    $('#departamentosTable').DataTable({
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

    // Manejar clic en botón Editar
    $('.btn-editar').on('click', function () {
        var departamentoId = $(this).data('id');
        var departamentoNombre = $(this).data('nombre');

        // Llenar el formulario con los datos del departamento
        $('#departamento_id').val(departamentoId);
        $('#id_nombre').val(departamentoNombre);

        // Mostrar el modal de edición
        $('#modalEditar').modal('show');
    });
});
