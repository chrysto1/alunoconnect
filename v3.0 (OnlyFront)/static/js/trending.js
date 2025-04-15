document.addEventListener('DOMContentLoaded', function() {
    const showMoreButton = document.getElementById('showMoreTrending');
    const hiddenItems = document.querySelectorAll('.trending-item.hidden');
    let isExpanded = false;

    showMoreButton.addEventListener('click', function() {
        hiddenItems.forEach(item => {
            item.classList.toggle('hidden');
        });
        
        isExpanded = !isExpanded;
        showMoreButton.classList.toggle('active');
        showMoreButton.innerHTML = isExpanded ? 
            'Exibir menos <i class="fas fa-chevron-down"></i>' : 
            'Exibir mais <i class="fas fa-chevron-down"></i>';
    });
});