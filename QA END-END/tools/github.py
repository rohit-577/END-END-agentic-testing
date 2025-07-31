from tools.logger import setup_logger

logger = setup_logger()

class GitHub:
    def fetch_pr_diff(self, pr_number):
        try:
            logger.info(f"Mock fetching PR diff for PR #{pr_number}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching PR diff: {str(e)}")
            raise