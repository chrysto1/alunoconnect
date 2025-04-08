document.getElementById("publicacao_texto").addEventListener("submit", async function(event) {
    event.preventDefault();

    const conteudo = document.getElementById("conteudo").value;

    // Simples validação/sanitização contra scripts maliciosos
    if (/<script.*?>.*?<\/script>/gi.test(conteudo)) {
        alert("Conteúdo inválido! Scripts maliciosos não são permitidos.");
        return;
    }

    // Enviando dados sanitizados para o backend
    try {
        const response = await fetch("/processar_dados", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ conteudo })
        });

        if (response.ok) {
            location.reload();
        } else {
            alert("Erro ao publicar.");
        }
    } catch (error) {
        console.error("Erro ao enviar os dados:", error);
    }
});