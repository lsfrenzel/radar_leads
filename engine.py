import os
from openai import OpenAI
import pandas as pd
import re
from unidecode import unidecode
import json
from datetime import datetime, timedelta

# Utilizando a chave de API fornecida pelo usuário para OpenAI direta
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Fallback para Replit AI Integrations caso a chave não esteja disponível (segurança)
AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

if OPENAI_API_KEY and OPENAI_API_KEY != "dummy":
    client = OpenAI(api_key=OPENAI_API_KEY)
    MODEL = "gpt-4o" # Modelo estável para busca/browsing via API direta
else:
    client = OpenAI(
        api_key=AI_INTEGRATIONS_OPENAI_API_KEY,
        base_url=AI_INTEGRATIONS_OPENAI_BASE_URL
    )
    MODEL = "gpt-5"

class MarketIntelligenceEngine:
    def __init__(self):
        self.model = MODEL

    def normalize_text(self, text):
        if not text: return ""
        text = text.lower()
        text = unidecode(text)
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def scrape_realtime(self, product, days=30):
        print(f"Iniciando busca real-time (API Direta) para: {product}")
        
        # Prompt otimizado para o modelo gpt-4o com foco em busca
        prompt = f"""
        Search the internet for RECENT (last {days} days) consumer interest in Brazil regarding '{product}'.
        Find 5 specific mentions from social media (X/Twitter, Reddit), forums, or news.
        
        You MUST return a JSON object with this EXACT structure:
        {{
            "mentions": [
                {{
                    "text": "The post/mention content in Portuguese",
                    "source": "Source name",
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
                timeout=60.0
            )
            content = response.choices[0].message.content
            print(f"Resposta bruta da OpenAI: {content}")
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
            Analyze this mention for '{product}': "{m['text']}"
            Return JSON: {{ "intent_score": 0.0-1.0, "classification": "intent/research/neutral", "location": {{"city": "Name", "state": "UF"}} }}
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
                    if m.get('intent_score', 0) > 0.1:
                        results.append(m)
            except Exception as e:
                print(f"Error analyzing: {e}")
        return results

    def run_intelligence(self, product, keywords=None, days=30):
        raw_data = self.scrape_realtime(product, days)
        for item in raw_data:
            item['normalized_text'] = self.normalize_text(item['text'])
            
        if raw_data:
            df = pd.DataFrame(raw_data).drop_duplicates(subset=['normalized_text'])
            unique_data = df.to_dict('records')
        else:
            unique_data = []
        
        return self.analyze_mentions(unique_data, product)

if __name__ == "__main__":
    engine = MarketIntelligenceEngine()
    print(engine.run_intelligence("iPhone 15", days=7))
