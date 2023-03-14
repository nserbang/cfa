import logging
from django.conf import settings
import inspect
#logger = logging.getLogger(__name__)

log = logging.getLogger(__name__)
calling_function = inspect.stack()[1][3]
logging.basicConfig(
    format='%(asctime)s %(levelname)s [%(funcName)s:%(lineno)d] %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler('api.log')],
)

