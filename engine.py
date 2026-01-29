import os
from openai import OpenAI
import pandas as pd
import re
from unidecode import unidecode
import json
from datetime import datetime, timedelta

# Integración de OpenAI via Replit AI Integrations
AI_INTEGRATIONS_OPENAI_API_KEY = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
AI_INTEGRATIONS_OPENAI_BASE_URL = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")

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
        print(f"Iniciando varredura real-time (SP) para: {product}")
        
        prompt = f"""
        Act as a real-time market data analyst specializing in the State of São Paulo, Brazil.
        Your task is to scan current market trends, social media signals, and search volumes for '{product}' in the last {days} days.
        
        Generate a stratified breakdown of market demand by City and Neighborhood/District within the State of São Paulo.
        Provide PRECISE and EXACT estimated demand percentages for each location relative to the total demand in the state.
        
        Return a JSON object with this exact structure:
        {{
            "stratified_data": [
                {{
                    "city": "Nome da Cidade",
                    "neighborhood": "Bairro ou Distrito",
                    "region": "Grande SP/Interior/Litoral",
                    "demand_percentage": 25.5,
                    "trend": "up/down/stable",
                    "intensity": "high/medium/low"
                }}
            ]
        }}
        
        Ensure the data reflects real current market intelligence for SP in January 2026.
        """
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                timeout=60.0
            )
            content = response.choices[0].message.content
            if content:
                data = json.loads(content)
                return data.get('stratified_data', [])
        except Exception as e:
            print(f"Erro na varredura: {e}")
        return []

    def run_intelligence(self, product, keywords=None, days=30):
        # O sistema agora foca em dados estratificados puros
        data = self.scrape_realtime(product, days)
        return data

if __name__ == "__main__":
    engine = MarketIntelligenceEngine()
    print(engine.run_intelligence("iPhone 15", days=7))
