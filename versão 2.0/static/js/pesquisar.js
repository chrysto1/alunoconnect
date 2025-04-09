document.getElementById('pesquisar').addEventListener('input', function () {
    const pesquisa = this.value;

    fetch(`/pesquisanado?query=${pesquisa}`)
        .then(response => response.json())
        .then(data => {
            const resultado = document.getElementById('resultado');
            resultado.innerHTML = ''; // Limpa resultados anteriores

            data.forEach(user => {
                resultado.innerHTML += `<div>${user.nome}</div>`;
            });
        })
        .catch(error => console.error('Erro:', error));
});
