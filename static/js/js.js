const dropdownToggle = document.querySelector('.dropdown-toggle');
const dropdownMenu = document.querySelector('.dropdown-menu');

dropdownToggle.addEventListener('click', () => {
  const isMenuOpen = dropdownMenu.style.display === 'block';
  dropdownMenu.style.display = isMenuOpen ? 'none' : 'block';
});

document.addEventListener('click', (event) => {
  if (!event.target.closest('.dropdown')) {
    dropdownMenu.style.display = 'none';
  }
});


return redirect(url_for('homepage', mensagem='CADASTRADO'))