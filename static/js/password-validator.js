/**
 * PasswordValidator - Sistema de validação de senha reutilizável
 *
 * Funcionalidades:
 * - Toggle de visibilidade de senha
 * - Medição de força de senha
 * - Atualização visual de requisitos
 * - Validação de senhas coincidentes
 * - Validação de formulário
 */

class PasswordValidator {
    /**
     * @param {Object} config - Configuração do validador
     * @param {string} config.passwordFieldId - ID do campo de senha
     * @param {string} config.confirmPasswordFieldId - ID do campo de confirmação (opcional)
     * @param {string} config.strengthBarId - ID da barra de progresso (opcional)
     * @param {string} config.strengthTextId - ID do texto de força (opcional)
     * @param {string} config.matchMessageId - ID da mensagem de coincidência (opcional)
     * @param {Object} config.requirements - IDs dos elementos de requisitos (opcional)
     * @param {number} config.minLength - Tamanho mínimo da senha (padrão: 8)
     * @param {boolean} config.showStrength - Exibir medidor de força (padrão: false)
     * @param {boolean} config.showRequirements - Exibir requisitos visuais (padrão: false)
     * @param {Function} config.onValidate - Callback customizado de validação (opcional)
     */
    constructor(config) {
        this.config = {
            minLength: 8,
            showStrength: false,
            showRequirements: false,
            ...config
        };

        this.passwordField = document.getElementById(this.config.passwordFieldId);
        this.confirmPasswordField = this.config.confirmPasswordFieldId
            ? document.getElementById(this.config.confirmPasswordFieldId)
            : null;

        if (!this.passwordField) {
            console.error(`Campo de senha com ID "${this.config.passwordFieldId}" não encontrado`);
            return;
        }

        this.init();
    }

    init() {
        // Configurar eventos de força de senha
        if (this.config.showStrength) {
            this.strengthBar = document.getElementById(this.config.strengthBarId);
            this.strengthText = document.getElementById(this.config.strengthTextId);

            if (this.strengthBar && this.strengthText) {
                this.passwordField.addEventListener('input', () => this.checkPasswordStrength());
            }
        }

        // Configurar eventos de senha coincidente
        if (this.confirmPasswordField && this.config.matchMessageId) {
            this.matchMessage = document.getElementById(this.config.matchMessageId);

            if (this.matchMessage) {
                this.confirmPasswordField.addEventListener('input', () => this.checkPasswordMatch());
            }
        }
    }

