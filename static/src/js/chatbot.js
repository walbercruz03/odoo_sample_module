/** @odoo-module **/

(function () {
    "use strict";

    let chatUuid = null;
    let lastMessageId = 0;

    async function jsonRpc(url, params) {
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ jsonrpc: "2.0", params: params })
            });
            const data = await response.json();
            if (data.error) {
                console.error("Erro RPC:", data.error);
                return null;
            }
            return data.result;
        } catch (e) {
            console.error("Falha na conexão:", e);
            return null;
        }
    }

    async function escutarBot() {
    if (!chatUuid) return;
    try {
        const result = await jsonRpc("/im_livechat/get_messages", {
            uuid: chatUuid,
            last_id: lastMessageId
        });

        if (result && result.length > 0) {
            result.forEach(msg => {
                // Se a mensagem tem um ID maior que o último que vimos
                if (msg.id > lastMessageId) {
                    // Verificamos se quem enviou NÃO foi o autor da sessão (você)
                    // No Odoo, mensagens do Bot geralmente não trazem o nome 'Visitante'
                    if (!msg.author_id[1].includes("Visitante")) {
                        const tempDiv = document.createElement("div");
                        tempDiv.innerHTML = msg.body;
                        const cleanText = tempDiv.textContent || tempDiv.innerText || "";
                        
                        adicionarMensagemTela(cleanText, "Bot");
                    }
                    lastMessageId = msg.id;
                }
            });
        }
    } catch (e) { console.error("Erro na escuta:", e); }
    setTimeout(escutarBot, 1500); // Diminuí para 1.5s para ser mais rápido
}

    window.enviarMensagem = async function () {
    const input = document.getElementById("chat-input");
    const mensagem = input?.value.trim();
    if (!mensagem) return;

    adicionarMensagemTela(mensagem, "Você");
    input.value = "";

    try {
        if (!chatUuid) {
            // Tentativa com context explícito, que muitas vezes é exigido pelo Odoo backend
            const session = await jsonRpc("/im_livechat/get_session", {
                channel_id: 2,
                anonymous_name: "Visitante Clínica",
                previous_operator_id: false,
                context: { chatbot_script_id: 2 } // MUDOU DE 1 PARA 2
            });
            console.log("Resposta bruta do Odoo:", session); // ISSO VAI MOSTRAR O ERRO REAL

            if (session && session.uuid) {
                chatUuid = session.uuid;
                escutarBot();
                await new Promise(r => setTimeout(r, 600));
            } else {
                console.error("Odoo não gerou UUID. Verifique se o canal 2 tem regras de Chatbot ativas.");
                return;
            }
        }

        await jsonRpc("/mail/chat_post", {
            uuid: chatUuid,
            message_content: mensagem
        });

    } catch (err) {
        console.error("Erro na comunicação:", err);
    }
};

    function adicionarMensagemTela(texto, autor) {
        const chat = document.getElementById("chat-messages");
        if (!chat) return;

        const msgDiv = document.createElement("div");
        const isUser = autor === "Você";
        
        msgDiv.style.cssText = `
            align-self: ${isUser ? 'flex-end' : 'flex-start'};
            background: ${isUser ? '#714B67' : '#f1f1f1'};
            color: ${isUser ? 'white' : '#333'};
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 85%;
            margin-bottom: 10px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            font-size: 0.95rem;
            line-height: 1.4;
        `;
        
        msgDiv.innerHTML = `<strong>${autor}:</strong> ${texto}`;
        chat.appendChild(msgDiv);
        
        // Rola suavemente para a última mensagem
        chat.scrollTo({ top: chat.scrollHeight, behavior: 'smooth' });
    }
})();