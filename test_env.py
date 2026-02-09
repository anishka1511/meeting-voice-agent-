from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("DEEPGRAM_API_KEY"))