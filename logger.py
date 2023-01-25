import logging
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    handlers=[
                        logging.FileHandler(
                            'bypass.log', mode='w'),
                        logging.StreamHandler(
                            sys.stdout)
                    ]
                    )

log = logging.getLogger(__name__)
