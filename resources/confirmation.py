import time
import traceback

from flask.helpers import make_response
from flask.templating import render_template
from flask_restful import Resource
from libs.mailgun import MailGunException

from models.confirmation import ConfirmationModel
from models.user import UserModel
from resources.user import USER_NOT_FOUND
from schemas.confirmation import ConfirmationSchema

NOT_FOUND = "Confirmation not found"
EXPIRED = "Confirmation expired"
ALREADY_CONFIRMED = "Registeration has already been confirmed"
RESEND_SUCCESSFUL = "A new confirmation email has been sent successfully."
RESEND_FAIL = "Fail to send a new confirmation email."

confirmation_list_schema = ConfirmationSchema(many=True)


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {"message": NOT_FOUND}, 404
        if confirmation.expired:
            return {"message": EXPIRED}, 400
        if confirmation.confirmed:
            return {"message": ALREADY_CONFIRMED}, 400
        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {"Content-Type": "text/html"}
        return make_response(
            render_template("confirmation_page.html", email=confirmation.user.email),
            200,
            headers
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):  # Return all user confirmation detailed used for testing only!!
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return(
            {
                "current_time": int(time.time()),
                "confirmation": confirmation_list_schema.dump(user.confirmation.order_by(ConfirmationModel.expire_at))
            },
            200
        )

    @classmethod
    def post(cls, user_id: int):
        """Resend confirmation email"""
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {"message": ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {"message": RESEND_SUCCESSFUL}
        except MailGunException as me:
            return {"message": str(me)}, 500
        except:
            traceback.print_exc()
            return {"message": RESEND_FAIL}, 500
