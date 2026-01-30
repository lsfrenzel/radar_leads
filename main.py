from flask import Flask, request, jsonify, render_template_string
from engine import MarketIntelligenceEngine
import os

app = Flask(__name__)
engine = MarketIntelligenceEngine()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de Leads SP - Inteligência de Mercado</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <style>
        :root {
            --bg-dark: #020617;
            --card-bg: #0f172a;
            --accent: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.5);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }
        body { background-color: var(--bg-dark); color: var(--text-main); font-family: 'Inter', system-ui, sans-serif; overflow-x: hidden; }
        .glass-card { background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5); backdrop-filter: blur(10px); transition: all 0.3s ease; }
        .glass-card:hover { border-color: var(--accent); }
        .hero-title { background: linear-gradient(135deg, #fff 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.5rem; }
        .btn-primary { background: var(--accent); border: none; padding: 12px 24px; border-radius: 12px; font-weight: 600; box-shadow: 0 0 20px var(--accent-glow); transition: all 0.3s; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 0 30px var(--accent-glow); background: #2563eb; }
        .form-control, .form-select { background: #1e293b; border: 1px solid #334155; color: #fff; border-radius: 10px; padding: 12px; }
        .form-control:focus, .form-select:focus { background: #1e293b; color: #fff; border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }
        
        /* Processamento Incrível */
        .loader-container { padding: 60px 0; text-align: center; }
        .cyber-loader { position: relative; width: 100px; height: 100px; margin: 0 auto 30px; }
        .cyber-loader div { position: absolute; width: 100%; height: 100%; border: 4px solid transparent; border-top-color: var(--accent); border-radius: 50%; animation: spin 1.5s linear infinite; }
        .cyber-loader div:nth-child(2) { border-top-color: #10b981; animation-duration: 2s; width: 80%; height: 80%; top: 10%; left: 10%; }
        .cyber-loader div:nth-child(3) { border-top-color: #f59e0b; animation-duration: 1s; width: 60%; height: 60%; top: 20%; left: 20%; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loading-text { font-family: 'Courier New', monospace; letter-spacing: 2px; color: var(--accent); text-transform: uppercase; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

        .table { color: var(--text-main); border-collapse: separate; border-spacing: 0 8px; }
        .table thead th { background: transparent; color: var(--text-muted); text-transform: uppercase; font-size: 0.7rem; border: none; font-weight: 700; letter-spacing: 1px; padding: 12px 20px; }
        .table tbody tr { background: rgba(255,255,255,0.02); transition: all 0.3s ease; }
        .table tbody tr:hover { background: rgba(255,255,255,0.05); transform: scale(1.005); }
        .table td { border: none; padding: 16px 20px; vertical-align: middle; }
        .table td:first-child { border-radius: 12px 0 0 12px; }
        .table td:last-child { border-radius: 0 12px 12px 0; }
        
        .trend-badge { padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; }
        .trend-up { background: rgba(16, 185, 129, 0.1); color: #10b981; }
        .trend-down { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
        .trend-stable { background: rgba(148, 163, 184, 0.1); color: #94a3b8; }
        
        .intensity-pill { display: inline-block; padding: 4px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
        .intensity-high { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
        .intensity-medium { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
        .intensity-low { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }

        .text-muted { color: #cbd5e1 !important; }
        .small.text-muted { color: #cbd5e1 !important; font-weight: 500; }
        .modal-content { background-color: var(--card-bg); color: var(--text-main); border: 1px solid rgba(255,255,255,0.1); }
        .modal-header { border-bottom: 1px solid rgba(255,255,255,0.1); }
        .modal-footer { border-top: 1px solid rgba(255,255,255,0.1); }
        .btn-close { filter: invert(1) grayscale(100%) brightness(200%); }
        .heatmap-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 15px; }
        .heatmap-cell { padding: 15px; border-radius: 8px; text-align: center; color: #fff; font-weight: bold; transition: transform 0.2s; border: 1px solid rgba(255,255,255,0.05); cursor: pointer; }
        .heatmap-cell:hover { transform: scale(1.05); }
        .heat-high { background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%); box-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }
        .heat-medium { background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%); box-shadow: 0 0 15px rgba(245, 158, 11, 0.4); }
        .heat-low { background: linear-gradient(135deg, #10b981 0%, #065f46 100%); box-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
    </style>
</head>
<body>
    <div class="container py-5">
        <div class="text-center mb-5">
            <h1 class="hero-title">Radar de Leads SP</h1>
            <p class="text-muted">Inteligência de Mercado em Tempo Real para o Estado de São Paulo</p>
        </div>
        
        <div class="glass-card p-4">
            <form id="searchForm">
                <div class="row g-3">
                    <div class="col-md-6">
                        <label class="small text-muted mb-2">O QUE VOCÊ BUSCA?</label>
                        <input type="text" class="form-control" id="product" placeholder="Ex: Energia Solar, Imóveis, IA..." required>
                    </div>
                    <div class="col-md-3">
                        <label class="small text-muted mb-2">PERÍODO</label>
                        <select class="form-select" id="days">
                            <option value="7">7 Dias</option>
                            <option value="30" selected>30 Dias</option>
                            <option value="90">90 Dias</option>
                        </select>
                    </div>
                    <div class="col-md-3 d-flex align-items-end">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-search me-2"></i>ANALISAR
                        </button>
                    </div>
                </div>
            </form>
        </div>

        <div id="results" class="mt-4"></div>
        
        <!-- Legenda do Sistema -->
        <div id="legend" class="glass-card p-4 mt-4" style="display: none;">
            <h5 class="mb-3"><i class="bi bi-info-circle"></i> Guia de Indicadores</h5>
            <div class="row g-4">
                <div class="col-md-4">
                    <h6 class="text-primary fw-bold">Demanda (%)</h6>
                    <p class="small text-muted mb-0">Representa a fatia de interesse do público naquela localidade em relação ao volume total captado no estado de São Paulo.</p>
                </div>
                <div class="col-md-4">
                    <h6 class="text-primary fw-bold">Tendência</h6>
                    <div class="d-flex align-items-center mb-1">
                        <span class="me-2">↗️ Alta:</span> <small class="text-muted">Crescimento de buscas e menções.</small>
                    </div>
                    <div class="d-flex align-items-center mb-1">
                        <span class="me-2">➡️ Estável:</span> <small class="text-muted">Volume de interesse constante.</small>
                    </div>
                    <div class="d-flex align-items-center">
                        <span class="me-2">↘️ Queda:</span> <small class="text-muted">Redução no engajamento recente.</small>
                    </div>
                </div>
                <div class="col-md-4">
                    <h6 class="text-primary fw-bold">Intensidade</h6>
                    <div class="d-flex align-items-center mb-1">
                        <span class="badge heat-high me-2" style="width: 15px; height: 15px; padding: 0;"></span> <small class="text-muted">Crítica: Intenção de compra imediata detectada.</small>
                    </div>
                    <div class="d-flex align-items-center mb-1">
                        <span class="badge heat-medium me-2" style="width: 15px; height: 15px; padding: 0;"></span> <small class="text-muted">Média: Interesse exploratório em crescimento.</small>
                    </div>
                    <div class="d-flex align-items-center">
                        <span class="badge heat-low me-2" style="width: 15px; height: 15px; padding: 0;"></span> <small class="text-muted">Baixa: Sinais iniciais ou volume orgânico estável.</small>
                    </div>
                </div>
            </div>
        </div>

        <div class="glass-card p-4 mt-4" id="exportControls" style="display: none;">
            <div class="d-flex justify-content-center gap-3">
                <button class="btn btn-outline-light" onclick="exportToExcel()">
                    <i class="bi bi-file-earmark-excel me-2"></i>Exportar Excel (.xlsx)
                </button>
                <button class="btn btn-outline-light" onclick="exportToPDF()">
                    <i class="bi bi-file-earmark-pdf me-2"></i>Exportar PDF (.pdf)
                </button>
            </div>
        </div>

        <div id="dashboard" class="row mt-4" style="display: none;">
                <div class="col-12 mb-4">
                    <div class="glass-card p-4">
                        <h4 class="mb-4 text-center"><i class="bi bi-graph-up text-primary me-2"></i>Curva de Tendência de Mercado (SP)</h4>
                        <div class="chart-container">
                            <canvas id="trendChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-12 mb-4">
                    <div class="glass-card p-4">
                        <h4 class="mb-3 text-center"><i class="bi bi-geo-alt text-primary me-2"></i>Mapa de Calor de Demanda Estratificada</h4>
                        <div id="heatmapContainer" class="heatmap-grid"></div>
                    </div>
                </div>
        </div>
    </div>

    <!-- Modal de Detalhes Estático -->
    <div class="modal fade" id="detailsModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="modalTitle">Detalhes da Fonte</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p id="modalBody"></p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
          </div>
        </div>
      </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let trendChart = null;

        let lastResults = [];

        function showDetails(city, neighborhood, details) {
            document.getElementById('modalTitle').innerText = `Fontes: ${city} - ${neighborhood}`;
            document.getElementById('modalBody').innerText = details;
            var modalEl = document.getElementById('detailsModal');
            var myModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            myModal.show();
        }

        async function exportToPDF() {
            const { jsPDF } = window.jspdf;
            const doc = jsPDF('p', 'mm', 'a4');
            const pageWidth = doc.internal.pageSize.getWidth();
            
            // Título Principal
            doc.setFillColor(15, 23, 42);
            doc.rect(0, 0, pageWidth, 40, 'F');
            doc.setTextColor(255, 255, 255);
            doc.setFontSize(22);
            doc.text("Relatório Inteligência de Mercado", 20, 25);
            doc.setFontSize(10);
            doc.text(`RADAR DE LEADS SP - Gerado em: ${new Date().toLocaleString()}`, 20, 33);
            
            let y = 55;
            
            // Capturar e adicionar gráfico de tendência
            const trendCanvas = document.getElementById('trendChart');
            const trendImg = trendCanvas.toDataURL('image/png', 1.0);
            doc.setTextColor(15, 23, 42);
            doc.setFontSize(14);
            doc.text("1. Análise de Tendência de Mercado", 20, y);
            y += 8;
            doc.addImage(trendImg, 'PNG', 20, y, 170, 80);
            y += 95;

            // Adicionar Tabela de Dados
            doc.setFontSize(14);
            doc.text("2. Intelligence Feed (Estratificado)", 20, y);
            y += 10;
            
            doc.setFontSize(9);
            doc.setTextColor(100, 116, 139);
            doc.text("CIDADE / BAIRRO", 20, y);
            doc.text("DEMANDA", 100, y);
            doc.text("TENDÊNCIA", 130, y);
            doc.text("INTENSIDADE", 160, y);
            y += 5;
            doc.setDrawColor(226, 232, 240);
            doc.line(20, y, 190, y);
            y += 8;

            doc.setTextColor(30, 41, 59);
            lastResults.forEach((item, i) => {
                if (y > 270) { doc.addPage(); y = 20; }
                doc.setFont(undefined, 'bold');
                doc.text(`${item.city} - ${item.neighborhood}`, 20, y);
                doc.setFont(undefined, 'normal');
                doc.text(`${item.demand_percentage}%`, 100, y);
                doc.text(`${item.trend.toUpperCase()}`, 130, y);
                doc.text(`${item.intensity.toUpperCase()}`, 160, y);
                y += 8;
            });

            doc.save(`radar-leads-sp-${new Date().getTime()}.pdf`);
        }

        function exportToExcel() {
            const ws = XLSX.utils.json_to_sheet(lastResults.map(r => ({
                Cidade: r.city,
                Bairro: r.neighborhood,
                Região: r.region,
                'Demanda (%)': r.demand_percentage,
                Tendência: r.trend.toUpperCase(),
                Intensidade: r.intensity.toUpperCase(),
                Fontes: r.sources
            })));

            // Aplicar estilização básica (largura das colunas)
            const wscols = [
                {wch: 20}, // Cidade
                {wch: 20}, // Bairro
                {wch: 15}, // Região
                {wch: 15}, // Demanda
                {wch: 15}, // Tendência
                {wch: 15}, // Intensidade
                {wch: 100} // Fontes
            ];
            ws['!cols'] = wscols;

            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Leads SP");
            
            // Gerar arquivo com nome datado
            XLSX.writeFile(wb, `radar-leads-sp-${new Date().getTime()}.xlsx`);
        }

        function updateDashboard(results) {
            lastResults = results;
            const dashboard = document.getElementById('dashboard');
            const legend = document.getElementById('legend');
            const exportControls = document.getElementById('exportControls');
            
            dashboard.style.display = 'flex';
            legend.style.display = 'block';
            exportControls.style.display = 'block';

            // Curva de Tendência (Simulando variação nos últimos 7 dias baseada na demanda atual)
            const labels = results.map(r => `${r.city} (${r.neighborhood})`);
            
            if (trendChart) trendChart.destroy();

            const ctxTrend = document.getElementById('trendChart').getContext('2d');
            const gradient = ctxTrend.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, 'rgba(59, 130, 246, 0.5)');
            gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');

            trendChart = new Chart(ctxTrend, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Interesse de Mercado (%)',
                        data: results.map(r => r.demand_percentage),
                        borderColor: '#3b82f6',
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.4,
                        borderWidth: 3,
                        pointBackgroundColor: '#fff',
                        pointBorderColor: '#3b82f6',
                        pointHoverRadius: 8
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, grid: { color: '#334155' }, ticks: { color: '#94a3b8' } },
                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                    },
                    plugins: { 
                        legend: { labels: { color: '#e2e8f0' } },
                        tooltip: { backgroundColor: '#1e293b', titleColor: '#fff', bodyColor: '#cbd5e1' }
                    }
                }
            });

            // Mapa de Calor Visual (Estratificado)
            const heatmapContainer = document.getElementById('heatmapContainer');
            heatmapContainer.innerHTML = '';
            results.forEach(r => {
                const cell = document.createElement('div');
                const heatClass = r.intensity === 'high' ? 'heat-high' : (r.intensity === 'medium' ? 'heat-medium' : 'heat-low');
                cell.className = `heatmap-cell ${heatClass}`;
                cell.innerHTML = `
                    <div style="font-size: 0.7rem; opacity: 0.8;">${r.city}</div>
                    <div style="font-size: 0.9rem;">${r.neighborhood}</div>
                    <div style="font-size: 1.1rem; margin-top: 5px;">${r.demand_percentage}%</div>
                `;
                cell.onclick = () => showDetails(r.city, r.neighborhood, r.sources);
                heatmapContainer.appendChild(cell);
            });
        }

        document.getElementById('searchForm').onsubmit = async (e) => {
            e.preventDefault();
            const resultsDiv = document.getElementById('results');
            document.getElementById('dashboard').style.display = 'none';
            document.getElementById('legend').style.display = 'none';
            document.getElementById('exportControls').style.display = 'none';
            
            resultsDiv.innerHTML = `
                <div class="loader-container">
                    <div class="cyber-loader">
                        <div></div><div></div><div></div>
                    </div>
                    <p class="loading-text">Iniciando Varredura SP...</p>
                    <p class="small text-muted">Processando inteligência estratificada da web</p>
                </div>
            `;
            
            const product = document.getElementById('product').value;
            const days = document.getElementById('days').value;
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ product, days: parseInt(days) })
                });
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    updateDashboard(data.results);
                    let html = `
                        <div class="glass-card p-4 mt-4">
                            <h3 class="mb-4 text-primary">Intelligence Feed: São Paulo</h3>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Cidade</th>
                                            <th>Bairro</th>
                                            <th>Região</th>
                                            <th>Demanda</th>
                                            <th>Tendência</th>
                                            <th>Intensidade</th>
                                            <th>Ação</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                    `;
                    
                    data.results.forEach((item, index) => {
                        const trendIcon = item.trend === 'up' ? '↗️' : (item.trend === 'down' ? '↘️' : '➡️');
                        const trendClass = item.trend === 'up' ? 'trend-up' : (item.trend === 'down' ? 'trend-down' : 'trend-stable');
                        const intensityClass = item.intensity === 'high' ? 'intensity-high' : (item.intensity === 'medium' ? 'intensity-medium' : 'intensity-low');
                        const sourceData = item.sources || 'Fontes baseadas em volume de busca, redes sociais e tráfego de varejo regional.';
                        
                        html += `
                            <tr>
                                <td>
                                    <div class="d-flex align-items-center">
                                        <div class="bg-primary rounded-circle me-2" style="width: 8px; height: 8px; box-shadow: 0 0 10px var(--accent);"></div>
                                        <strong>${item.city}</strong>
                                    </div>
                                </td>
                                <td>${item.neighborhood}</td>
                                <td><span class="text-muted small">${item.region}</span></td>
                                <td class="fw-bold text-primary">${item.demand_percentage}%</td>
                                <td>
                                    <span class="trend-badge ${trendClass}">
                                        ${trendIcon} ${item.trend === 'up' ? 'Alta' : (item.trend === 'down' ? 'Queda' : 'Estável')}
                                    </span>
                                </td>
                                <td>
                                    <span class="intensity-pill ${intensityClass}">
                                        ${item.intensity}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-info btn-details border-0" 
                                            data-city="${item.city}" 
                                            data-neighborhood="${item.neighborhood}" 
                                            data-sources="${sourceData.replace(/"/g, '&quot;')}">
                                        <i class="bi bi-eye"></i>
                                    </button>
                                </td>
                            </tr>
                        `;
                    });
                    
                    html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;
                    resultsDiv.innerHTML = html;

                    document.querySelectorAll('.btn-details').forEach(btn => {
                        btn.onclick = function() {
                            showDetails(this.dataset.city, this.dataset.neighborhood, this.dataset.sources);
                        };
                    });
                } else {
                    resultsDiv.innerHTML = '<div class="alert alert-info">Nenhuma intenção clara detectada para este produto no período.</div>';
                }
            } catch (err) {
                resultsDiv.innerHTML = '<div class="alert alert-danger">Erro ao processar análise. Verifique os logs.</div>';
            }
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        product = data.get('product')
        days = data.get('days', 30)
        
        if not product:
            return jsonify({"error": "Product is required"}), 400
            
        results = engine.run_intelligence(product, days=days)
        return jsonify({"results": results})
    except Exception as e:
        print(f"Erro na rota /analyze: {e}")
        return jsonify({"error": str(e), "results": []}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
