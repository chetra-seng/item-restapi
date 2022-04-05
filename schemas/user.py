from ma import ma
from marshmallow.decorators import pre_dump
from models.user import UserModel


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        dump_only = ("id",)
        load_only = ("password", "confirmation", )
        load_instance = True

    @pre_dump
    def _pre_dump(self, user: UserModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user
