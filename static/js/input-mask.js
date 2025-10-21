/**
 * InputMask - Sistema de máscaras de digitação reutilizável
 *
 * Funcionalidades:
 * - Máscaras customizadas com padrões: 0 (número), A (maiúscula), a (minúscula)
 * - Aplicação automática durante digitação
 * - Suporte a unmask (enviar valor sem formatação)
 * - Máscaras pré-definidas (CPF, CNPJ, telefone, etc.)
 * - Eventos customizados
 *
 * Padrões de máscara:
 * - "0" = dígito numérico (0-9)
 * - "A" = letra maiúscula (A-Z)
 * - "a" = letra minúscula (a-z)
 * - Qualquer outro caractere = literal (será inserido automaticamente)
 *
 * Exemplos:
 * - CPF: "000.000.000-00"
 * - CNPJ: "00.000.000/0000-00"
 * - Telefone: "(00) 00000-0000"
 * - CEP: "00000-000"
 * - Placa Mercosul: "AAA-0A00"
 * - Cartão: "0000 0000 0000 0000"
 */

class InputMask {
    // Máscaras pré-definidas para uso comum
    static MASKS = {
        CPF: '000.000.000-00',
        CNPJ: '00.000.000/0000-00',
        TELEFONE: '(00) 00000-0000',
        TELEFONE_FIXO: '(00) 0000-0000',
        CEP: '00000-000',
        DATA: '00/00/0000',
        HORA: '00:00',
        DATA_HORA: '00/00/0000 00:00',
        PLACA_ANTIGA: 'AAA-0000',
        PLACA_MERCOSUL: 'AAA-0A00',
        CARTAO: '0000 0000 0000 0000',
        CVV: '000',
        CVV4: '0000',
        VALIDADE_CARTAO: '00/00'
    };

    /**
     * @param {HTMLInputElement} input - Elemento input
     * @param {string} mask - Padrão da máscara
     * @param {Object} options - Opções adicionais
     * @param {boolean} options.unmask - Se true, envia valor sem máscara no submit
     * @param {Function} options.onComplete - Callback quando máscara está completa
     */
    constructor(input, mask, options = {}) {
        this.input = input;
        this.mask = mask;
        this.options = {
            unmask: false,
            onComplete: null,
            ...options
        };

        this.init();
    }

    init() {
        // Adicionar classe para identificação
        this.input.classList.add('input-mask');

        // Aplicar máscara no valor inicial se houver
        if (this.input.value) {
            this.input.value = this.applyMask(this.input.value);
        }

        // Eventos de digitação
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('paste', (e) => this.handlePaste(e));

        // Se unmask está ativado, interceptar submit do formulário
        if (this.options.unmask) {
            const form = this.input.closest('form');
            if (form) {
                form.addEventListener('submit', (e) => this.handleSubmit(e));
            }
        }
    }

    /**
     * Aplica a máscara em um valor
     * @param {string} value - Valor a ser formatado
     * @returns {string} Valor formatado
     */
    applyMask(value) {
        // Remover caracteres não permitidos
        const cleanValue = this.cleanValue(value);
        let maskedValue = '';
        let valueIndex = 0;

        for (let i = 0; i < this.mask.length && valueIndex < cleanValue.length; i++) {
            const maskChar = this.mask[i];
            const valueChar = cleanValue[valueIndex];

            if (maskChar === '0') {
                // Dígito numérico
                if (/\d/.test(valueChar)) {
                    maskedValue += valueChar;
                    valueIndex++;
                } else {
                    break; // Valor inválido, parar
                }
            } else if (maskChar === 'A') {
                // Letra maiúscula
                if (/[a-zA-Z]/.test(valueChar)) {
                    maskedValue += valueChar.toUpperCase();
                    valueIndex++;
                } else {
                    break; // Valor inválido, parar
                }
            } else if (maskChar === 'a') {
                // Letra minúscula
                if (/[a-zA-Z]/.test(valueChar)) {
                    maskedValue += valueChar.toLowerCase();
                    valueIndex++;
                } else {
                    break; // Valor inválido, parar
                }
            } else {
                // Caractere literal (inserir automaticamente)
                maskedValue += maskChar;
                // Se o usuário digitou o caractere literal, avançar
                if (valueChar === maskChar) {
                    valueIndex++;
                }
            }
        }

        return maskedValue;
    }

