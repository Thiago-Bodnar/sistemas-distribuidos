"""Config do logging """
import logging
import sys

def setup_logging(level: int = logging.INFO):
    """Configura o logging da aplicação."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

