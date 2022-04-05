from ma import ma
from models.item import ItemModel

class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItemModel
        load_instance = True
        load_only = ("store",)
        dump_only = ("id",)
        include_fk = True