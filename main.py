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
        .chart-container { position: relative; height: 300px; width: 100%; }
        h1, h3 { font-weight: 700; letter-spacing: -0.025em; color: #f8fafc; }
        .badge-demand { font-size: 0.8rem; padding: 0.5em 0.8em; border-radius: 6px; }
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
        <div id="dashboard" class="row mt-4" style="display: none;">
            <div class="col-md-6">
                <div class="card p-4">
                    <h4 class="mb-3 text-center">Distribuição de Demanda</h4>
                    <div class="chart-container">
                        <canvas id="demandChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card p-4">
                    <h4 class="mb-3 text-center">Intensidade por Localidade</h4>
                    <div class="chart-container">
                        <canvas id="intensityChart"></canvas>
                    </div>
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
        let demandChart = null;
        let intensityChart = null;

        function showDetails(city, neighborhood, details) {
            document.getElementById('modalTitle').innerText = `Fontes: ${city} - ${neighborhood}`;
            document.getElementById('modalBody').innerText = details;
            var modalEl = document.getElementById('detailsModal');
            var myModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            myModal.show();
        }

        function updateDashboard(results) {
            const dashboard = document.getElementById('dashboard');
            dashboard.style.display = 'flex';

            const labels = results.map(r => `${r.city} (${r.neighborhood})`);
            const demandData = results.map(r => r.demand_percentage);
            const intensityMap = { 'high': 3, 'medium': 2, 'low': 1 };
            const intensityData = results.map(r => intensityMap[r.intensity] || 0);

            if (demandChart) demandChart.destroy();
            if (intensityChart) intensityChart.destroy();

            const ctxDemand = document.getElementById('demandChart').getContext('2d');
            demandChart = new Chart(ctxDemand, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: demandData,
                        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316'],
                        borderWidth: 0
                    }]
                },
                options: { maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0' } } } }
            });

            const ctxIntensity = document.getElementById('intensityChart').getContext('2d');
            intensityChart = new Chart(ctxIntensity, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Nível de Intensidade',
                        data: intensityData,
                        backgroundColor: '#3b82f6',
                        borderRadius: 8
                    }]
                },
                options: {
                    maintainAspectRatio: false,
                    scales: {
                        y: { beginAtZero: true, max: 3, ticks: { stepSize: 1, color: '#94a3b8', callback: v => ['','LOW','MEDIUM', 'HIGH'][v] } },
                        x: { ticks: { color: '#94a3b8' } }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }

        document.getElementById('searchForm').onsubmit = async (e) => {
            e.preventDefault();
            const resultsDiv = document.getElementById('results');
            document.getElementById('dashboard').style.display = 'none';
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
