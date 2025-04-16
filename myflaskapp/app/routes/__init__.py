from .auth import auth_bp
from .item import item_bp
from .productdatafetcher import product_bp

# Make sure you are exposing these variables for imports
__all__ = ['auth_bp', 'item_bp', 'product_bp']