    /**
     * Remove todos os caracteres literais, mantendo apenas os dados
     * @param {string} value - Valor formatado
     * @returns {string} Valor sem formatação
     */
    unmaskValue(value) {
        let unmasked = '';
        let maskIndex = 0;

        for (let i = 0; i < value.length && maskIndex < this.mask.length; i++) {
            const char = value[i];
            const maskChar = this.mask[maskIndex];

            if (maskChar === '0' || maskChar === 'A' || maskChar === 'a') {
                // É um caractere de dado
                unmasked += char;
                maskIndex++;
            } else if (char === maskChar) {
                // É um caractere literal
                maskIndex++;
            } else {
                // Caractere não esperado, ignorar
                continue;
            }
        }

        return unmasked;
    }

    /**
     * Limpa o valor removendo caracteres literais e mantendo apenas válidos
     * @param {string} value - Valor a ser limpo
     * @returns {string} Valor limpo
     */
    cleanValue(value) {
        return value.replace(/[^a-zA-Z0-9]/g, '');
    }

    /**
     * Manipula o evento de input (digitação)
     */
    handleInput(e) {
        const cursorPosition = this.input.selectionStart;
        const oldValue = e.target.value;
        const oldLength = oldValue.length;

        // Aplicar máscara
        const newValue = this.applyMask(oldValue);
        this.input.value = newValue;

        // Ajustar posição do cursor
        let newCursorPosition = cursorPosition;
        if (newValue.length > oldLength) {
            // Se valor aumentou, mover cursor
            newCursorPosition = cursorPosition + (newValue.length - oldLength);
        }

        // Garantir que cursor não fique em posição literal
        while (newCursorPosition < newValue.length && newCursorPosition < this.mask.length) {
            const maskChar = this.mask[newCursorPosition - 1];
            if (maskChar && maskChar !== '0' && maskChar !== 'A' && maskChar !== 'a') {
                newCursorPosition++;
            } else {
                break;
            }
        }

        this.input.setSelectionRange(newCursorPosition, newCursorPosition);

        // Verificar se máscara está completa
        if (newValue.length === this.mask.length && this.options.onComplete) {
            this.options.onComplete(this.unmaskValue(newValue));
        }
    }

    /**
     * Manipula o evento de keydown
     */
    handleKeydown(e) {
        // Permitir teclas de navegação e edição
        const allowedKeys = [
            'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight',
            'ArrowUp', 'ArrowDown', 'Home', 'End', 'Tab'
        ];

        if (allowedKeys.includes(e.key) || e.ctrlKey || e.metaKey) {
            return;
        }
    }

    /**
     * Manipula o evento de paste (colar)
     */
    handlePaste(e) {
        e.preventDefault();
        const pastedText = (e.clipboardData || window.clipboardData).getData('text');
        const maskedValue = this.applyMask(pastedText);
        this.input.value = maskedValue;
        this.input.dispatchEvent(new Event('input', { bubbles: true }));
    }

    /**
     * Manipula o submit do formulário (para unmask)
     */
    handleSubmit(e) {
        if (!this.options.unmask) return;

        const unmaskedValue = this.unmaskValue(this.input.value);

        // Criar input hidden com valor sem máscara
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = this.input.name + '_unmasked';
        hiddenInput.value = unmaskedValue;

        // Adicionar ao formulário
        this.input.form.appendChild(hiddenInput);

        // Opcional: substituir o valor do input original
        // this.input.value = unmaskedValue;
    }

    /**
     * Remove a máscara do input
     */
    destroy() {
        this.input.classList.remove('input-mask');
        // Remover eventos seria necessário guardar referências
    }
}

/**
 * DecimalMask - Sistema de formatação de valores decimais/monetários
 *
 * Funcionalidades:
 * - Formatação automática com separadores de milhar e decimais
 * - Suporte a valores negativos
 * - Configurável: casas decimais, separadores, prefixo/sufixo
 * - Formato brasileiro (vírgula para decimal, ponto para milhares)
 * - Remove formatação no submit para enviar valor numérico
 *
 * Padrão de formatação brasileiro:
 * - Separador decimal: vírgula (,)
 * - Separador de milhares: ponto (.)
 * - Exemplo: 1.234,56
 */
