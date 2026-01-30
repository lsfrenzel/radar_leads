from flask import Flask, request, jsonify, render_template_string
from engine import MarketIntelligenceEngine
import os
import re
import json

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
        .navbar { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(10px); border-bottom: 1px solid rgba(255,255,255,0.05); }
        .nav-link { color: var(--text-muted) !important; font-weight: 500; transition: all 0.3s; }
        .nav-link:hover, .nav-link.active { color: var(--accent) !important; }
        .glass-card { background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5); backdrop-filter: blur(10px); transition: all 0.3s ease; }
        .glass-card:hover { border-color: var(--accent); }
        .hero-title { background: linear-gradient(135deg, #fff 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.5rem; }
        .btn-primary { background: var(--accent); border: none; padding: 12px 24px; border-radius: 12px; font-weight: 600; box-shadow: 0 0 20px var(--accent-glow); transition: all 0.3s; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 0 30px var(--accent-glow); background: #2563eb; }
        .form-control, .form-select { background: #1e293b; border: 1px solid #334155; color: #fff; border-radius: 10px; padding: 12px; }
        .form-control:focus, .form-select:focus { background: #1e293b; color: #fff; border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }
        
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
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top">
        <div class="container">
            <a class="navbar-brand fw-bold text-primary" href="/">RADAR SP</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if active_page == 'leads' else '' }}" href="/">Radar de Leads</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if active_page == 'tendencias' else '' }}" href="/tendencias">Radar de Tendências</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        {% if active_page == 'leads' %}
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
                    <div class="glass-card p-4 border-primary">
                        <h4 class="mb-3 text-primary"><i class="bi bi-lightbulb me-2"></i>Análise dos Resultados & Recomendações</h4>
                        <div id="aiAnalysisContent" class="text-main">
                            <div class="d-flex align-items-center">
                                <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                                <span class="small text-muted">Gerando insights estratégicos...</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-12 mb-4">
                    <div class="glass-card p-4">
                        <h4 class="mb-4 text-center"><i class="bi bi-graph-up text-primary me-2"></i>Curva de Tendência de Mercado (SP)</h4>
                        <div class="chart-container" style="position: relative; height:400px;">
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

                <div class="col-12 mb-4">
                    <div class="glass-card p-4">
                        <h4 class="mb-3 text-primary"><i class="bi bi-cpu me-2"></i>Modelos Mais Pesquisados & Referências</h4>
                        <div id="popularModelsContent" class="row g-3">
                            <div class="col-12 text-center py-3">
                                <span class="text-muted small">Aguardando análise...</span>
                            </div>
                        </div>
                    </div>
                </div>
        </div>
        {% elif active_page == 'tendencias' %}
        <div class="text-center mb-5">
            <h1 class="hero-title">Radar de Tendências SP</h1>
            <p class="text-muted">Produtos e Categorias em Ascensão por Região</p>
        </div>
        
        <div class="glass-card p-4">
            <form id="trendsForm">
                <div class="row g-3">
                    <div class="col-md-8">
                        <label class="small text-muted mb-2">REGIÃO DE SÃO PAULO</label>
                        <select class="form-select" id="region">
                            <option value="todas">Todas as Regiões</option>
                            <option value="capital">Capital (Centro, ZN, ZS, ZL, ZO)</option>
                            <option value="abc">Grande ABC</option>
                            <option value="interior">Interior Paulista</option>
                            <option value="litoral">Litoral</option>
                            <option disabled>──────────</option>
                            <option value="bairro:centro">Centro (SP)</option>
                            <option value="bairro:itaim_bibi">Itaim Bibi</option>
                            <option value="bairro:moema">Moema</option>
                            <option value="bairro:pinheiros">Pinheiros</option>
                            <option value="bairro:vila_madalena">Vila Madalena</option>
                            <option value="bairro:tatuape">Tatuapé</option>
                            <option value="bairro:santana">Santana</option>
                            <option value="bairro:morumbi">Morumbi</option>
                            <option value="bairro:jardins">Jardins</option>
                        </select>
                    </div>
                    <div class="col-md-4 d-flex align-items-end">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-graph-up-arrow me-2"></i>MAPEAR TENDÊNCIAS
                        </button>
                    </div>
                </div>
            </form>
        </div>

        <div id="trendsResults" class="mt-4"></div>
        <div id="trendsDashboard" class="row mt-4" style="display: none;">
            <div class="col-md-6 mb-4">
                <div class="glass-card p-4">
                    <h5 class="text-primary mb-3"><i class="bi bi-fire me-2"></i>Produtos "Hot" Agora</h5>
                    <div id="hotProducts" class="list-group list-group-flush bg-transparent"></div>
                </div>
            </div>
            <div class="col-md-6 mb-4">
                <div class="glass-card p-4">
                    <h5 class="text-primary mb-3"><i class="bi bi-geo-fill me-2"></i>Demanda por Micro-região</h5>
                    <div style="position: relative; height:300px;">
                        <canvas id="regionChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}
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
            <button type="button" class="btn btn-secondary" data-bs-modal="dismiss">Fechar</button>
          </div>
        </div>
      </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        {% if active_page == 'leads' %}
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
            doc.setFillColor(2, 6, 23);
            doc.rect(0, 0, pageWidth, 50, 'F');
            doc.setTextColor(255, 255, 255);
            doc.setFont("helvetica", "bold");
            doc.setFontSize(26);
            doc.text("RADAR DE LEADS SP", 20, 25);
            doc.setFont("helvetica", "normal");
            doc.setFontSize(10);
            doc.setTextColor(148, 163, 184);
            doc.text("Inteligência de Mercado em Tempo Real", 20, 32);
            doc.text(`Relatório Gerado em: ${new Date().toLocaleString('pt-BR')}`, 20, 38);
            let y = 65;
            const trendCanvas = document.getElementById('trendChart');
            const originalBackground = trendCanvas.style.backgroundColor;
            trendCanvas.style.backgroundColor = '#0f172a';
            const trendImg = trendCanvas.toDataURL('image/png', 1.0);
            doc.setTextColor(15, 23, 42);
            doc.setFontSize(16);
            doc.setFont("helvetica", "bold");
            doc.text("1. Análise de Tendência de Mercado", 20, y);
            y += 10;
            doc.setDrawColor(59, 130, 246);
            doc.setLineWidth(0.5);
            doc.rect(19, y - 1, 172, 82);
            doc.addImage(trendImg, 'PNG', 20, y, 170, 80);
            y += 95;
            doc.setFontSize(16);
            doc.text("2. Intelligence Feed (Estratificado)", 20, y);
            y += 12;
            doc.setFillColor(241, 245, 249);
            doc.rect(20, y - 6, 170, 10, 'F');
            doc.setFontSize(9);
            doc.setTextColor(100, 116, 139);
            doc.text("CIDADE / BAIRRO", 25, y);
            doc.text("DEMANDA", 95, y);
            doc.text("TENDÊNCIA", 125, y);
            doc.text("INTENSIDADE", 155, y);
            y += 10;
            doc.setTextColor(30, 41, 59);
            lastResults.forEach((item, i) => {
                if (y > 275) { 
                    doc.addPage(); 
                    y = 30; 
                    doc.setFillColor(241, 245, 249);
                    doc.rect(20, y - 6, 170, 10, 'F');
                    doc.text("CIDADE / BAIRRO", 25, y);
                    doc.text("DEMANDA", 95, y);
                    doc.text("TENDÊNCIA", 125, y);
                    doc.text("INTENSIDADE", 155, y);
                    y += 10;
                }
                if (i % 2 === 0) {
                    doc.setFillColor(248, 250, 252);
                    doc.rect(20, y - 6, 170, 8, 'F');
                }
                doc.setFont("helvetica", "bold");
                doc.text(`${item.city} - ${item.neighborhood}`, 25, y);
                doc.setFont("helvetica", "normal");
                doc.text(`${item.demand_percentage}%`, 95, y);
                doc.text(`${item.trend.toUpperCase()}`, 125, y);
                doc.text(`${item.intensity.toUpperCase()}`, 155, y);
                y += 8;
            });
            trendCanvas.style.backgroundColor = originalBackground;
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
            const wscols = [{wch: 20}, {wch: 20}, {wch: 15}, {wch: 15}, {wch: 15}, {wch: 15}, {wch: 100}];
            ws['!cols'] = wscols;
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Leads SP");
            XLSX.writeFile(wb, `radar-leads-sp-${new Date().getTime()}.xlsx`);
        }

        function updateDashboard(resultsData) {
            const results = resultsData.stratified_data;
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
                    responsive: true,
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
            const heatmapContainer = document.getElementById('heatmapContainer');
            heatmapContainer.innerHTML = '';
            results.forEach(r => {
                const cell = document.createElement('div');
                const heatClass = r.intensity === 'high' ? 'heat-high' : (r.intensity === 'medium' ? 'heat-medium' : 'heat-low');
                cell.className = `heatmap-cell ${heatClass}`;
                cell.innerHTML = `<div style="font-size: 0.7rem; opacity: 0.8;">${r.city}</div><div style="font-size: 0.9rem;">${r.neighborhood}</div><div style="font-size: 1.1rem; margin-top: 5px;">${r.demand_percentage}%</div>`;
                cell.onclick = () => showDetails(r.city, r.neighborhood, r.sources);
                heatmapContainer.appendChild(cell);
            });
            const aiAnalysisContent = document.getElementById('aiAnalysisContent');
            const topCity = results[0];
            aiAnalysisContent.innerHTML = `<p><strong>Destaque Geográfico:</strong> A maior demanda foi detectada em <strong>${topCity.city} (${topCity.neighborhood})</strong> com ${topCity.demand_percentage}% de interesse.</p><p><strong>Recomendação:</strong> Focar esforços de marketing digital e força de vendas nas regiões de intensidade 'high' para maximizar a conversão imediata.</p>`;
            lastResults = results;
            const popularModelsContent = document.getElementById('popularModelsContent');
            if (resultsData.popular_models && resultsData.popular_models.length > 0) {
                let modelsHtml = '';
                resultsData.popular_models.forEach(model => {
                    modelsHtml += `<div class="col-md-4"><div class="glass-card p-3 h-100 border-info"><h6 class="text-info mb-2">${model.name}</h6><p class="small text-muted mb-0">${model.reason}</p></div></div>`;
                });
                popularModelsContent.innerHTML = modelsHtml;
            }
        }

        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const product = document.getElementById('product').value;
            const days = document.getElementById('days').value;
            const resultsDiv = document.getElementById('results');
            const legend = document.getElementById('legend');
            const exportControls = document.getElementById('exportControls');
            const dashboard = document.getElementById('dashboard');
            resultsDiv.innerHTML = `<div class="loader-container"><div class="cyber-loader"><div></div><div></div><div></div></div><div class="loading-text">Mapeando Signals...</div></div>`;
            legend.style.display = 'none';
            exportControls.style.display = 'none';
            dashboard.style.display = 'none';
            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ product, days })
                });
                const data = await response.json();
                resultsDiv.innerHTML = '';
                legend.style.display = 'block';
                exportControls.style.display = 'block';
                dashboard.style.display = 'flex';
                updateDashboard(data);
            } catch (err) {
                resultsDiv.innerHTML = '<div class="alert alert-danger">Erro ao processar inteligência.</div>';
            }
        });
        {% elif active_page == 'tendencias' %}
        let regionChart = null;
        document.getElementById('trendsForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const region = document.getElementById('region').value;
            const resultsDiv = document.getElementById('trendsResults');
            const dashboard = document.getElementById('trendsDashboard');
            resultsDiv.innerHTML = `<div class="loader-container"><div class="cyber-loader"><div></div><div></div><div></div></div><div class="loading-text">Analisando Big Data Regional...</div></div>`;
            dashboard.style.display = 'none';
            try {
                const response = await fetch('/api/trends', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ region })
                });
                const data = await response.json();
                resultsDiv.innerHTML = '';
                dashboard.style.display = 'flex';
                const hotDiv = document.getElementById('hotProducts');
                hotDiv.innerHTML = data.hot_products.map(p => `
                    <a href="${p.url}" target="_blank" class="list-group-item list-group-item-action bg-transparent border-0 d-flex justify-content-between align-items-center text-decoration-none">
                        <div>
                            <h6 class="mb-0 text-white">${p.name} <i class="bi bi-box-arrow-up-right small text-muted ms-1"></i></h6>
                            <small class="text-muted">${p.category}</small>
                        </div>
                        <span class="badge bg-primary rounded-pill">+${p.growth}%</span>
                    </a>`).join('');
                if (regionChart) regionChart.destroy();
                const ctx = document.getElementById('regionChart').getContext('2d');
                regionChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: data.regions.map(r => r.name),
                        datasets: [{
                            data: data.regions.map(r => r.value),
                            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom', labels: { color: '#fff', boxWidth: 12 } } }
                    }
                });
            } catch (err) {
                resultsDiv.innerHTML = '<div class="alert alert-danger">Erro ao carregar tendências regionais.</div>';
            }
        });
        {% endif %}
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, active_page='leads')

