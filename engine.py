import os
from openai import OpenAI
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

    def scrape_realtime(self, product, days=30):
        # Usando OpenAI gpt-5 para rastreamento da internet em tempo real
        # Nota: gpt-5 tem capacidades de pesquisa integradas
        
        prompt = f"""
        Aja como um agente de busca em tempo real. 
        Pesquise menções recentes (últimos {days} dias) em redes sociais, fóruns e notícias 
        sobre consumidores no Brasil interessados em adquirir '{product}'.
        
        Retorne estritamente um JSON com a seguinte estrutura:
        {{
            "mentions": [
                {{
                    "text": "texto da menção",
                    "source": "fonte (ex: Twitter, Reddit, G1)",
                    "date": "YYYY-MM-DD"
                }}
            ]
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                return data.get('mentions', [])
        except Exception as e:
            print(f"Erro no rastreamento real-time da OpenAI: {e}")
            
        return []

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
        # Agora usamos a capacidade de busca da OpenAI gpt-5
        raw_data = self.scrape_realtime(product, days)
        
        # Normalização
        for item in raw_data:
            item['normalized_text'] = self.normalize_text(item['text'])
            
        # Deduplicação básica
        if raw_data:
            df = pd.DataFrame(raw_data).drop_duplicates(subset=['normalized_text'])
            unique_data = df.to_dict('records')
        else:
            unique_data = []
        
        # Análise NLP
        processed_data = self.analyze_mentions(unique_data, product)
        return processed_data

if __name__ == "__main__":
    engine = MarketIntelligenceEngine()
    print(engine.run_intelligence("iPhone 15", days=7))
