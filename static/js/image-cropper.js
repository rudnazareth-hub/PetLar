/**
 * Image Cropper
 *
 * Sistema reutilizável de crop de imagens usando Cropper.js
 *
 * Uso:
 * 1. Incluir Cropper.js no template: <link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.css" rel="stylesheet">
 * 2. Incluir script: <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.js"></script>
 * 3. Incluir este arquivo: <script src="/static/js/image-cropper.js"></script>
 * 4. Configurar window.config_{modalId} com modalId, aspectRatio e maxFileSizeMB
 */

// Armazenar instâncias do Cropper para cada modal
const cropperInstances = {};

/**
 * Inicializa o cropper para um modal específico
 */
function initImageCropper(modalId, aspectRatio = 1.0, maxFileSizeMB = 5) {
    const inputFile = document.getElementById(`input-${modalId}`);
    const uploadSection = document.getElementById(`upload-section-${modalId}`);
    const cropperContainer = document.getElementById(`cropper-container-${modalId}`);
    const cropperImage = document.getElementById(`cropper-image-${modalId}`);
    const previewImage = document.getElementById(`preview-${modalId}`);
    const btnChange = document.getElementById(`btn-change-${modalId}`);
    const btnSubmit = document.getElementById(`btn-submit-${modalId}`);
    const fotoBase64Input = document.getElementById(`foto-base64-${modalId}`);
    const form = document.getElementById(`form-${modalId}`);

    if (!inputFile || !cropperContainer || !cropperImage) {
        console.error(`Elementos do modal ${modalId} não encontrados`);
        return;
    }

    // Evento: Seleção de arquivo
    inputFile.addEventListener('change', function(e) {
        const file = e.target.files[0];

        if (!file) return;

        // Validar tamanho
        const maxBytes = maxFileSizeMB * 1024 * 1024;
        if (file.size > maxBytes) {
            alert(`Arquivo muito grande! Tamanho máximo: ${maxFileSizeMB}MB`);
            inputFile.value = '';
            return;
        }

        // Validar tipo
        if (!file.type.startsWith('image/')) {
            alert('Por favor, selecione um arquivo de imagem válido.');
            inputFile.value = '';
            return;
        }

        // Ler arquivo
        const reader = new FileReader();
        reader.onload = function(event) {
            // Ocultar seção de upload e mostrar cropper
            uploadSection.classList.add('d-none');
            cropperContainer.classList.remove('d-none');
            btnSubmit.disabled = false;

            // Definir imagem no cropper
            cropperImage.src = event.target.result;

            // Destruir cropper anterior se existir
            if (cropperInstances[modalId]) {
                cropperInstances[modalId].destroy();
            }

            // Inicializar Cropper.js
            cropperInstances[modalId] = new Cropper(cropperImage, {
                aspectRatio: aspectRatio,
                viewMode: 2,
                dragMode: 'move',
                autoCropArea: 1,
                restore: false,
                guides: true,
                center: true,
                highlight: false,
                cropBoxMovable: true,
                cropBoxResizable: true,
                toggleDragModeOnDblclick: false,
                crop: function(event) {
                    // Atualizar preview em tempo real
                    updatePreview(modalId, previewImage);
                }
            });
        };
        reader.readAsDataURL(file);
    });

    // Evento: Escolher outra imagem
    if (btnChange) {
        btnChange.addEventListener('click', function() {
            resetCropper(modalId, uploadSection, cropperContainer, inputFile, btnSubmit);
        });
    }

    // Evento: Submit do formulário
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            if (!cropperInstances[modalId]) {
                alert('Nenhuma imagem selecionada');
                return;
            }

            // Obter canvas da imagem cropada
            const canvas = cropperInstances[modalId].getCroppedCanvas({
                maxWidth: 1000,
                maxHeight: 1000,
                fillColor: '#fff',
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });

            // Converter para base64 (JPEG com qualidade 90)
            const base64 = canvas.toDataURL('image/jpeg', 0.9);

            // Definir no campo hidden
            fotoBase64Input.value = base64;

            // Submeter formulário
            form.submit();
        });
    }

    // Evento: Reset ao fechar modal
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', function() {
            resetCropper(modalId, uploadSection, cropperContainer, inputFile, btnSubmit);
        });
    }
}

/**
 * Atualiza o preview da imagem cropada
 */
function updatePreview(modalId, previewImage) {
    if (!cropperInstances[modalId]) return;

    const canvas = cropperInstances[modalId].getCroppedCanvas({
        width: 150,
        height: 150,
        imageSmoothingEnabled: true,
        imageSmoothingQuality: 'high'
    });

    if (canvas) {
        previewImage.src = canvas.toDataURL('image/jpeg', 0.9);
    }
}

/**
 * Reseta o cropper para estado inicial
 */
function resetCropper(modalId, uploadSection, cropperContainer, inputFile, btnSubmit) {
    // Destruir cropper
    if (cropperInstances[modalId]) {
        cropperInstances[modalId].destroy();
        delete cropperInstances[modalId];
    }

    // Resetar UI
    if (uploadSection) uploadSection.classList.remove('d-none');
    if (cropperContainer) cropperContainer.classList.add('d-none');
    if (inputFile) inputFile.value = '';
    if (btnSubmit) btnSubmit.disabled = true;
}

/**
 * Auto-inicialização de modais com configuração
 */
document.addEventListener('DOMContentLoaded', function() {
    // Procurar por todas as configurações de modal no window
    for (const key in window) {
        if (key.startsWith('config_modal')) {
            const config = window[key];
            if (config && config.modalId) {
                initImageCropper(
                    config.modalId,
                    config.aspectRatio || 1.0,
                    config.maxFileSizeMB || 5
                );
            }
        }
    }
});