    /**
     * Verifica a força da senha e atualiza indicadores visuais
     */
    checkPasswordStrength() {
        const password = this.passwordField.value;
        let strength = 0;
        let color = 'danger';
        let text = 'Muito fraca';

        // Verificar requisitos
        const requirements = {
            length: password.length >= this.config.minLength,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // Atualizar indicadores visuais de requisitos
        if (this.config.showRequirements && this.config.requirements) {
            this.updateRequirementIndicators(requirements);
        }

        // Calcular força (20% para cada requisito)
        if (requirements.length) strength += 20;
        if (requirements.uppercase) strength += 20;
        if (requirements.lowercase) strength += 20;
        if (requirements.number) strength += 20;
        if (requirements.special) strength += 20;

        // Definir texto e cor baseado na força
        if (strength >= 80) {
            color = 'success';
            text = 'Forte';
        } else if (strength >= 60) {
            color = 'info';
            text = 'Média';
        } else if (strength >= 40) {
            color = 'warning';
            text = 'Fraca';
        }

        // Atualizar barra de progresso
        if (this.strengthBar) {
            this.strengthBar.style.width = strength + '%';
            this.strengthBar.className = 'progress-bar bg-' + color;
        }

        // Atualizar texto de força
        if (this.strengthText) {
            this.strengthText.textContent = text;
            this.strengthText.className = 'text-' + color;
        }

        return { strength, requirements };
    }

    /**
     * Atualiza indicadores visuais de requisitos de senha
     */
    updateRequirementIndicators(requirements) {
        const reqMap = {
            length: this.config.requirements.length,
            uppercase: this.config.requirements.uppercase,
            lowercase: this.config.requirements.lowercase,
            number: this.config.requirements.number
        };

        Object.keys(reqMap).forEach(key => {
            const elementId = reqMap[key];
            if (!elementId) return;

            const element = document.getElementById(elementId);
            if (!element) return;

            const isMet = requirements[key];
            const originalText = element.textContent
                .replace(/✓ /g, '')
                .replace(/<i.*?<\/i>/g, '')
                .trim();

            if (isMet) {
                element.classList.add('text-success');
                element.innerHTML = `<i class="bi bi-check-circle-fill"></i> ${originalText}`;
            } else {
                element.classList.remove('text-success');
                element.innerHTML = originalText;
            }
        });
    }

    /**
     * Verifica se as senhas coincidem
     */
    checkPasswordMatch() {
        if (!this.confirmPasswordField || !this.matchMessage) return true;

        const password = this.passwordField.value;
        const confirmPassword = this.confirmPasswordField.value;

        if (confirmPassword.length === 0) {
            this.matchMessage.innerHTML = '';
            return true;
        }

        if (password === confirmPassword) {
            this.matchMessage.innerHTML = '<span class="text-success"><i class="bi bi-check-circle"></i> As senhas coincidem</span>';
            return true;
        } else {
            this.matchMessage.innerHTML = '<span class="text-danger"><i class="bi bi-x-circle"></i> As senhas não coincidem</span>';
            return false;
        }
    }

    /**
     * Valida o formulário antes do envio
     * @param {Object} options - Opções de validação
     * @param {boolean} options.requireCurrent - Se requer senha atual (padrão: false)
     * @param {string} options.currentPasswordFieldId - ID do campo de senha atual
     */
    validateForm(options = {}) {
        const password = this.passwordField.value;
        const confirmPassword = this.confirmPasswordField ? this.confirmPasswordField.value : password;

        // Verificar senha atual se requerido
        if (options.requireCurrent && options.currentPasswordFieldId) {
            const currentPassword = document.getElementById(options.currentPasswordFieldId)?.value;
            if (!currentPassword) {
                alert('Digite sua senha atual');
                return false;
            }
        }

        // Verificar tamanho mínimo
        if (password.length < this.config.minLength) {
            alert(`A senha deve ter no mínimo ${this.config.minLength} caracteres`);
            return false;
        }

        // Verificar senhas coincidem
        if (this.confirmPasswordField && password !== confirmPassword) {
            alert('As senhas não coincidem!');
            this.confirmPasswordField.focus();
            return false;
        }

        // Verificar requisitos mínimos (maiúscula, minúscula, número)
        if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/\d/.test(password)) {
            alert('A senha deve conter pelo menos:\n- 1 letra maiúscula\n- 1 letra minúscula\n- 1 número');
            return false;
        }

        // Callback customizado de validação
        if (this.config.onValidate && typeof this.config.onValidate === 'function') {
            return this.config.onValidate(password, confirmPassword);
        }

        return true;
    }

    /**
     * Validação flexível para edição (senha opcional)
     */
    validateFormOptional(options = {}) {
        const password = this.passwordField.value;
        const confirmPassword = this.confirmPasswordField ? this.confirmPasswordField.value : '';

        // Se senha não foi preenchida, não validar
        if (!password && !confirmPassword) {
            return true;
        }

        // Se alguma senha foi preenchida, validar normalmente
        if (password || confirmPassword) {
            if (password !== confirmPassword) {
                alert('As senhas não coincidem!');
                return false;
            }

            if (password.length < this.config.minLength) {
                alert(`A senha deve ter no mínimo ${this.config.minLength} caracteres!`);
                return false;
            }
        }

        // Callback customizado de validação
        if (this.config.onValidate && typeof this.config.onValidate === 'function') {
            return this.config.onValidate(password, confirmPassword);
        }

        return true;
    }
}

/**
 * Função global para toggle de visibilidade de senha
 * @param {string} fieldId - ID do campo de senha
 */
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const icon = document.getElementById('icon_' + fieldId);

    if (!field) {
        console.error(`Campo com ID "${fieldId}" não encontrado`);
        return;
    }

    if (field.type === 'password') {
        field.type = 'text';
        if (icon) {
            icon.classList.remove('bi-eye');
            icon.classList.add('bi-eye-slash');
        }
    } else {
        field.type = 'password';
        if (icon) {
            icon.classList.remove('bi-eye-slash');
            icon.classList.add('bi-eye');
        }
    }
}

// Exportar para uso global
window.PasswordValidator = PasswordValidator;
window.togglePassword = togglePassword;
