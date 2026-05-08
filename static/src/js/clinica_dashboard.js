(function () {
    "use strict";

    // Variáveis para controlar renderização dos gráficos
    let dashboardInicializado = false;
    let chartLinha = null;
    let chartRosca = null;

    // Tenta renderizar os dados ao carregar ou navegar pelo Odoo (SPA)
    document.addEventListener("click", () => setTimeout(verificarDashboard, 100));
    document.addEventListener("DOMContentLoaded", verificarDashboard);
    setTimeout(verificarDashboard, 1000); // Carregamento inicial de segurança

    function verificarDashboard() {
        const kpiFaturamento = document.getElementById("kpi_faturamento");
        // Se os elementos não existirem na página atual, reseta o estado
        if (!kpiFaturamento) {
            dashboardInicializado = false;
            return;
        }
        if (dashboardInicializado) return;
        
        dashboardInicializado = true;
        carregarDadosDashboard();
    }

    async function carregarDadosDashboard() {
        try {
            // Realiza uma chamada JSON-RPC para o método no Python (backend)
            const response = await fetch("/web/dataset/call_kw", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    id: Math.floor(Math.random() * 1000000),
                    method: "call",
                    params: {
                        model: "clinica.dashboard",
                        method: "get_dashboard_data",
                        args: [],
                        kwargs: {}
                    }
                })
            });
            
            const data = await response.json();
            if (data.result) {
                atualizarTela(data.result);
            }
        } catch (error) {
            console.error("Erro ao carregar os dados do Dashboard:", error);
        }
    }

    function atualizarTela(dados) {
        // 1. Atualizar Blocos de Indicadores (KPIs)
        const faturamentoEl = document.getElementById("kpi_faturamento");
        if(faturamentoEl) {
            faturamentoEl.innerText = dados.kpis.faturamento_total.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            document.getElementById("kpi_produtos").innerText = dados.kpis.vendas_produtos;
            document.getElementById("kpi_procedimentos").innerText = dados.kpis.procedimentos;
            document.getElementById("kpi_agendamentos").innerText = dados.kpis.agendamentos_hoje;
        }

        // Tira o tracejado de layout do HTML original
        document.getElementById("chart_vendas_line").style.border = "none";
        document.getElementById("chart_vendas_donut").style.border = "none";

        // 2. Montar Gráfico de Evolução de Vendas (Linha)
        const ctxLine = document.getElementById('canvas_vendas_line');
        if (ctxLine && window.Chart) {
            if(chartLinha) chartLinha.destroy();
            chartLinha = new window.Chart(ctxLine, {
                type: 'line',
                data: {
                    labels: dados.charts.linha_datas,
                    datasets: [{
                        label: 'Vendas Diárias (R$)',
                        data: dados.charts.linha_valores,
                        borderColor: '#714B67',
                        backgroundColor: 'rgba(113, 75, 103, 0.2)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // 3. Montar Gráfico de Mix de Receita (Rosca)
        const ctxDonut = document.getElementById('canvas_vendas_donut');
        if (ctxDonut && window.Chart) {
            if(chartRosca) chartRosca.destroy();
            chartRosca = new window.Chart(ctxDonut, {
                type: 'doughnut',
                data: {
                    labels: ['Produtos', 'Serviços'],
                    datasets: [{
                        data: dados.charts.mix_receita,
                        backgroundColor: ['#28a745', '#17a2b8'],
                        hoverOffset: 4
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    }
})();