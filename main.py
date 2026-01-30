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
    <title>Radar de Leads - Inteligência de Mercado</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #0f172a; color: #e2e8f0; font-family: 'Inter', sans-serif; }
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-bottom: 24px; }
        .table { color: #e2e8f0; }
        .table-light { background-color: #334155; color: #f8fafc; border-color: #475569; }
        .table-hover tbody tr:hover { background-color: #334155; color: #fff; }
        .btn-primary { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); border: none; }
        .spinner-border { color: #3b82f6; }
        .chart-container { position: relative; height: 400px; width: 100%; }
        h1, h3 { font-weight: 700; letter-spacing: -0.025em; color: #f8fafc; }
        .heatmap-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 10px; margin-top: 20px; }
        .heatmap-cell { padding: 15px; border-radius: 8px; text-align: center; color: #fff; font-weight: bold; transition: transform 0.2s; }
        .heatmap-cell:hover { transform: scale(1.05); }
        .heat-high { background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%); box-shadow: 0 0 15px rgba(239, 68, 68, 0.4); }
        .heat-medium { background: linear-gradient(135deg, #f59e0b 0%, #b45309 100%); box-shadow: 0 0 15px rgba(245, 158, 11, 0.4); }
        .heat-low { background: linear-gradient(135deg, #10b981 0%, #065f46 100%); box-shadow: 0 0 15px rgba(16, 185, 129, 0.4); }
    </style>
</head>
<body>
    <div class="container py-5">
        <h1 class="text-center mb-4">Radar de Leads Brasil</h1>
        <div class="card p-4">
            <form id="searchForm">
                <div class="row g-3">
                    <div class="col-md-6">
                        <input type="text" class="form-control" id="product" placeholder="Produto ou Serviço (ex: Solar Energy)" required>
                    </div>
                    <div class="col-md-3">
                        <select class="form-select" id="days">
                            <option value="7">Últimos 7 dias</option>
                            <option value="30" selected>Últimos 30 dias</option>
                            <option value="90">Últimos 90 dias</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-primary w-100">Analisar Mercado</button>
                    </div>
                </div>
            </form>
        </div>

        <div id="results" class="mt-4"></div>
        
        <!-- Legenda do Sistema -->
        <div id="legend" class="card p-4 mt-4" style="display: none;">
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

        <div id="dashboard" class="row mt-4" style="display: none;">
            <div class="col-12 mb-4">
                <div class="card p-4">
                    <h4 class="mb-4 text-center"><i class="bi bi-graph-up"></i> Curva de Tendência de Mercado (SP)</h4>
                    <div class="chart-container">
                        <canvas id="trendChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-12 mb-4">
                <div class="card p-4">
                    <h4 class="mb-3 text-center"><i class="bi bi-geo-alt"></i> Mapa de Calor de Demanda Estratificada</h4>
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

        function showDetails(city, neighborhood, details) {
            document.getElementById('modalTitle').innerText = `Fontes: ${city} - ${neighborhood}`;
            document.getElementById('modalBody').innerText = details;
            var modalEl = document.getElementById('detailsModal');
            var myModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            myModal.show();
        }

        function updateDashboard(results) {
            const dashboard = document.getElementById('dashboard');
            const legend = document.getElementById('legend');
            dashboard.style.display = 'flex';
            legend.style.display = 'block';

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
            resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div><p class="mt-2">Escaneando a web e processando inteligência estratificada...</p></div>';
            
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
                        <div class="card p-4">
                            <h3 class="mb-4">Inteligência de Mercado: São Paulo</h3>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr class="table-light">
                                            <th>Cidade</th>
                                            <th>Bairro/Distrito</th>
                                            <th>Região</th>
                                            <th>Demanda (%)</th>
                                            <th>Tendência</th>
                                            <th>Intensidade</th>
                                            <th>Ações</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                    `;
                    
                    data.results.forEach((item, index) => {
                        const trendIcon = item.trend === 'up' ? '↗️' : (item.trend === 'down' ? '↘️' : '➡️');
                        const intensityClass = item.intensity === 'high' ? 'text-danger' : (item.intensity === 'medium' ? 'text-warning' : 'text-success');
                        const sourceData = item.sources || 'Fontes baseadas em volume de busca, redes sociais e tráfego de varejo regional.';
                        
                        html += `
                            <tr>
                                <td><strong>${item.city}</strong></td>
                                <td>${item.neighborhood}</td>
                                <td><small class="text-muted">${item.region}</small></td>
                                <td class="fw-bold text-primary">${item.demand_percentage}%</td>
                                <td>${trendIcon} ${item.trend === 'up' ? 'Alta' : (item.trend === 'down' ? 'Queda' : 'Estável')}</td>
                                <td class="${intensityClass} fw-bold">${item.intensity.toUpperCase()}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-info btn-details" 
                                            data-city="${item.city}" 
                                            data-neighborhood="${item.neighborhood}" 
                                            data-sources="${sourceData.replace(/"/g, '&quot;')}">
                                        Detalhes
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
