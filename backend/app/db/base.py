from app.db.session import Base

# Import models so SQLAlchemy registers them with Base metadata.
from app.models.restaurant import Restaurant  # noqa: F401
from app.models.menu import Menu  # noqa: F401
from app.models.dish import Dish  # noqa: F401
from app.models.ingredient import Ingredient  # noqa: F401
from app.models.dish_ingredient import DishIngredient  # noqa: F401
from app.models.ingredient_price import IngredientPrice  # noqa: F401
from app.models.distributor import Distributor  # noqa: F401
from app.models.distributor_ingredient import DistributorIngredient  # noqa: F401
from app.models.rfp import RFP  # noqa: F401
from app.models.rfp_ingredient import RFPIngredient  # noqa: F401
from app.models.quote import Quote  # noqa: F401
from app.models.quote_line_item import QuoteLineItem  # noqa: F401
