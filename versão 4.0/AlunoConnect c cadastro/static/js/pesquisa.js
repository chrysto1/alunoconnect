// Selecionar o campo de entrada de texto e escutar o evento "input"
document.getElementById("pesquisar").addEventListener("input", async function () {
    const query = this.value; // Obtém o valor digitado pelo usuário
    const url = `/pesquisanado?query=${encodeURIComponent(query)}`; // Constrói a URL com o parâmetro atualizado

    try {
        const response = await fetch(url); // Faz a requisição GET para o backend
        if (!response.ok) {
            throw new Error("Erro na resposta do servidor"); // Trata erros de resposta
        }

        const resultados = await response.json(); // Converte a resposta para JSON

        // Atualiza a interface com os novos resultados
        const resultadosContainer = document.getElementById("resultados");
        resultadosContainer.innerHTML = ""; // Limpa resultados antigos

        resultados.forEach(resultado => {
            const item = document.createElement("div"); // Cria um elemento para cada resultado
            item.textContent = resultado.nome; // Define o nome do usuário no texto do elemento
            resultadosContainer.appendChild(item); // Adiciona o item ao contêiner de resultados
        });
    } catch (error) {
        console.error("Erro ao buscar resultados:", error);
    }
});

// Evento para ocultar a filtragem quando clicar fora da div de resultados
document.addEventListener("click", function (event) {
    const pesquisarInput = document.getElementById("pesquisar");
    const resultadosContainer = document.getElementById("resultados");

    // Verifica se o clique foi fora do campo de pesquisa e da div de resultados
    if (!pesquisarInput.contains(event.target) && !resultadosContainer.contains(event.target)) {
        resultadosContainer.style.display = "none"; // Oculta a div
    }
});