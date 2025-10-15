/**
 * Perfil Photo Handler
 *
 * Gerencia o fluxo de seleção e crop de foto de perfil
 * Abre o seletor de arquivos diretamente ao clicar na foto ou botão
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos
    const photoInput = document.getElementById('hidden-photo-input');
    const profilePhoto = document.getElementById('profile-photo');
    const changePhotoBtn = document.getElementById('btn-change-photo');

    // Configuração do modal (deve existir no window)
    const modalConfig = window.config_modalFotoPerfil;

    if (!photoInput || !modalConfig) {
        console.warn('Elementos necessários para photo handler não encontrados');
        return;
    }

    // Função para abrir o seletor de arquivos
    function openFileSelector() {
        photoInput.click();
    }

    // Adicionar click handler na foto de perfil (se existir)
    if (profilePhoto) {
        profilePhoto.style.cursor = 'pointer';
        profilePhoto.addEventListener('click', openFileSelector);
    }

    // Adicionar click handler no botão de alterar foto
    if (changePhotoBtn) {
        changePhotoBtn.addEventListener('click', function(e) {
            e.preventDefault();
            openFileSelector();
        });
    }

    // Quando um arquivo for selecionado
    photoInput.addEventListener('change', function(e) {
        const file = e.target.files[0];

        if (!file) return;

        // Abrir o modal primeiro
        const modalElement = document.getElementById(modalConfig.modalId);
        const modal = new bootstrap.Modal(modalElement);
        modal.show();

        // Quando o modal estiver completamente visível, carregar a imagem
        modalElement.addEventListener('shown.bs.modal', function() {
            loadImageFromFile(
                modalConfig.modalId,
                file,
                modalConfig.aspectRatio,
                modalConfig.maxFileSizeMB
            );
        }, { once: true });
    });

    // Resetar o input quando o modal for fechado
    document.getElementById(modalConfig.modalId).addEventListener('hidden.bs.modal', function() {
        photoInput.value = '';
    });
});