@app.route("/tendencias")
def tendencias():
    return render_template_string(HTML_TEMPLATE, active_page='tendencias')

@app.route("/api/trends", methods=["POST"])
def get_trends():
    region = request.json.get('region')
    
    # Determinar o nome amigável da região/bairro
    if region and region.startswith("bairro:"):
        loc_nome = region.split(":")[1].replace("_", " ").title()
        contexto = f"bairro {loc_nome}"
    else:
        mapeamento = {
            "todas": "Estado de São Paulo",
            "capital": "Capital de São Paulo",
            "abc": "Grande ABC Paulista",
            "interior": "Interior Paulista",
            "litoral": "Litoral Paulista"
        }
        loc_nome = mapeamento.get(region, "São Paulo")
        contexto = f"região {loc_nome}"

    prompt = f"Gere uma análise de tendências de consumo EM TEMPO REAL para a {contexto} em São Paulo (Jan 2026). " \
             f"Seja extremamente específico sobre o que as pessoas estão buscando agora nessa localidade. " \
             f"Retorne 4 produtos/serviços 'hot' com categoria, porcentagem de crescimento e um link de referência (ex: busca no Google Shopping ou site de notícias relevante). " \
             f"e a distribuição de interesse por sub-áreas/bairros da localidade em 5 pontos." \
             f"Formato JSON: {{\"hot_products\": [{{ \"name\": \"\", \"category\": \"\", \"growth\": 0, \"url\": \"\" }}], \"regions\": [{{ \"name\": \"\", \"value\": 0 }}]}}"
    
    try:
        from engine import client, MODEL
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=60.0
        )
        content = response.choices[0].message.content
        if content:
            data = json.loads(content)
            return jsonify(data)
    except Exception as e:
        print(f"Erro na IA de tendências: {e}")
        # Fallback se a IA falhar
        if region and region.startswith("bairro:"):
            return jsonify({
                "hot_products": [
                    {"name": f"Delivery Premium em {loc_nome}", "category": "Gastronomia", "growth": 45, "url": "https://www.ifood.com.br"},
                    {"name": "Serviços Home Office", "category": "Tecnologia", "growth": 32, "url": "https://www.mercadolivre.com.br"},
                    {"name": "Saúde Preventiva", "category": "Bem-estar", "growth": 28, "url": "https://www.drogaraia.com.br"},
                    {"name": "Mobilidade Elétrica", "category": "Transporte", "growth": 15, "url": "https://www.movida.com.br"}
                ],
                "regions": [
                    {"name": "Setor Norte", "value": 30},
                    {"name": "Setor Sul", "value": 25},
                    {"name": "Setor Leste", "value": 20},
                    {"name": "Setor Oeste", "value": 15},
                    {"name": "Centro", "value": 10}
                ]
            })
        
        return jsonify({
            "hot_products": [
                {"name": "Ar Condicionado Inverter", "category": "Eletro", "growth": 45, "url": "https://www.magazineluiza.com.br"},
                {"name": "Protetor Solar FPS 60+", "category": "Saúde", "growth": 38, "url": "https://www.belezanaweb.com.br"},
                {"name": "Cerveja Artesanal IPA", "category": "Bebidas", "growth": 22, "url": "https://www.empiriodacerveja.com.br"},
                {"name": "Bicicleta Elétrica", "category": "Mobilidade", "growth": 15, "url": "https://www.decathlon.com.br"}
            ],
            "regions": [
                {"name": "Centro", "value": 30},
                {"name": "Zona Sul", "value": 25},
                {"name": "Zona Leste", "value": 20},
                {"name": "Zona Oeste", "value": 15},
                {"name": "Zona Norte", "value": 10}
            ]
        })

@app.route("/api/analyze", methods=["POST"])
def analyze():
    product = request.json.get("product")
    days = int(request.json.get("days", 30))
    results = engine.run_intelligence(product, days=days)
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