class DecimalMask {
    /**
     * @param {HTMLInputElement} input - Elemento input
     * @param {Object} options - Opções de configuração
     * @param {number} options.decimal_places - Número de casas decimais (padrão: 2)
     * @param {boolean} options.show_thousands - Exibir separador de milhares (padrão: true)
     * @param {boolean} options.allow_negative - Permitir valores negativos (padrão: false)
     * @param {string} options.prefix - Prefixo (ex: "R$ ") (padrão: "")
     * @param {string} options.suffix - Sufixo (ex: " kg") (padrão: "")
     */
    constructor(input, options = {}) {
        this.input = input;
        this.options = {
            decimal_places: 2,
            show_thousands: true,
            allow_negative: false,
            prefix: '',
            suffix: '',
            ...options
        };

        this.init();
    }

    init() {
        // Adicionar classe para identificação
        this.input.classList.add('decimal-mask');

        // Aplicar formatação no valor inicial se houver
        if (this.input.value && this.input.value.trim() !== '') {
            // Tentar parsear como número decimal (formato do servidor: 1234.56)
            const serverValue = parseFloat(this.input.value.replace(',', '.'));
            if (!isNaN(serverValue)) {
                this.input.value = this.format(serverValue);
            } else {
                this.input.value = this.format(0);
            }
        }

        // Eventos
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('paste', (e) => this.handlePaste(e));
        this.input.addEventListener('blur', (e) => this.handleBlur(e));

        // Interceptar submit do formulário
        const form = this.input.closest('form');
        if (form && !form.hasAttribute('data-decimal-submit-bound')) {
            form.setAttribute('data-decimal-submit-bound', 'true');
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    /**
     * Converte string formatada para número
     * @param {string} value - Valor formatado
     * @returns {number} Número parseado
     */
    parse(value) {
        if (!value) return 0;

        // Remover prefixo e sufixo
        let cleanValue = value;
        if (this.options.prefix) {
            cleanValue = cleanValue.replace(this.options.prefix, '');
        }
        if (this.options.suffix) {
            cleanValue = cleanValue.replace(this.options.suffix, '');
        }

        // Remover espaços
        cleanValue = cleanValue.trim();

        // Verificar sinal negativo
        const isNegative = cleanValue.startsWith('-');
        if (isNegative) {
            cleanValue = cleanValue.substring(1);
        }

        // Remover separadores de milhares (.)
        cleanValue = cleanValue.replace(/\./g, '');

        // Substituir vírgula decimal por ponto
        cleanValue = cleanValue.replace(',', '.');

        // Converter para número
        const number = parseFloat(cleanValue);

        return (isNegative && this.options.allow_negative) ? -number : number;
    }

    /**
     * Formata número para exibição
     * @param {number} value - Número a ser formatado
     * @returns {string} Valor formatado
     */
    format(value) {
        if (isNaN(value)) return '';

        // Verificar sinal
        const isNegative = value < 0;
        let absValue = Math.abs(value);

        // Arredondar para casas decimais
        absValue = absValue.toFixed(this.options.decimal_places);

        // Separar parte inteira e decimal
        let [integerPart, decimalPart] = absValue.split('.');

        // Adicionar separador de milhares
        if (this.options.show_thousands) {
            integerPart = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        }

        // Montar valor formatado
        let formatted = integerPart;
        if (this.options.decimal_places > 0) {
            formatted += ',' + (decimalPart || '0'.repeat(this.options.decimal_places));
        }

        // Adicionar sinal negativo
        if (isNegative && this.options.allow_negative) {
            formatted = '-' + formatted;
        }

        // Adicionar prefixo e sufixo
        if (this.options.prefix) {
            formatted = this.options.prefix + formatted;
        }
        if (this.options.suffix) {
            formatted = formatted + this.options.suffix;
        }

        return formatted;
    }

    /**
     * Manipula evento de input (digitação)
     */
    handleInput(e) {
        const oldValue = e.target.value;

        // Remover tudo exceto dígitos e sinal negativo
        let digitsOnly = oldValue.replace(/[^\d-]/g, '');

        // Garantir que sinal negativo só aparece no início
        const isNegative = digitsOnly.startsWith('-');
        digitsOnly = digitsOnly.replace(/-/g, '');
        if (isNegative && this.options.allow_negative) {
            digitsOnly = '-' + digitsOnly;
        }

        // Se vazio, mostrar zero
        if (!digitsOnly || digitsOnly === '-') {
            this.input.value = this.format(0);
            let cursorPosition = this.input.value.length;
            if (this.options.suffix) {
                cursorPosition -= this.options.suffix.length;
            }
            this.input.setSelectionRange(cursorPosition, cursorPosition);
            return;
        }

        // Converter dígitos para número decimal
        // Por exemplo: "1234" com 2 casas decimais = 12.34
        let numericValue = parseInt(digitsOnly);
        numericValue = numericValue / Math.pow(10, this.options.decimal_places);

        // Formatar e atualizar
        const formatted = this.format(numericValue);
        this.input.value = formatted;

        // Posicionar cursor após o último dígito (antes do sufixo)
        let cursorPosition = formatted.length;
        if (this.options.suffix) {
            cursorPosition -= this.options.suffix.length;
        }
        this.input.setSelectionRange(cursorPosition, cursorPosition);
    }

    /**
     * Manipula evento de keydown
     */
    handleKeydown(e) {
        // Permitir teclas de navegação e edição
        const allowedKeys = [
            'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight',
            'ArrowUp', 'ArrowDown', 'Home', 'End', 'Tab'
        ];

        if (allowedKeys.includes(e.key) || e.ctrlKey || e.metaKey) {
            return;
        }

        // Permitir números
        if (/^\d$/.test(e.key)) {
            return;
        }

        // Permitir sinal negativo no início
        if (e.key === '-' && this.options.allow_negative && this.input.selectionStart === 0) {
            return;
        }

        // Bloquear outras teclas (incluindo vírgula, já que não é necessária)
        e.preventDefault();
    }

    /**
     * Manipula evento de paste (colar)
     */
    handlePaste(e) {
        e.preventDefault();
        const pastedText = (e.clipboardData || window.clipboardData).getData('text');

        // Extrair apenas dígitos do texto colado
        let digitsOnly = pastedText.replace(/[^\d-]/g, '');

        // Garantir sinal negativo apenas no início
        const isNegative = digitsOnly.includes('-');
        digitsOnly = digitsOnly.replace(/-/g, '');
        if (isNegative && this.options.allow_negative) {
            digitsOnly = '-' + digitsOnly;
        }

        if (digitsOnly && digitsOnly !== '-') {
            let numericValue = parseInt(digitsOnly);
            numericValue = numericValue / Math.pow(10, this.options.decimal_places);
            this.input.value = this.format(numericValue);
        } else {
            this.input.value = this.format(0);
        }

        // Posicionar cursor após o último dígito (antes do sufixo)
        let cursorPosition = this.input.value.length;
        if (this.options.suffix) {
            cursorPosition -= this.options.suffix.length;
        }
        this.input.setSelectionRange(cursorPosition, cursorPosition);

        this.input.dispatchEvent(new Event('input', { bubbles: true }));
    }

    /**
     * Manipula evento de blur (perder foco)
     */
    handleBlur(e) {
        // Garantir formatação completa ao perder foco
        // O valor já está formatado pelo handleInput, apenas garantir que não está vazio
        if (!this.input.value || this.input.value.trim() === '') {
            this.input.value = this.format(0);
        }
    }

    /**
     * Manipula submit do formulário
     */
    handleSubmit(e) {
        // Converter todos os campos decimais para valor numérico
        const form = e.target;
        form.querySelectorAll('.decimal-mask').forEach(input => {
            const parsed = this.parse(input.value);

            // Criar input hidden com valor sem formatação
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = input.name + '_unmasked';
            hiddenInput.value = parsed.toString();

            form.appendChild(hiddenInput);
        });
    }

    /**
     * Remove a máscara do input
     */
    destroy() {
        this.input.classList.remove('decimal-mask');
    }

    /**
     * Método estático para formatar valor
     */
    static format(value, options = {}) {
        const mask = new DecimalMask(document.createElement('input'), options);
        return mask.format(value);
    }

    /**
     * Método estático para parsear valor
     */
    static parse(value, options = {}) {
        const mask = new DecimalMask(document.createElement('input'), options);
        return mask.parse(value);
    }
}

/**
 * Função global para aplicar máscara facilmente
 * @param {string} fieldId - ID do campo
 * @param {string} mask - Padrão da máscara
 * @param {Object} options - Opções adicionais
 * @returns {InputMask} Instância do InputMask
 */
function applyMask(fieldId, mask, options = {}) {
    const input = document.getElementById(fieldId);
    if (!input) {
        console.error(`Campo com ID "${fieldId}" não encontrado`);
        return null;
    }
    return new InputMask(input, mask, options);
}

/**
 * Inicializa automaticamente todos os campos com data-mask
 */
function initMasks() {
    document.querySelectorAll('input[data-mask]').forEach(input => {
        const mask = input.getAttribute('data-mask');
        const unmask = input.getAttribute('data-unmask') === 'true';

        // Verificar se é uma máscara pré-definida
        const maskPattern = InputMask.MASKS[mask.toUpperCase()] || mask;

        new InputMask(input, maskPattern, { unmask });
    });
}

/**
 * Inicializa automaticamente todos os campos decimais com data-decimal
 */
function initDecimalFields() {
    document.querySelectorAll('input[data-decimal]').forEach(input => {
        const options = {
            decimal_places: parseInt(input.getAttribute('data-decimal-places')) || 2,
            show_thousands: input.getAttribute('data-show-thousands') !== 'false',
            allow_negative: input.getAttribute('data-allow-negative') === 'true',
            prefix: input.getAttribute('data-decimal-prefix') || '',
            suffix: input.getAttribute('data-decimal-suffix') || ''
        };

        new DecimalMask(input, options);
    });
}

// Inicializar máscaras e campos decimais quando DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initMasks();
        initDecimalFields();
    });
} else {
    initMasks();
    initDecimalFields();
}

