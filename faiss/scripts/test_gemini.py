from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

res = client.models.embed_content(
    model="models/text-embedding-004",
    contents="test query",
)

print(len(res.embeddings[0].values))
