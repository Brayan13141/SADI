$(document).ready(function () {
    const inputclave = document.getElementById('inputclave');
    const inputclaveoculta = document.getElementById('inputclaveoculta');

    inputclave.addEventListener('input', () => {
        if (inputclave.value.trim() !== '') {
            inputclaveoculta.value = inputclave.value.trim();
        } else {
            inputclaveoculta.value = 'AUTO';
        }
    });

    // DataTable
    $('#metasTable').DataTable({
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

    // Cuando el usuario haga clic en una fila de la tabla
    $('#metasTable tbody').on('click', 'tr.fila-meta', function () {
        // Quitar selección previa
        $('#metasTable tbody tr').removeClass('fila-seleccionada');

        // Marcar la fila actual
        $(this).addClass('fila-seleccionada');
        let metaId = $(this).data('id');
        let clave = $(this).data('clave');
        let nombre = $(this).data('nombre');
        let compId = $(this).data('comprometida-id');
        let compValor = $(this).data('comprometida-valor');

        if (compId) {
            $('#infoComprometida').html(`
            <p><strong>Meta:</strong> ${clave} - ${nombre}</p>
            <p><strong>Valor comprometido:</strong> ${compValor}</p>
        `);
        } else {
            $('#infoComprometida').html(`
            <p><strong>Meta:</strong> ${clave} - ${nombre}</p>
            <p class="text-danger">No tiene meta comprometida registrada.</p>
        `);
        }

        $('#btnVerComprometida')
            .removeClass('d-none')
            .attr('href', `/metas/${metaId}/comprometida/`);
    });

    $('.btn-editar').on('click', function () {
        const fila = $(this).closest('.fila-meta');

        // Datos
        const metaId = $(this).data('id');
        const clave = $(this).data('clave');
        const nombre = $(this).data('nombre');
        const lineaB = $(this).data('lineabase');
        const metaCumplir = $(this).data('metacumplir');
        const proyectoId = $(this).data('proyecto');
        const departamentoId = $(this).data('departamento');
        const indicador = $(this).data('indicador');
        const unidadMedida = $(this).data('unidadmedida');
        const metodoCalculo = $(this).data('metodocalculo');
        let variableB = $(this).data('variableb') === 'True';
        const cicloId = $(this).data('ciclo');
        const activa = $(this).data('activa') === 'True';
        const acumulable = $(this).data('acumulable') === 'True';
        const porcentages = $(this).data('porcentages') === 'True';

        // Llenar el formulario
        $('#meta_id').val(metaId);
        $('#id_clave').val(clave);
        $('#id_nombre').val(nombre);
        $('#eid_lineabase').val(lineaB);
        $('#eid_metacumplir').val(metaCumplir);
        $('#id_proyecto').val(proyectoId);
        $('#id_departamento').val(departamentoId);
        $('#id_indicador').val(indicador);
        $('#id_acumulable').prop('checked', acumulable);
        $('#id_unidadmedida').val(unidadMedida);
        $('#id_metodocalculo').val(metodoCalculo);
        $('#Eid_variableb').prop('checked', variableB);
        $('#id_ciclo').val(cicloId);
        $('#id_activa').prop('checked', activa);
        $('#Eid_porcentages').prop('checked', porcentages);
        $('#Eid_acumulable').prop('checked', acumulable);

        // Mostrar ejemplo dinámico si está activado
        togglePorcentajeUI(porcentages);

        // Deshabilitar campos para docentes
        if (usuarioRol === 'DOCENTE') {
            $(
                '#id_clave, #id_nombre, #id_proyecto, #id_departamento, #id_ciclo, #id_activa, #id_indicador, #id_unidadmedida, #id_metodocalculo,  #Eid_variableb'
            ).prop('disabled', true);
        } else {
            $(
                '#formEditar input, #formEditar select, #formEditar textarea'
            ).prop('disabled', false);
        }

        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $(
            '#formEditar input, #formEditar select, #formEditar textarea'
        ).removeClass('is-invalid');

        // Mostrar modal
        $('#modalEditar').modal('show');
    }); // Botón Editar -> cargar datos al modal de metas

    // Listener para cuando el usuario activa/desactiva porcentajes en el modal
    $('#id_porcentages').on('change', function () {
        togglePorcentajeUI(this.checked);
    });
    $('#Eid_porcentages').on('change', function () {
        togglePorcentajeUI(this.checked);
    });

    // Función para mostrar animación + símbolo de %
    function togglePorcentajeUI(activar) {
        const inputs = ['#id_lineabase', '#id_metacumplir', '#id_variableb'];

        if (activar) {
            inputs.forEach((sel) => {
                const $input = $(sel);

                // Añadir placeholder de ejemplo
                $input.attr('placeholder', 'Ej: 85.55 %');

                // Animación visual
                $input
                    .addClass('is-percentage')
                    .animate({ backgroundColor: '#e8f5e9' }, 300);
            });

            $('#labelEjemplo')
                .text('Formato en porcentaje (0 - 100)')
                .fadeIn(300);
        } else {
            inputs.forEach((sel) => {
                const $input = $(sel);
                $input.attr('placeholder', 'Ej: 1500.50');
                $input
                    .removeClass('is-percentage')
                    .animate({ backgroundColor: '#fff' }, 300);
            });

            $('#labelEjemplo').text('Formato en cantidad').fadeIn(300);
        }
    }

    // Validación Crear
    $('#formCrear').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresCrear').addClass('d-none').empty();
        $('input, select, textarea', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        // Validar campos requeridos
        const camposRequeridos = [
            'nombre',

            'proyecto',
            'indicador',
            'unidadMedida',
            'metodoCalculo',
            'acumulable',
        ];

        camposRequeridos.forEach(
            function (campo) {
                if (
                    !$('[name="' + campo + '"]', this)
                        .val()
                        .trim()
                ) {
                    errores.push('El campo ' + campo + ' es obligatorio.');
                    camposInvalidos.push($('[name="' + campo + '"]', this));
                }
            }.bind(this)
        );

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });

            $('#erroresCrear')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Validación Editar
    $('#formEditar').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $('input, select, textarea', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = [];

        // Validar campos requeridos
        const camposRequeridos = [
            'clave',
            'nombre',
            'proyecto',
            'acumulable',
            'indicador',
            'unidadMedida',
            'metodoCalculo',
        ];

        camposRequeridos.forEach(function (campo) {
            const field = $('#id_' + campo.toLowerCase());
            if (!field.val().trim()) {
                errores.push('El campo ' + campo + ' es obligatorio.');
                camposInvalidos.push(field);
            }
        });

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            camposInvalidos.forEach(function (campo) {
                campo.addClass('is-invalid');
            });

            $('#erroresEditar')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Quitar el resaltado de error cuando el usuario empiece a escribir
    $('input, select, textarea').on('input change', function () {
        $(this).removeClass('is-invalid');
    });

    // Limpiar formularios al cerrar modales
    $('#modalCrear').on('hidden.bs.modal', function () {
        $(this).find('form')[0].reset();
        $(this).find('.is-invalid').removeClass('is-invalid');
        $('#erroresCrear').addClass('d-none').empty();
    });

    $('#modalEditar').on('hidden.bs.modal', function () {
        $(this).find('.is-invalid').removeClass('is-invalid');
        $('#erroresEditar').addClass('d-none').empty();
    });
});
