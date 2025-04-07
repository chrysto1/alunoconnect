// Script para habilitar o botão de publicar quando o texto for digitado
document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.querySelector('.post-content textarea');
    const publishBtn = document.querySelector('.publish-btn');

    textarea.addEventListener('input', function() {
        publishBtn.disabled = !this.value.trim();
    });
});

// Script para o botão de voltar ao topo
document.addEventListener('DOMContentLoaded', function() {
    const scrollToTop = document.getElementById('scrollToTop');
    let lastScrollPosition = 0;
    
    // Mostrar/ocultar o botão baseado na direção do scroll
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        // Mostrar botão quando rolar para baixo e estiver além de 200px
        if (currentScroll > 200 && currentScroll > lastScrollPosition) {
            scrollToTop.classList.add('visible');
        } else {
            scrollToTop.classList.remove('visible');
        }
        
        lastScrollPosition = currentScroll;
    });
    
    // Rolar para o topo quando clicar no botão
    scrollToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});