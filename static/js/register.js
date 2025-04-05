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
    const genderInputs = document.querySelectorAll('input[name="gender"]');

    genderInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value === 'personalizado') {
                customGenderDiv.style.display = 'block';
            } else {
                customGenderDiv.style.display = 'none';
            }
        });
    });
});