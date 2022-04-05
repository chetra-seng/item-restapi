import os
import traceback

from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs import image_helper
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @jwt_required(fresh=True)
    def post(self):
        """
        Used to upload an image file.
        If uses JWT to retrieve user information and then savees the image to the user's folder.
        If there's a filename conflict, it appends a number at the end.
        """
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        try:
            image_path = image_helper.save_image(data["image"], folder=folder)
            basename = image_helper.get_basename(image_path)
            return {"message": "Image <{}> uploaded".format(basename)}, 201
        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return {'message': "Extension <{}> is not allowed".format(extension)}, 400


class Image(Resource):
    @jwt_required()
    def get(self, filename: str):
        """
        Return the requested image if it exists. Look up inside the logged in user's folder
        """
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            return {"message": "Illegal file name <{}>".format(filename)}, 400
        try:
            return send_file(image_helper.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": "Image not found."}, 404
        
    @jwt_required()
    def delete(self, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_helper.is_filename_safe(filename):
            return {"message": "Illegal file name <{}>".format(filename)}, 400
        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {"message": "File deleted."}, 200
        except FileNotFoundError:
            return {"message": "Image not found."}, 404
        except:
            traceback.print_exc()
            return {"message": "Failed to delete image"}, 500
