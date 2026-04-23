/** @odoo-module **/

// Usamos uma função autoinvocável ou garantimos o escopo global de forma segura
(function () {
    "use strict";

    window.enviarMensagem = function () {
        const input = document.getElementById("chat-input");
        const chat = document.getElementById("chat-messages");
        
        if (!input || !chat) return;

        const mensagem = input.value.trim();
        if (!mensagem) return;

        // 1. Adiciona a mensagem do usuário na tela (alinhada à direita)
        const userDiv = document.createElement("div");
        userDiv.style.cssText = "align-self: flex-end; background: #714B67; color: white; padding: 8px 12px; border-radius: 15px; max-width: 80%; margin-bottom: 5px;";
        userDiv.innerHTML = `<b>Você:</b> ${mensagem}`;
        chat.appendChild(userDiv);

        // Limpa o input e rola para o fim
        input.value = "";
        chat.scrollTop = chat.scrollHeight;

        // 2. Chamada ao Webhook do Chatbot (Rasa/Outros)
        fetch("http://127.0.0.1:5005/webhooks/rest/webhook", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sender: "user_odoo",
                message: mensagem
            })
        })
        .then(res => {
            if (!res.ok) throw new Error("Erro na rede");
            return res.json();
        })
        .then(data => {
            data.forEach(msg => {
                // 3. Adiciona a resposta do Bot (alinhada à esquerda)
                const botDiv = document.createElement("div");
                botDiv.style.cssText = "align-self: flex-start; background: #e2e2e2; color: #333; padding: 8px 12px; border-radius: 15px; max-width: 80%; margin-bottom: 5px;";
                botDiv.innerHTML = `<b>Bot:</b> ${msg.text}`;
                chat.appendChild(botDiv);
            });
            chat.scrollTop = chat.scrollHeight;
        })
        .catch(err => {
            console.error("Erro no Chatbot:", err);
            const errorDiv = document.createElement("div");
            errorDiv.style.cssText = "color: red; font-size: 0.8rem; text-align: center;";
            errorDiv.innerText = "Erro ao conectar com o assistente.";
            chat.appendChild(errorDiv);
        });
    };

    // Permite enviar a mensagem ao apertar "Enter"
    document.addEventListener("keypress", function (e) {
        if (e.key === "Enter" && document.activeElement.id === "chat-input") {
            window.enviarMensagem();
        }
    });

})();