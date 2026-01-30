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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #020617;
            --card-bg: #0f172a;
            --accent: #3b82f6;
            --accent-secondary: #8b5cf6;
            --accent-glow: rgba(59, 130, 246, 0.5);
            --accent-glow-purple: rgba(139, 92, 246, 0.4);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --cyber-green: #00ff88;
            --cyber-cyan: #00d4ff;
        }
        body { background-color: var(--bg-dark); color: var(--text-main); font-family: 'Inter', system-ui, sans-serif; overflow-x: hidden; }
        
        .navbar { 
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0.85) 100%);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(59, 130, 246, 0.15);
            padding: 1rem 0;
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3), 0 0 40px rgba(59, 130, 246, 0.05);
        }
        .navbar-brand {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #00d4ff 0%, #3b82f6 50%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 2px;
            position: relative;
            padding-left: 35px;
        }
        .navbar-brand::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            width: 24px;
            height: 24px;
            background: linear-gradient(135deg, #00d4ff, #3b82f6);
            border-radius: 6px;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.5);
        }
        .navbar-brand::after {
            content: '';
            position: absolute;
            left: 6px;
            top: 50%;
            transform: translateY(-50%);
            width: 12px;
            height: 12px;
            border: 2px solid rgba(255,255,255,0.9);
            border-radius: 3px;
        }
        .nav-link { 
            color: var(--text-muted) !important; 
            font-weight: 500; 
            font-size: 0.9rem;
            letter-spacing: 0.5px;
            padding: 0.6rem 1.2rem !important;
            margin: 0 0.2rem;
            border-radius: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .nav-link::before {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 2px;
            background: linear-gradient(90deg, #00d4ff, #3b82f6, #8b5cf6);
            transition: width 0.3s ease;
            border-radius: 2px;
        }
        .nav-link:hover::before, .nav-link.active::before {
            width: 80%;
        }
        .nav-link:hover { 
            color: #fff !important;
            background: rgba(59, 130, 246, 0.1);
        }
        .nav-link.active { 
            color: #fff !important;
            background: rgba(59, 130, 246, 0.15);
        }
        
        .glass-card { background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5); backdrop-filter: blur(10px); transition: all 0.3s ease; }
        .glass-card:hover { border-color: var(--accent); }
        
        .hero-section {
            position: relative;
            padding: 2rem 0;
        }
        .hero-section::before {
            content: '';
            position: absolute;
            top: -100px;
            left: 50%;
            transform: translateX(-50%);
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, rgba(139, 92, 246, 0.1) 30%, transparent 70%);
            pointer-events: none;
            z-index: -1;
        }
        .hero-title { 
            font-family: 'Space Grotesk', sans-serif;
            background: linear-gradient(135deg, #fff 0%, #00d4ff 40%, #3b82f6 70%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            font-size: 3rem;
            letter-spacing: -1px;
            text-shadow: 0 0 80px rgba(59, 130, 246, 0.5);
            margin-bottom: 0.5rem;
        }
        .hero-subtitle {
            color: var(--text-muted);
            font-size: 1.1rem;
            font-weight: 400;
            letter-spacing: 0.5px;
        }
        .hero-subtitle span {
            color: var(--accent);
            font-weight: 500;
        }
        .btn-primary { background: var(--accent); border: none; padding: 12px 24px; border-radius: 12px; font-weight: 600; box-shadow: 0 0 20px var(--accent-glow); transition: all 0.3s; }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 0 30px var(--accent-glow); background: #2563eb; }
        .form-control, .form-select { background: #1e293b; border: 1px solid #334155; color: #fff; border-radius: 10px; padding: 12px; }
        .form-control:focus, .form-select:focus { background: #1e293b; color: #fff; border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }
        .form-control::placeholder { color: #64748b; opacity: 1; font-weight: 400; }
        .form-control::-webkit-input-placeholder { color: #64748b; }
        .form-control::-moz-placeholder { color: #64748b; }
        .form-control:-ms-input-placeholder { color: #64748b; }
        
        .chart-responsive-container { 
            position: relative; 
            min-height: 280px;
            width: 100%;
            overflow: visible;
        }
        .chart-responsive-container canvas {
            max-width: 100%;
            height: auto !important;
        }
        @media (max-width: 768px) {
            .chart-responsive-container {
                min-height: 250px;
            }
        }
        
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
                    <li class="nav-item">
                        <a class="nav-link {{ 'active' if active_page == 'nicho' else '' }}" href="/nicho">Radar por Nicho</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        {% if active_page == 'leads' %}
        <div class="hero-section text-center mb-5">
            <h1 class="hero-title">Radar de Leads SP</h1>
            <p class="hero-subtitle">Inteligência de Mercado em <span>Tempo Real</span> para o Estado de São Paulo</p>
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
        <div class="hero-section text-center mb-5">
            <h1 class="hero-title">Radar de Tendências SP</h1>
            <p class="hero-subtitle">Produtos e Categorias em <span>Ascensão</span> por Região</p>
        </div>
        
        <div class="glass-card p-4">
            <form id="trendsForm">
                <div class="row g-3">
                    <div class="col-md-5">
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
                    <div class="col-md-4">
                        <label class="small text-muted mb-2">CEP (OPCIONAL - VARREDURA LOCAL)</label>
                        <input type="text" class="form-control" id="cep" placeholder="Ex: 01310-100" maxlength="9">
                        <small class="text-muted">Informe o CEP para análise em torno dessa localização</small>
                    </div>
                    <div class="col-md-3 d-flex align-items-end">
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
        {% elif active_page == 'nicho' %}
        <div class="hero-section text-center mb-5">
            <h1 class="hero-title">Radar por Nicho</h1>
            <p class="hero-subtitle">Inteligência de Mercado por <span>Segmento de Negócio</span></p>
        </div>
        
        <div class="glass-card p-4 mb-4">
            <form id="nichoForm">
                <div class="row g-3">
                    <div class="col-md-5">
                        <label class="small text-muted mb-2">NICHO DE NEGÓCIO</label>
                        <select class="form-select" id="nicho">
                            <option value="comercio_local">Comércio e Serviços Locais</option>
                            <option value="imobiliario">Mercado Imobiliário</option>
                            <option value="ecommerce">E-commerce e Vendas Online</option>
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label class="small text-muted mb-2">SEGMENTO ESPECÍFICO (OPCIONAL)</label>
                        <input type="text" class="form-control" id="segmento" placeholder="Ex: Pet Shop, Clínica Estética...">
                    </div>
                    <div class="col-md-3 d-flex align-items-end">
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="bi bi-search me-2"></i>ANALISAR NICHO
                        </button>
                    </div>
                </div>
            </form>
        </div>

        <div id="nichoSubtipo" class="mb-4" style="display: none;">
            <div class="row g-3">
                <div class="col-md-12">
                    <div class="d-flex flex-wrap gap-2" id="subtipoButtons"></div>
                </div>
            </div>
        </div>

        <div id="nichoResults" class="mt-4"></div>
        
        <div id="nichoDashboard" class="mt-4" style="display: none;">
            <div class="row g-4">
                <div class="col-md-6">
                    <div class="glass-card p-4 h-100">
                        <h5 class="text-primary mb-3"><i class="bi bi-rocket-takeoff me-2"></i>Oportunidades Identificadas</h5>
                        <div id="oportunidades"></div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="glass-card p-4 h-100">
                        <h5 class="text-warning mb-3"><i class="bi bi-graph-up me-2"></i>Tendências em Alta</h5>
                        <div id="tendenciasNicho"></div>
                    </div>
                </div>
            </div>
            <div class="row g-4 mt-2">
                <div class="col-md-4">
                    <div class="glass-card p-4 h-100">
                        <h5 class="text-danger mb-3"><i class="bi bi-exclamation-triangle me-2"></i>Dores do Mercado</h5>
                        <div id="doresNicho"></div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="glass-card p-4 h-100">
                        <h5 class="text-success mb-3"><i class="bi bi-lightbulb me-2"></i>Ações Recomendadas</h5>
                        <div id="acoesNicho"></div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="glass-card p-4 h-100">
                        <h5 class="text-info mb-3"><i class="bi bi-people me-2"></i>Perfil do Cliente</h5>
                        <div id="perfilCliente"></div>
                    </div>
                </div>
            </div>
            <div class="row g-4 mt-2">
                <div class="col-md-6">
                    <div class="glass-card p-4">
                        <h5 class="text-primary mb-3"><i class="bi bi-bar-chart me-2"></i>Produtos/Serviços em Destaque</h5>
                        <div class="chart-responsive-container">
                            <canvas id="nichoChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="glass-card p-4">
                        <h5 class="text-primary mb-3"><i class="bi bi-geo-alt me-2"></i>Regiões com Maior Potencial</h5>
                        <div id="regioesNicho" class="heatmap-grid"></div>
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
        
        document.getElementById('cep').addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 5) {
                value = value.slice(0, 5) + '-' + value.slice(5, 8);
            }
            e.target.value = value;
        });
        
        document.getElementById('trendsForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const region = document.getElementById('region').value;
            const cep = document.getElementById('cep').value.replace(/\D/g, '');
            const resultsDiv = document.getElementById('trendsResults');
            const dashboard = document.getElementById('trendsDashboard');
            const loadingMsg = cep ? 'Analisando região do CEP ' + document.getElementById('cep').value + '...' : 'Analisando Big Data Regional...';
            resultsDiv.innerHTML = `<div class="loader-container"><div class="cyber-loader"><div></div><div></div><div></div></div><div class="loading-text">${loadingMsg}</div></div>`;
            dashboard.style.display = 'none';
            try {
                const response = await fetch('/api/trends', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ region, cep: cep || null })
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
        {% elif active_page == 'nicho' %}
        let nichoChart = null;
        const subtipos = {
            'comercio_local': ['Restaurantes', 'Clínicas', 'Oficinas', 'Academias', 'Salões de Beleza', 'Pet Shops', 'Escolas/Cursos'],
            'imobiliario': ['Apartamentos', 'Casas', 'Comercial', 'Terrenos', 'Lançamentos', 'Alto Padrão'],
            'ecommerce': ['Moda', 'Eletrônicos', 'Casa/Decoração', 'Beleza', 'Saúde', 'Esportes', 'Dropshipping']
        };
        
        document.getElementById('nicho').addEventListener('change', function() {
            const subtipoBtns = document.getElementById('subtipoButtons');
            const nichoVal = this.value;
            subtipoBtns.innerHTML = subtipos[nichoVal].map(s => 
                `<button type="button" class="btn btn-outline-primary btn-sm subtipo-btn" data-subtipo="${s}">${s}</button>`
            ).join('');
            document.getElementById('nichoSubtipo').style.display = 'block';
            
            document.querySelectorAll('.subtipo-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    document.querySelectorAll('.subtipo-btn').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    document.getElementById('segmento').value = this.dataset.subtipo;
                });
            });
        });
        
        document.getElementById('nichoForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const nicho = document.getElementById('nicho').value;
            const segmento = document.getElementById('segmento').value;
            const resultsDiv = document.getElementById('nichoResults');
            const dashboard = document.getElementById('nichoDashboard');
            
            const nichoNomes = {
                'comercio_local': 'Comércio e Serviços Locais',
                'imobiliario': 'Mercado Imobiliário',
                'ecommerce': 'E-commerce e Vendas Online'
            };
            
            resultsDiv.innerHTML = `<div class="loader-container">
                <div class="cyber-loader"><div></div><div></div><div></div></div>
                <div class="loading-text">Analisando ${nichoNomes[nicho]}${segmento ? ' - ' + segmento : ''}...</div>
                <p class="text-muted mt-3 small">Varrendo buscas, redes sociais, notícias, marketplaces e reclamações...</p>
            </div>`;
            dashboard.style.display = 'none';
            
            try {
                const response = await fetch('/api/nicho', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ nicho, segmento: segmento || null })
                });
                const data = await response.json();
                resultsDiv.innerHTML = '';
                dashboard.style.display = 'block';
                
                document.getElementById('oportunidades').innerHTML = data.oportunidades.map(o => `
                    <div class="mb-3 p-3 bg-dark rounded">
                        <h6 class="text-white mb-1"><i class="bi bi-check-circle text-success me-2"></i>${o.titulo}</h6>
                        <p class="small text-muted mb-0">${o.descricao}</p>
                    </div>
                `).join('');
                
                document.getElementById('tendenciasNicho').innerHTML = data.tendencias.map(t => `
                    <div class="d-flex justify-content-between align-items-center mb-2 p-2 bg-dark rounded">
                        <span class="text-white">${t.nome}</span>
                        <span class="badge bg-warning text-dark">+${t.crescimento}%</span>
                    </div>
                `).join('');
                
                document.getElementById('doresNicho').innerHTML = data.dores.map(d => `
                    <div class="mb-2 p-2 bg-dark rounded">
                        <small class="text-danger"><i class="bi bi-exclamation-circle me-1"></i>${d}</small>
                    </div>
                `).join('');
                
                document.getElementById('acoesNicho').innerHTML = data.acoes.map(a => `
                    <div class="mb-2 p-2 bg-dark rounded">
                        <small class="text-success"><i class="bi bi-arrow-right-circle me-1"></i>${a}</small>
                    </div>
                `).join('');
                
                document.getElementById('perfilCliente').innerHTML = `
                    <div class="p-2 bg-dark rounded">
                        <p class="small text-info mb-2"><strong>Perfil:</strong> ${data.perfil.descricao}</p>
                        <p class="small text-muted mb-1"><strong>Faixa etária:</strong> ${data.perfil.faixa_etaria}</p>
                        <p class="small text-muted mb-1"><strong>Renda:</strong> ${data.perfil.renda}</p>
                        <p class="small text-muted mb-0"><strong>Comportamento:</strong> ${data.perfil.comportamento}</p>
                    </div>
                `;
                
                document.getElementById('regioesNicho').innerHTML = data.regioes.map(r => `
                    <div class="heatmap-cell heat-${r.potencial}">
                        <div class="fw-bold">${r.nome}</div>
                        <small>${r.indice}%</small>
                    </div>
                `).join('');
                
                if (nichoChart) nichoChart.destroy();
                const ctx = document.getElementById('nichoChart').getContext('2d');
                nichoChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: data.produtos.map(p => p.nome),
                        datasets: [{
                            label: 'Índice de Demanda',
                            data: data.produtos.map(p => p.demanda),
                            backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
                        }]
                    },
                    options: {
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        layout: {
                            padding: { left: 10, right: 20 }
                        },
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#fff' } },
                            y: { 
                                grid: { display: false }, 
                                ticks: { 
                                    color: '#fff',
                                    font: { size: 11 },
                                    callback: function(value, index, values) {
                                        const label = this.getLabelForValue(value);
                                        return label.length > 20 ? label.substring(0, 18) + '...' : label;
                                    }
                                }
                            }
                        }
                    }
                });
            } catch (err) {
                resultsDiv.innerHTML = '<div class="alert alert-danger">Erro ao analisar nicho. Tente novamente.</div>';
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

@app.route("/nicho")
def nicho():
    return render_template_string(HTML_TEMPLATE, active_page='nicho')

@app.route("/api/nicho", methods=["POST"])
def get_nicho():
    nicho = request.json.get('nicho')
    segmento = request.json.get('segmento')
    
    nicho_configs = {
        "comercio_local": {
            "nome": "Comércio e Serviços Locais",
            "contexto": "restaurantes, clínicas, oficinas, academias, salões de beleza, pet shops, escolas e cursos locais em São Paulo",
            "analise": """Identifique:
- Produtos e serviços em crescimento na região
- Tendências sazonais próximas
- Reclamações frequentes sobre concorrentes (Reclame Aqui, Google Reviews)
- Demandas não atendidas no mercado local
- Horários e dias de maior interesse

Entregue insights sobre:
- Oportunidades locais claras
- Regiões com maior potencial
- Sugestões práticas de ação (promoções, estoque, anúncios)"""
        },
        "imobiliario": {
            "nome": "Mercado Imobiliário",
            "contexto": "corretores autônomos, imobiliárias e construtoras em São Paulo",
            "analise": """Identifique:
- Tipos de imóveis mais buscados
- Faixas de preço em alta
- Bairros ou regiões em crescimento
- Intenção do cliente (compra, aluguel, financiamento)
- Termos recorrentes ligados a urgência ou decisão

Entregue insights sobre:
- Insights por região
- Perfil do comprador
- Sugestões de abordagem comercial e anúncios"""
        },
        "ecommerce": {
            "nome": "E-commerce e Vendas Online",
            "contexto": "pequenos e médios e-commerces, dropshipping e marcas digitais",
            "analise": """Identifique:
- Produtos emergentes antes da saturação
- Comparações frequentes entre produtos
- Reclamações recorrentes que indiquem falhas de mercado
- Tendências sazonais futuras
- Intenção de compra clara

Entregue insights sobre:
- Produtos com alto potencial
- Oportunidades de diferenciação
- Sugestões de campanhas e posicionamento"""
        }
    }
    
    config = nicho_configs.get(nicho, nicho_configs["comercio_local"])
    segmento_texto = f" com foco específico em {segmento}" if segmento else ""
    
    prompt = f"""Você é um analista de inteligência de mercado especializado. Analise a internet (buscas do Google, redes sociais, notícias, marketplaces como Mercado Livre e Amazon, e sites de reclamações como Reclame Aqui) para o nicho de {config['nome']}{segmento_texto}.

Contexto: {config['contexto']}

{config['analise']}

Data atual: Janeiro de 2026, São Paulo, Brasil.

Retorne um JSON estruturado com dados realistas e acionáveis:
{{
    "oportunidades": [
        {{"titulo": "título curto", "descricao": "descrição detalhada da oportunidade de negócio"}}
    ],
    "tendencias": [
        {{"nome": "nome da tendência", "crescimento": número de 10 a 150}}
    ],
    "dores": ["reclamação/problema 1", "reclamação/problema 2", "reclamação/problema 3"],
    "acoes": ["ação prática 1", "ação prática 2", "ação prática 3", "ação prática 4"],
    "perfil": {{
        "descricao": "descrição do cliente ideal",
        "faixa_etaria": "ex: 25-45 anos",
        "renda": "ex: Classe B/C",
        "comportamento": "principais comportamentos de compra"
    }},
    "produtos": [
        {{"nome": "produto/serviço", "demanda": número de 50 a 100}}
    ],
    "regioes": [
        {{"nome": "região/bairro", "potencial": "high/medium/low", "indice": número de 60 a 95}}
    ]
}}

Retorne exatamente 4 oportunidades, 5 tendências, 3 dores, 4 ações, 5 produtos e 5 regiões. Seja específico e realista para São Paulo em 2026."""
    
    try:
        from engine import client, MODEL
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=90.0
        )
        content = response.choices[0].message.content
        if content:
            data = json.loads(content)
            return jsonify(data)
    except Exception as e:
        print(f"Erro na IA de nicho: {e}")
        
        fallback_data = {
            "comercio_local": {
                "oportunidades": [
                    {"titulo": "Delivery de última hora", "descricao": "Alto crescimento de pedidos urgentes após 21h. Oportunidade para delivery noturno premium."},
                    {"titulo": "Serviços por assinatura", "descricao": "Clientes buscando conveniência com planos mensais para academias, estética e pet care."},
                    {"titulo": "Experiências locais", "descricao": "Aumento de 40% em buscas por 'aulas ao vivo' e 'workshops presenciais'."},
                    {"titulo": "Micro-franquias", "descricao": "Interesse crescente em negócios compactos e baixo investimento inicial."}
                ],
                "tendencias": [
                    {"nome": "Alimentação saudável rápida", "crescimento": 78},
                    {"nome": "Pet care premium", "crescimento": 65},
                    {"nome": "Estética masculina", "crescimento": 52},
                    {"nome": "Coworking de bairro", "crescimento": 45},
                    {"nome": "Aulas particulares híbridas", "crescimento": 38}
                ],
                "dores": [
                    "Demora no atendimento e filas longas",
                    "Falta de opções de pagamento (Pix, parcelamento)",
                    "Horários limitados que não atendem quem trabalha"
                ],
                "acoes": [
                    "Implementar sistema de agendamento online",
                    "Criar programa de fidelidade com cashback",
                    "Investir em Google Meu Negócio e reviews",
                    "Oferecer horário estendido aos sábados"
                ],
                "perfil": {
                    "descricao": "Profissional urbano que valoriza praticidade",
                    "faixa_etaria": "28-45 anos",
                    "renda": "Classe B/C+",
                    "comportamento": "Pesquisa online antes de comprar, valoriza avaliações"
                },
                "produtos": [
                    {"nome": "Delivery premium", "demanda": 92},
                    {"nome": "Banho e tosa pet", "demanda": 85},
                    {"nome": "Personal trainer", "demanda": 78},
                    {"nome": "Estética facial", "demanda": 72},
                    {"nome": "Cursos rápidos", "demanda": 65}
                ],
                "regioes": [
                    {"nome": "Pinheiros", "potencial": "high", "indice": 92},
                    {"nome": "Moema", "potencial": "high", "indice": 88},
                    {"nome": "Tatuapé", "potencial": "medium", "indice": 75},
                    {"nome": "Santana", "potencial": "medium", "indice": 70},
                    {"nome": "Santo Amaro", "potencial": "low", "indice": 62}
                ]
            },
            "imobiliario": {
                "oportunidades": [
                    {"titulo": "Studios compactos", "descricao": "Demanda explosiva por apartamentos de 25-35m² próximos ao metrô."},
                    {"titulo": "Home office integrado", "descricao": "Imóveis com espaço dedicado para trabalho remoto valorizam 15% mais."},
                    {"titulo": "Bairros emergentes", "descricao": "Vila Prudente e Ipiranga com valorização acima de 20% ao ano."},
                    {"titulo": "Financiamento facilitado", "descricao": "Clientes buscando imóveis na faixa do Minha Casa Verde Amarela."}
                ],
                "tendencias": [
                    {"nome": "Apartamentos pet-friendly", "crescimento": 85},
                    {"nome": "Imóveis próximos a parques", "crescimento": 72},
                    {"nome": "Condomínios com coworking", "crescimento": 68},
                    {"nome": "Aluguel por temporada", "crescimento": 55},
                    {"nome": "Imóveis retrofit", "crescimento": 42}
                ],
                "dores": [
                    "Corretores que não respondem rápido",
                    "Fotos ruins e descrições genéricas nos anúncios",
                    "Dificuldade em agendar visitas em horários flexíveis"
                ],
                "acoes": [
                    "Investir em tour virtual 360°",
                    "Responder leads em menos de 5 minutos",
                    "Criar conteúdo sobre os bairros no Instagram",
                    "Oferecer simulação de financiamento online"
                ],
                "perfil": {
                    "descricao": "Jovem profissional buscando primeiro imóvel",
                    "faixa_etaria": "25-35 anos",
                    "renda": "R$ 8.000 - R$ 15.000/mês",
                    "comportamento": "Pesquisa muito online, valoriza localização e transporte"
                },
                "produtos": [
                    {"nome": "Studios até 35m²", "demanda": 95},
                    {"nome": "2 dorms com varanda", "demanda": 88},
                    {"nome": "Aluguel mobiliado", "demanda": 82},
                    {"nome": "Casas em condomínio", "demanda": 70},
                    {"nome": "Salas comerciais", "demanda": 58}
                ],
                "regioes": [
                    {"nome": "Vila Mariana", "potencial": "high", "indice": 94},
                    {"nome": "Ipiranga", "potencial": "high", "indice": 87},
                    {"nome": "Tatuapé", "potencial": "medium", "indice": 78},
                    {"nome": "Butantã", "potencial": "medium", "indice": 72},
                    {"nome": "Penha", "potencial": "low", "indice": 65}
                ]
            },
            "ecommerce": {
                "oportunidades": [
                    {"titulo": "Produtos sustentáveis", "descricao": "Busca por 'eco-friendly' cresceu 120%. Nicho ainda pouco explorado."},
                    {"titulo": "Personalização", "descricao": "Clientes pagam até 30% mais por produtos personalizados."},
                    {"titulo": "Cross-border", "descricao": "Importados da China com marca própria ainda têm margem de 60%."},
                    {"titulo": "Bundles inteligentes", "descricao": "Kits combinados convertem 40% mais que produtos avulsos."}
                ],
                "tendencias": [
                    {"nome": "Skincare coreano", "crescimento": 135},
                    {"nome": "Acessórios para home office", "crescimento": 92},
                    {"nome": "Moda plus size", "crescimento": 78},
                    {"nome": "Produtos para pets", "crescimento": 65},
                    {"nome": "Suplementos naturais", "crescimento": 55}
                ],
                "dores": [
                    "Frete caro e demorado",
                    "Produtos que não correspondem às fotos",
                    "Dificuldade de troca e devolução"
                ],
                "acoes": [
                    "Oferecer frete grátis acima de valor mínimo",
                    "Investir em fotos e vídeos de qualidade",
                    "Criar unboxing experience memorável",
                    "Usar remarketing para carrinhos abandonados"
                ],
                "perfil": {
                    "descricao": "Comprador digital frequente e comparador",
                    "faixa_etaria": "22-40 anos",
                    "renda": "Classe B/C",
                    "comportamento": "Busca cupons, compara preços, lê reviews"
                },
                "produtos": [
                    {"nome": "Skincare importado", "demanda": 98},
                    {"nome": "Gadgets úteis", "demanda": 85},
                    {"nome": "Moda feminina", "demanda": 80},
                    {"nome": "Artigos fitness", "demanda": 72},
                    {"nome": "Decoração minimalista", "demanda": 68}
                ],
                "regioes": [
                    {"nome": "Grande SP", "potencial": "high", "indice": 95},
                    {"nome": "Interior SP", "potencial": "high", "indice": 88},
                    {"nome": "Sul/Sudeste", "potencial": "medium", "indice": 80},
                    {"nome": "Nordeste", "potencial": "medium", "indice": 72},
                    {"nome": "Centro-Oeste", "potencial": "low", "indice": 65}
                ]
            }
        }
        
        return jsonify(fallback_data.get(nicho, fallback_data["comercio_local"]))

@app.route("/api/trends", methods=["POST"])
def get_trends():
    region = request.json.get('region')
    cep = request.json.get('cep')
    
    # Se CEP foi informado, priorizar a análise por CEP
    if cep and len(cep) == 8:
        cep_formatado = f"{cep[:5]}-{cep[5:]}"
        contexto = f"região do CEP {cep_formatado} e arredores (raio de aproximadamente 5km)"
        analise_extra = f"Considere que o CEP {cep_formatado} está localizado em São Paulo. " \
                       f"Analise as tendências de consumo específicas para essa micro-região e bairros vizinhos. "
    elif region and region.startswith("bairro:"):
        loc_nome = region.split(":")[1].replace("_", " ").title()
        contexto = f"bairro {loc_nome}"
        analise_extra = ""
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
        analise_extra = ""

    prompt = f"Gere uma análise de tendências de consumo EM TEMPO REAL para a {contexto} em São Paulo (Jan 2026). " \
             f"{analise_extra}" \
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
