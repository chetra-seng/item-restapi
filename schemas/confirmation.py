from ma import ma
from models.confirmation import ConfirmationModel

class ConfirmationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConfirmationModel
        load_only = ("user",)
        dump_only = ("expire_at", "confirmed", "id")
        include_fk = True
        load_instance = True
