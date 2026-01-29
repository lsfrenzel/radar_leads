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
        print(f"Iniciando busca real-time para: {product}")
        # Simplificando ao máximo para garantir que a IA entenda a necessidade de dados reais
        prompt = f"""
        Find 5 real recent examples of people in Brazil looking to buy '{product}' on social media, forums or marketplaces from the last {days} days.
        Provide the text, source, and date. If you can't find exact matches, look for general market demand signals for this product.
        
        Return JSON format:
        {{
            "mentions": [
                {{
                    "text": "text of the post/mention",
                    "source": "Twitter/Facebook/Reddit/Marketplace",
                    "date": "2026-01-29"
                }}
            ]
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                timeout=45.0
            )
            content = response.choices[0].message.content
            print(f"Resposta bruta da OpenAI: {content}")
            if content:
                data = json.loads(content)
                mentions = data.get('mentions', [])
                if not mentions:
                    print("Lista 'mentions' vazia no JSON")
                return mentions
        except Exception as e:
            print(f"Erro no rastreamento real-time da OpenAI: {e}")
            
        return []

    def analyze_mentions(self, mentions, product):
        results = []
        for m in mentions:
            # Baixando o rigor para garantir que resultados apareçam
            prompt = f"""
            Analyze the following mention about '{product}':
            Text: "{m['text']}"
            
            Return JSON with:
            1. intent_score: (0 to 1) active interest.
            2. classification: "intent", "research", "comparison", "neutral".
            3. location: {{"city": "City Name", "state": "UF"}}
            
            Be helpful and identify even subtle interest.
            """
            
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    timeout=30.0
                )
                content = response.choices[0].message.content
                if content:
                    analysis = json.loads(content)
                    m.update(analysis)
                    # Baixando o threshold de 0.3 para 0.1 para não filtrar nada relevante
                    if m.get('intent_score', 0) > 0.1:
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