// Observar mudanças no DOM para inicializar máscaras e campos decimais em novos elementos
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) { // Element node
                // Verificar máscaras de padrão
                if (node.matches && node.matches('input[data-mask]')) {
                    const mask = node.getAttribute('data-mask');
                    const unmask = node.getAttribute('data-unmask') === 'true';
                    const maskPattern = InputMask.MASKS[mask.toUpperCase()] || mask;
                    new InputMask(node, maskPattern, { unmask });
                }

                // Verificar campos decimais
                if (node.matches && node.matches('input[data-decimal]')) {
                    const options = {
                        decimal_places: parseInt(node.getAttribute('data-decimal-places')) || 2,
                        show_thousands: node.getAttribute('data-show-thousands') !== 'false',
                        allow_negative: node.getAttribute('data-allow-negative') === 'true',
                        prefix: node.getAttribute('data-decimal-prefix') || '',
                        suffix: node.getAttribute('data-decimal-suffix') || ''
                    };
                    new DecimalMask(node, options);
                }

                // Verificar elementos filhos
                if (node.querySelectorAll) {
                    node.querySelectorAll('input[data-mask]').forEach(input => {
                        const mask = input.getAttribute('data-mask');
                        const unmask = input.getAttribute('data-unmask') === 'true';
                        const maskPattern = InputMask.MASKS[mask.toUpperCase()] || mask;
                        new InputMask(input, maskPattern, { unmask });
                    });

                    node.querySelectorAll('input[data-decimal]').forEach(input => {
                        const options = {
                            decimal_places: parseInt(input.getAttribute('data-decimal-places')) || 2,
                            show_thousands: input.getAttribute('data-show-thousands') !== 'false',
                            allow_negative: input.getAttribute('data-allow-negative') === 'true',
                            prefix: input.getAttribute('data-decimal-prefix') || '',
                            suffix: input.getAttribute('data-decimal-suffix') || ''
                        };
                        new DecimalMask(input, options);
                    });
                }
            }
        });
    });
});

observer.observe(document.body, { childList: true, subtree: true });

// Exportar para uso global
window.InputMask = InputMask;
window.DecimalMask = DecimalMask;
window.applyMask = applyMask;
