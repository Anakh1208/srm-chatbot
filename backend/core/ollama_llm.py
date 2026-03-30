import requests

class OllamaLLM:
    def __init__(self, model="gemma3:1b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )

            data = response.json()
            return data.get("response", "").strip()

        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return "Error generating response"