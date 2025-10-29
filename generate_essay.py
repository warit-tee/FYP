import os
from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions

load_dotenv()

TOPICS = [
    "Effects of social media on youth",
    "how to fix a broken fan",
    "summary of harry potter and the philosopher stone",
    "the ethics of artificial intelligence",
    "my favourite childhood cartoon"
]

LENGTH = [
    "200-300 words",
    "400-600 words",
    "800-1000 words"
]

MODEL = [
    "GPT",
    "GEMINI"
]


api_key = os.getenv("VERTEX_API_KEY")

client = genai.Client(vertexai=True, api_key=api_key)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?",
)
print(response)
