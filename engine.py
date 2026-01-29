import os
from openai import OpenAI
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from unidecode import unidecode
import json
from datetime import datetime, timedelta

# Integración de OpenAI via Replit AI Integrations
# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

client = OpenAI(
    api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
    base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
)

class MarketIntelligenceEngine:
    def __init__(self):
        self.model = "gpt-5"

    def normalize_text(self, text):
        if not text: return ""
        text = text.lower()
        text = unidecode(text)
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def scrape_simulated(self, product, keywords, days):
        # En un escenario real, aquí irían los scrapers para sitios específicos
        # Para este MVP, simulamos la recolección de datos públicos (foros, reviews)
        # basados en el producto para demostrar el pipeline de procesamiento.
        
        base_date = datetime.now()
        data = [
            {"text": f"Alguém sabe onde comprar {product} em São Paulo? Vi um review ótimo.", "source": "Forum X", "date": (base_date - timedelta(days=2)).isoformat()},
            {"text": f"O {product} é muito caro no Rio de Janeiro, vale a pena?", "source": "Social Media", "date": (base_date - timedelta(days=5)).isoformat()},
            {"text": f"Melhor preço de {product} em Curitiba!", "source": "Marketplace", "date": (base_date - timedelta(days=1)).isoformat()},
            {"text": f"Dúvida sobre {product}: funciona em BH?", "source": "QA Site", "date": (base_date - timedelta(days=10)).isoformat()},
            {"text": "Amo esse clima de Florianópolis, perfeito para testar novas tecnologias.", "source": "Blog", "date": (base_date - timedelta(days=3)).isoformat()},
        ]
        return data

    def analyze_mentions(self, mentions, product):
        results = []
        for m in mentions:
            prompt = f"""
            Analise a seguinte menção sobre o produto '{product}':
            Texto: "{m['text']}"
            
            Retorne um JSON com:
            1. intent_score: (0 a 1) Probabilidade de intenção de compra ou interesse ativo.
            2. classification: "intent", "research", "comparison", "neutral".
            3. location: {{"city": "Nome", "state": "UF", "region": "Região"}} (se detectado).
            
            Seja rigoroso no score.
            """
            
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                if content is None:
                    continue
                analysis = json.loads(content)
                
                m.update(analysis)
                if m.get('intent_score', 0) > 0.3: # Threshold configurável
                    results.append(m)
            except Exception as e:
                print(f"Error analyzing mention: {e}")
                
        return results

    def run_intelligence(self, product, keywords=None, days=30):
        raw_data = self.scrape_simulated(product, keywords, days)
        # Normalização
        for item in raw_data:
            item['normalized_text'] = self.normalize_text(item['text'])
            
        # Deduplicação básica
        df = pd.DataFrame(raw_data).drop_duplicates(subset=['normalized_text'])
        unique_data = df.to_dict('records')
        
        # Análise NLP
        processed_data = self.analyze_mentions(unique_data, product)
        return processed_data

if __name__ == "__main__":
    engine = MarketIntelligenceEngine()
    print(engine.run_intelligence("iPhone 15", days=7))
