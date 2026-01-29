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
    <style>
        body { background-color: #f8f9fa; }
        .card { margin-bottom: 20px; border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .intent-high { color: #198754; font-weight: bold; }
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
    </div>

    <script>
        document.getElementById('searchForm').onsubmit = async (e) => {
            e.preventDefault();
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p>Escaneando a web e processando intenções...</p></div>';
            
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
                    let html = `
                        <div class="card p-4">
                            <h3 class="mb-4">Inteligência de Mercado: São Paulo (Estratificado)</h3>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead class="table-light">
                                        <tr>
                                            <th>Cidade</th>
                                            <th>Bairro/Distrito</th>
                                            <th>Região</th>
                                            <th>Demanda (%)</th>
                                            <th>Tendência</th>
                                            <th>Intensidade</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                    `;
                    
                    data.results.forEach(item => {
                        const trendIcon = item.trend === 'up' ? '↗️' : (item.trend === 'down' ? '↘️' : '➡️');
                        const intensityClass = item.intensity === 'high' ? 'text-danger' : (item.intensity === 'medium' ? 'text-warning' : 'text-success');
                        
                        html += `
                            <tr>
                                <td><strong>${item.city}</strong></td>
                                <td>${item.neighborhood}</td>
                                <td><small class="text-muted">${item.region}</small></td>
                                <td class="fw-bold text-primary">${item.demand_percentage}%</td>
                                <td>${trendIcon} ${item.trend === 'up' ? 'Alta' : (item.trend === 'down' ? 'Queda' : 'Estável')}</td>
                                <td class="${intensityClass} fw-bold">${item.intensity.toUpperCase()}</td>
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
