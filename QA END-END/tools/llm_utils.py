from tools.logger import setup_logger
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load .env and setup logger
load_dotenv()
logger = setup_logger()

def get_llm_response(prompt):
    try:
        # Get the key from the environment
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        # Use completions for text-davinci-003
        response = client.completions.create(
            model="gpt-4.1-nano",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].text.strip()

    except Exception as e:
        logger.error(f"Error in LLM response: {str(e)}")
        return "Mock LLM response"
