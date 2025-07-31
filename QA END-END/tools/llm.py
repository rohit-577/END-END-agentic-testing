from tools.llm_utils import get_llm_response
from tools.logger import setup_logger

logger = setup_logger()

class LLM:
    def generate(self, prompt):
        try:
            response = get_llm_response(prompt)
            logger.info("LLM response generated successfully")
            return response
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise