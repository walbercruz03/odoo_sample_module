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
                body: JSON.stringify({ jsonrpc: "2.0", id: Math.floor(Math.random() * 1000000), params: params })
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
        const result = await jsonRpc("/mail/chat_history", {
            uuid: chatUuid,
            limit: 30
        });

        if (result && result.length > 0) {
            [...result].reverse().forEach(msg => {
                // Se a mensagem tem um ID maior que o último que vimos
                if (msg.id > lastMessageId) {
                    // Verificamos se quem enviou NÃO foi o autor da sessão (você)
                    // No Odoo, mensagens do Bot geralmente não trazem o nome 'Visitante'
                    if (!msg.author_id || (Array.isArray(msg.author_id) && !msg.author_id[1].includes("Visitante"))) {
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
    if (!input) {
        console.error("ERRO BOT: Elemento com id 'chat-input' não foi encontrado no seu XML!");
        return;
    }

    const mensagem = input.value.trim();
    if (!mensagem) return;

    adicionarMensagemTela(mensagem, "Você");
    input.value = "";

    // === LÓGICA DE ASSISTENTE VIRTUAL DA PLATAFORMA (FAQ) ===
    const textoMin = mensagem.toLowerCase();
    let respostaBot = "";

    if (textoMin.includes("cadastrar cliente") || textoMin.includes("novo cliente") || textoMin.includes("clientes")) {
        respostaBot = "Para cadastrar um <b>Cliente</b>, vá no menu principal em <b>Clientes</b> e clique em <b>Novo</b>. Lá você poderá preencher os dados pessoais e marcar as opções de Perfil (VIP, Convênio ou Cliente Novo).";
    } else if (textoMin.includes("cadastrar produto") || textoMin.includes("novo produto") || textoMin.includes("produtos")) {
        respostaBot = "Para cadastrar um <b>Produto ou Serviço</b>, navegue até a aba de <b>Produtos</b> e clique em <b>Novo</b>. Lembre-se de criar também as 'Regras de Preço' e os 'Preços Base' para ativar a vigência!";
    } else if (textoMin.includes("pedido") || textoMin.includes("venda")) {
        respostaBot = "Para fazer um pedido, vá na tela de <b>Pedidos</b> e clique em <b>Novo</b>. Ao adicionar os itens ao carrinho, o preço correto e os descontos (como promoções de perfis e combinações) serão aplicados automaticamente pelo sistema.";
    } else if (textoMin.includes("ajuda") || textoMin.includes("como usar") || textoMin.includes("olá") || textoMin.includes("oi")) {
        respostaBot = "Olá! Eu sou o Assistente Inteligente da Clínica. Como posso ajudar? Você pode me perguntar como cadastrar <b>Clientes</b>, <b>Produtos</b> ou <b>Pedidos</b>.";
    }

    if (respostaBot) {
        // Se o bot sabe responder, simula um "digitando" e injeta a mensagem na tela
        setTimeout(() => {
            adicionarMensagemTela(respostaBot, "Assistente Virtual");
        }, 600);
        return; // Interrompe a execução aqui para não enviar para o servidor Odoo
    }
    // ==========================================================

    try {
        if (!chatUuid) {
            // Tentativa com context explícito, que muitas vezes é exigido pelo Odoo backend
            const session = await jsonRpc("/im_livechat/get_session", {
                channel_id: 2, // Ajustado para bater com o canal importado no XML
                anonymous_name: "Visitante Clínica",
                previous_operator_id: false,
                context: {} // Removido hardcode do script para evitar falha fatal de UUID nulo
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

        await jsonRpc("/im_livechat/chat_post", {
            uuid: chatUuid,
            message_content: mensagem
        });

    } catch (err) {
        console.error("Erro na comunicação:", err);
    }
};

    function adicionarMensagemTela(texto, autor) {
        const chat = document.getElementById("chat-messages");
        if (!chat) {
            console.error("ERRO BOT: Elemento com id 'chat-messages' não foi encontrado no seu XML!");
            return;
        }

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

    // === DELEGAÇÃO DE EVENTOS PARA COMPATIBILIDADE COM ODOO SPA ===
    // O Odoo remove atributos 'onclick' do XML por segurança.
    // Esta delegação captura o evento no documento inteiro.
    document.addEventListener('click', function (e) {
        // Verifica com segurança se closest existe no target antes de chamar
        const btnEnviar = (e.target && e.target.closest) ? e.target.closest('#btn-enviar') : null;
        if (btnEnviar) {
            e.preventDefault(); // Impede o botão de tentar recarregar a tela/form
            window.enviarMensagem();
        }
        
        // Verifica se clicou no botão de minimizar/maximizar
        const btnMinimizar = (e.target && e.target.closest) ? e.target.closest('#btn-minimizar') : null;
        if (btnMinimizar) {
            e.preventDefault();
            const chatMessages = document.getElementById('chat-messages');
            const chatFooter = document.getElementById('chat-footer');
            
            if (chatMessages.style.display === 'none') {
                chatMessages.style.display = 'flex'; // Volta para o display padrão da caixa
                chatFooter.style.display = 'block';
                btnMinimizar.classList.replace('fa-plus', 'fa-minus');
            } else {
                chatMessages.style.display = 'none'; // Esconde as mensagens
                chatFooter.style.display = 'none'; // Esconde o campo de texto
                btnMinimizar.classList.replace('fa-minus', 'fa-plus'); // Troca o ícone para um "+"
            }
        }
    });
    document.addEventListener('keypress', function (e) {
        if (e.key === 'Enter' && e.target && e.target.id === 'chat-input') {
            window.enviarMensagem();
        }
    });
})();