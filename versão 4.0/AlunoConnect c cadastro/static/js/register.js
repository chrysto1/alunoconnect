// tela de cadastro | register.js 

// Preencher os campos de data de nascimento
document.addEventListener('DOMContentLoaded', function() {
    // Selects
    const daySelect = document.querySelector('select[name="day"]');
    const monthSelect = document.querySelector('select[name="month"]');
    const yearSelect = document.querySelector('select[name="year"]');

    //  (1-31)
    daySelect.innerHTML = '<option value="">Dia</option>';
    for (let i = 1; i <= 31; i++) {
        daySelect.innerHTML += `<option value="${i}">${i}</option>`;
    }

    // Preencher meses
    const months = [
        'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ];
    monthSelect.innerHTML = '<option value="">Mês</option>';
    months.forEach((month, index) => {
        monthSelect.innerHTML += `<option value="${index + 1}">${month}</option>`;
    });

    // Preencher anos (100 anos atrás até o ano atual)
    const currentYear = new Date().getFullYear();
    yearSelect.innerHTML = '<option value="">Ano</option>';
    for (let i = currentYear; i >= currentYear - 100; i--) {
        yearSelect.innerHTML += `<option value="${i}">${i}</option>`;
    }
});

// Inicializar todos os tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});

// Controle do gênero personalizado
document.addEventListener('DOMContentLoaded', function() {
    const customGenderDiv = document.querySelector('.custom-gender');
    const genderRadios = document.querySelectorAll('input[name="gender"]');

    genderRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            customGenderDiv.style.display = this.value === 'personalizado' ? 'block' : 'none';
        });
    });
});

// Lista de países com códigos e bandeiras
const countries = [
    { code: '+55', flag: '🇧🇷', name: 'Brasil' },
    { code: '+351', flag: '🇵🇹', name: 'Portugal' },
    { code: '+1', flag: '🇺🇸', name: 'Estados Unidos' },
    { code: '+44', flag: '🇬🇧', name: 'Reino Unido' },
    { code: '+34', flag: '🇪🇸', name: 'Espanha' },
    { code: '+33', flag: '🇫🇷', name: 'França' },
    { code: '+49', flag: '🇩🇪', name: 'Alemanha' },
    { code: '+39', flag: '🇮🇹', name: 'Itália' },
    { code: '+81', flag: '🇯🇵', name: 'Japão' },
    { code: '+86', flag: '🇨🇳', name: 'China' },
    { code: '+7', flag: '🇷🇺', name: 'Rússia' },
    { code: '+82', flag: '🇰🇷', name: 'Coreia do Sul' },
    { code: '+91', flag: '🇮🇳', name: 'Índia' },
    { code: '+52', flag: '🇲🇽', name: 'México' },
    { code: '+54', flag: '🇦🇷', name: 'Argentina' },
    { code: '+56', flag: '🇨🇱', name: 'Chile' },
    { code: '+57', flag: '🇨🇴', name: 'Colômbia' },
    { code: '+58', flag: '🇻🇪', name: 'Venezuela' },
    { code: '+61', flag: '🇦🇺', name: 'Austrália' },
    { code: '+64', flag: '🇳🇿', name: 'Nova Zelândia' },
    { code: '+27', flag: '🇿🇦', name: 'África do Sul' },
    { code: '+20', flag: '🇪🇬', name: 'Egito' },
    { code: '+212', flag: '🇲🇦', name: 'Marrocos' },
    { code: '+234', flag: '🇳🇬', name: 'Nigéria' },
    { code: '+30', flag: '🇬🇷', name: 'Grécia' },
    { code: '+31', flag: '🇳🇱', name: 'Países Baixos' },
    { code: '+32', flag: '🇧🇪', name: 'Bélgica' },
    { code: '+36', flag: '🇭🇺', name: 'Hungria' },
    { code: '+40', flag: '🇷🇴', name: 'Romênia' },
    { code: '+41', flag: '🇨🇭', name: 'Suíça' },
    { code: '+43', flag: '🇦🇹', name: 'Áustria' },
    { code: '+45', flag: '🇩🇰', name: 'Dinamarca' },
    { code: '+46', flag: '🇸🇪', name: 'Suécia' },
    { code: '+47', flag: '🇳🇴', name: 'Noruega' },
    { code: '+48', flag: '🇵🇱', name: 'Polônia' },
    { code: '+353', flag: '🇮🇪', name: 'Irlanda' },
    { code: '+358', flag: '🇫🇮', name: 'Finlândia' },
    { code: '+420', flag: '🇨🇿', name: 'República Tcheca' },
    { code: '+380', flag: '🇺🇦', name: 'Ucrânia' },
    { code: '+972', flag: '🇮🇱', name: 'Israel' }
].sort((a, b) => a.name.localeCompare(b.name));

document.addEventListener('DOMContentLoaded', function() {
    const countrySelect = document.getElementById('country-select');
    
    // Preenche o select com os países
    countries.forEach(country => {
        const option = document.createElement('option');
        option.value = country.code;
        option.innerHTML = `${country.flag} ${country.code} - ${country.name}`;
        countrySelect.appendChild(option);
    });

    // Define Brasil como padrão
    countrySelect.value = '+55';
});

// Adicione após o código existente
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const countrySelect = document.getElementById('country-select');
    const phoneInput = document.getElementById('phone-input');
    const fullPhoneInput = document.getElementById('full-phone');

    form.addEventListener('submit', function(e) {
        // Combina o código do país com o número do telefone
        const fullPhone = countrySelect.value + phoneInput.value;
        fullPhoneInput.value = fullPhone;
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const daySelect = document.querySelector('select[name="day"]');
    const monthSelect = document.querySelector('select[name="month"]');
    const yearSelect = document.querySelector('select[name="year"]');
    const fullBirthdateInput = document.getElementById('full-birthdate');

    form.addEventListener('submit', function(e) {
        // Formata a data completa (YYYY-MM-DD)
        if (daySelect.value && monthSelect.value && yearSelect.value) {
            const day = daySelect.value.padStart(2, '0');
            const month = monthSelect.value.padStart(2, '0');
            const fullBirthdate = `${yearSelect.value}-${month}-${day}`;
            fullBirthdateInput.value = fullBirthdate;
        }
    });
});