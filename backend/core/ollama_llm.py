import requests

class OllamaLLM:
    def __init__(self, model="gemma3:1b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        try:
            print("\n🧠 Sending prompt to Ollama...")
            
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )

            # 🔥 Check if request failed
            if response.status_code != 200:
                print(f"❌ Ollama HTTP Error: {response.status_code}")
                print("Response:", response.text)
                return ""

            data = response.json()

            # 🔥 Debug output
            print("📥 Raw Ollama response:", data)

            output = data.get("response", "").strip()

            if not output:
                print("⚠️ Empty response from Ollama")
                return ""

            print("✅ Ollama responded successfully")
            return output

        except requests.exceptions.ConnectionError:
            print("❌ Ollama is NOT running on localhost:11434")
            return ""

        except requests.exceptions.Timeout:
            print("❌ Ollama request timed out")
            return ""

        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return ""