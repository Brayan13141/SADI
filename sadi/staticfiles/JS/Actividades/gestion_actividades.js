$(document).ready(function () {
    // Inicializar DataTable
    $('#actividadesTable').DataTable({
        scrollX: true,
        scrollY: '300px',
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

    // ===== FUNCIONES EXISTENTES PARA EVIDENCIAS =====

    function getFilenameFromPath(path) {
        if (!path) return '';
        return path.split('/').pop();
    }

    function truncateFilename(filename, maxLength = 50) {
        if (filename.length <= maxLength) return filename;

        var extension = filename.split('.').pop();
        var name = filename.substring(
            0,
            filename.length - extension.length - 1
        );
        var truncated =
            name.substring(0, maxLength - extension.length - 3) + '...';

        return truncated + '.' + extension;
    }

    function getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        const iconMap = {
            pdf: 'fa-file-pdf text-danger',
            doc: 'fa-file-word text-primary',
            docx: 'fa-file-word text-primary',
            xls: 'fa-file-excel text-success',
            xlsx: 'fa-file-excel text-success',
            ppt: 'fa-file-powerpoint text-warning',
            pptx: 'fa-file-powerpoint text-warning',
            jpg: 'fa-file-image text-info',
            jpeg: 'fa-file-image text-info',
            png: 'fa-file-image text-info',
            gif: 'fa-file-image text-info',
            zip: 'fa-file-archive text-secondary',
            rar: 'fa-file-archive text-secondary',
            txt: 'fa-file-alt text-muted',
        };
        return iconMap[extension] || 'fa-file text-secondary';
    }

    // Manejar clic en botón Editar
    $(document).on('click', '.btn-editar', function () {
        // Obtener datos
        var actividadId = $(this).data('id');
        var nombre = $(this).data('nombre');
        var estado = $(this).data('estado');
        var descripcion = $(this).data('descripcion');
        var fechaInicio = $(this).data('fecha_inicio');
        var fechaFin = $(this).data('fecha_fin');
        var evidencia = $(this).data('evidencia');
        var metaId = $(this).data('meta_id');
        var responsableId = $(this).data('responsable_id');
        var departamentoId = $(this).data('departamento_id');
        var editable = $(this).data('editable');

        // Llenar formulario
        $('#actividad_id').val(actividadId);
        $('#Eid_nombre').val(nombre);
        $('#Eid_estado').val(estado);
        $('#id_descripcion').val(descripcion);
        $('#Eid_fecha_inicio').val(fechaInicio);
        $('#Eid_fecha_fin').val(fechaFin);
        $('#id_meta').val(metaId);
        $('#Eid_responsable').val(responsableId);
        $('#Eid_departamento').val(departamentoId);

        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $(
            '#formEditar input, #formEditar select, #formEditar textarea'
        ).removeClass('is-invalid');

        // Renderizar evidencias
        var evidenciasHtml = '';
        if (evidencia && evidencia.length > 0) {
            var archivos = evidencia.split(',');
            archivos.forEach(function (item) {
                var partes = item.split('|');
                if (partes.length === 2) {
                    var url = partes[0];
                    var nombre = partes[1];
                    var icono = getFileIcon(nombre);
                    var nombreReal = getFilenameFromPath(nombre);
                    var nombreTruncado = truncateFilename(nombreReal, 30);
                    evidenciasHtml += `
                        <li class="mb-1 d-flex align-items-center">
                            <i class="fas ${icono} me-2"></i>
                            <a href="${url}" download="${nombre}" class="text-decoration-none">
                                ${nombreTruncado}
                            </a>
                        </li>`;
                }
            });
        } else {
            evidenciasHtml =
                '<li><span class="text-muted">Sin evidencias</span></li>';
        }
        $('#listaEvidencias').html(evidenciasHtml);

        // Manejo editable
        if (editable) {
            $('#editarInputs').show();
            $('#noEditableMsg').hide();
            $('#btnGuardarEditar').show();
            $(
                '#formEditar input, #formEditar textarea, #formEditar select'
            ).prop('disabled', false);

            var departamentoInput = $('#id_departamento');
            var responsableInput = $('#id_responsable');
            // Crear o actualizar el input "editable" (finalizar actividad)
            var contenedorEditable = $('#contenedorEditable');
            contenedorEditable.empty(); // Limpiar cualquier input previo

            if (departamentoInput.length > 1 && responsableInput.length > 1) {
                var departamentoActual = departamentoInput.val();
                if (departamentoActual) {
                    filtrarResponsablesPorDepartamento(
                        departamentoActual,
                        '#id_responsable'
                    );
                    // Asegurar que el responsable actual esté seleccionado
                    responsableInput.val(responsableId);
                }
            }

            var switchEditable = `
                <div class="col-12 mb-3">
                    <div class="form-check form-switch">
                        <input type="checkbox" name="editable" class="form-check-input" id="id_editable">
                        <label class="form-check-label" for="id_editable">FINALIZAR ACTIVIDAD</label>
                    </div>
                    <small class="text-muted">Atención: al guardar los cambios, esta actividad se marcará como FINALIZADA y ya no podrá editarse.</small>
                </div>`;
            contenedorEditable.html(switchEditable);
        } else {
            $('#editarInputs').hide();
            $('#noEditableMsg').show();
            $('#btnGuardarEditar').hide();
            $(
                '#formEditar input, #formEditar textarea, #formEditar select'
            ).prop('disabled', true);
        }
        $('#csrf_token').prop('disabled', false);
        $('#actividad_id').prop('disabled', false);
        $('#id_estado').prop('disabled', false);

        // Mostrar modal
        $('#modalEditar').modal('show');
    });

    // Validación del formulario de creación
    $('#formCrear').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresCrear').addClass('d-none').empty();
        $('input, select, textarea', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = {};

        // Validar campos obligatorios
        if (!$('[name="descripcion"]', this).val().trim()) {
            errores.push('El campo Descripción es obligatorio.');
            camposInvalidos.descripcion = $('[name="descripcion"]', this);
        }
        if (!$('[name="fecha_inicio"]', this).val()) {
            errores.push('El campo Fecha inicio es obligatorio.');
            camposInvalidos.fecha_inicio = $('[name="fecha_inicio"]', this);
        }
        if (!$('[name="fecha_fin"]', this).val()) {
            errores.push('El campo Fecha fin es obligatorio.');
            camposInvalidos.fecha_fin = $('[name="fecha_fin"]', this);
        }
        if (!$('[name="meta"]', this).val()) {
            errores.push('Debe seleccionar una meta.');
            camposInvalidos.meta = $('[name="meta"]', this);
        }
        if (!$('[name="responsable"]', this).val()) {
            errores.push('Debe seleccionar un responsable.');
            camposInvalidos.responsable = $('[name="responsable"]', this);
        }
        if (!$('[name="departamento"]', this).val()) {
            errores.push('Debe seleccionar un departamento.');
            camposInvalidos.departamento = $('[name="departamento"]', this);
        }

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            for (let campo in camposInvalidos) {
                camposInvalidos[campo].addClass('is-invalid');
            }

            // Mostrar errores generales
            $('#erroresCrear')
                .removeClass('d-none')
                .html(' <ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Validación del formulario de edición
    $('#formEditar').on('submit', function (e) {
        // Limpiar errores previos
        $('#erroresEditar').addClass('d-none').empty();
        $('input, select, textarea', this).removeClass('is-invalid');

        let errores = [];
        let camposInvalidos = {};

        if (!$('#id_descripcion').val().trim()) {
            errores.push('El campo Descripción es obligatorio.');
            camposInvalidos.descripcion = $('#id_descripcion');
        }
        if (!$('#Eid_fecha_inicio').val()) {
            errores.push('El campo Fecha inicio es obligatorio.');
            camposInvalidos.fecha_inicio = $('#id_fecha_inicio');
        }
        if (!$('#Eid_fecha_fin').val()) {
            errores.push('El campo Fecha fin es obligatorio.');
            camposInvalidos.fecha_fin = $('#id_fecha_fin');
        }
        if (!$('#id_meta').val()) {
            errores.push('Debe seleccionar una meta.');
            camposInvalidos.meta = $('#id_meta');
        }
        if (!$('#Eid_responsable').val()) {
            errores.push('Debe seleccionar un responsable.');
            camposInvalidos.responsable = $('#Eid_responsable');
        }
        if (!$('#Eid_departamento').val()) {
            errores.push('Debe seleccionar un departamento.');
            camposInvalidos.departamento = $('#Eid_departamento');
        }

        // Validar que fecha fin sea posterior a fecha inicio
        if ($('#id_fecha_inicio').val() && $('#id_fecha_fin').val()) {
            var fechaInicio = new Date($('#id_fecha_inicio').val());
            var fechaFin = new Date($('#id_fecha_fin').val());

            if (fechaFin <= fechaInicio) {
                errores.push(
                    'La fecha fin debe ser posterior a la fecha inicio.'
                );
                camposInvalidos.fecha_fin = $('#id_fecha_fin');
            }
        }

        if (errores.length > 0) {
            e.preventDefault();

            // Aplicar clase is-invalid a los campos con error
            for (let campo in camposInvalidos) {
                camposInvalidos[campo].addClass('is-invalid');
            }

            // Mostrar errores generales
            $('#erroresEditar')
                .removeClass('d-none')
                .html('<ul><li>' + errores.join('</li><li>') + '</li></ul>');
        }
    });

    // Quitar el resaltado de error cuando el usuario empiece a escribir
    $(
        '#formCrear input, #formCrear select, #formCrear textarea, #formEditar input, #formEditar select, #formEditar textarea'
    ).on('input change', function () {
        $(this).removeClass('is-invalid');
    });
});
