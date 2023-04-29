"""
My Service

Describe what your service does here
"""

# pylint: disable=wrong-import-position
import sys  # noqa: F401, E402
import secrets  # noqa: F401, E402
import logging  # noqa: F401, E402
from functools import wraps
from flask import jsonify, request, url_for, render_template, make_response, abort  # noqa: F401, E402
from flask_restx import Api, Resource, fields, reqparse, inputs  # noqa: F401, E402
from service.common import status  # HTTP Status Codes
from service.models import Promotion, Promotype
from . import app, api

# Import Flask application


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model('Promotion', {
    'name': fields.String(required=True,
                          description='The name of the Promotion'),
    'category': fields.String(required=True,
                              description='The category of Promotion (e.g., holiday, friends_and_family, seasonal, etc.)'),
    'available': fields.Boolean(required=True,
                                description='Is the Promotion available for purchase?'),
    'promotype': fields.String(enum=Promotype._member_names_, description='The types of the Promotion')
})

promotion_model = api.inherit(
    'PromotionModel',
    create_model,
    {
        'id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service'),
    }
)

# query string arguments
promotion_args = reqparse.RequestParser()
promotion_args.add_argument('name', type=str, location='args', required=False, help='List Promotions by name')
promotion_args.add_argument('category', type=str, location='args', required=False, help='List Promotions by category')
promotion_args.add_argument('available',
                            type=inputs.boolean, location='args', required=False, help='List Promotions by availability')


######################################################################
# Authorization Decorator
######################################################################
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'X-Api-Key' in request.headers:
            token = request.headers['X-Api-Key']

        if app.config.get('API_KEY') and app.config['API_KEY'] == token:
            return f(*args, **kwargs)
        else:
            return {'message': 'Invalid or missing token'}, 401
    return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """ Helper function used when testing API keys """
    return "133b94898f9b6c07ede6296e0ec197f7"


######################################################################
#  PATH: /promotions/{id}
######################################################################
@api.route('/promotions/<promotion_id>')
@api.param('promotion_id', 'The Promotion identifier')
class PromotionResource(Resource):
    """
    PromotionResource class

    Allows the manipulation of a single Promotion
    GET /promotion{id} - Returns a Promotion with the id
    PUT /promotion{id} - Update a Promotion with the id
    DELETE /promotion{id} -  Deletes a Promotion with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc('get_promotions')
    @api.response(404, 'Promotion not found')
    @api.marshal_with(promotion_model)
    def get(self, promotion_id):
        """
        Retrieve a single Promotion
        This endpoint will return a Promotion based on it's id
        """
        app.logger.info("Request for promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                "Promotion with id '{promotion_id}' was not found.",
            )

        app.logger.info("Returning promotion: %s", promotion.name)
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PROMOTION
    # ------------------------------------------------------------------
    @api.doc('update_promotions', security='apikey')
    @api.response(404, 'Promotion not found')
    @api.response(400, 'The posted Promotion data was not valid')
    @api.expect(promotion_model)
    @api.marshal_with(promotion_model)
    @token_required
    def put(self, promotion_id):
        """
        Update a Promotion

        This endpoint will update a Promotion based the body that is posted
        """
        app.logger.info("Request to update promotion with id: %s", promotion_id)

        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Promotion with id '{promotion_id}' was not found.",
            )

        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        promotion.deserialize(data)
        promotion.id = promotion_id
        promotion.update()

        app.logger.info("Promotion with ID [%s] updated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PROMOTION
    # ------------------------------------------------------------------
    @api.doc('delete_promotions', security='apikey')
    @api.response(204, 'Promotion deleted')
    @token_required
    def delete(self, promotion_id):
        """
        deletes a Promotion
        This endpoint will delete a Promotion based on its id
        """
        app.logger.info("Request to delete promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            return "", status.HTTP_204_NO_CONTENT
        promotion.delete()
        app.logger.info("Promotion with id '%s' deleted.", promotion_id)
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /promotions
######################################################################
@api.route('/promotions', strict_slashes=False)
class PromotionCollection(Resource):
    """ Handles all interactions with collections of Promotions """
    # ------------------------------------------------------------------
    # LIST ALL PROMOTIONS
    # ------------------------------------------------------------------
    @api.doc('list_promotions')
    @api.expect(promotion_args, validate=True)
    @api.marshal_list_with(promotion_model)
    def get(self):
        """Returns all of the Promotions"""
        app.logger.info("Request for Promotion list")
        promotions = []

        args = promotion_args.parse_args()
        # Process the query string if any
        if args['name']:
            app.logger.info('Filtering by name: %s', args['name'])
            promotions = Promotion.find_by_name(args['name'])
        elif args['category']:
            app.logger.info('Filtering by category: %s', args['category'])
            promotions = Promotion.find_by_category(args['category'])
        elif args['available'] is not None:
            app.logger.info('Filtering by availability: %s', args['available'])
            promotions = Promotion.find_by_availability(args['available'])
        else:
            app.logger.info('Returning unfiltered list.')
            promotions = Promotion.all()

        # Return as an array of dictionaries
        # app.logger.info('Promotions returned' + str(promotions))
        results = [promotion.serialize() for promotion in promotions]

        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PROMOTION
    # ------------------------------------------------------------------
    @api.doc('create_promotions', security='apikey')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model)
    @api.marshal_with(promotion_model, code=201)
    @token_required
    def post(self):
        """
        Creates a Promotion
        This endpoint will create a Promotion based the data in the body that is posted
        """
        app.logger.info("Request to create a promotion")
        promotion = Promotion()
        app.logger.debug('Payload = %s', api.payload)
        promotion.deserialize(api.payload)
        promotion.create()

        location_url = api.url_for(PromotionResource, promotion_id=promotion.id, _external=True)

        app.logger.info("Promotion with ID [%s] created.", promotion.id)
        return promotion.serialize(), status.HTTP_201_CREATED, {'Location': location_url}


######################################################################
#  PATH: /promotions/{id}/activate
######################################################################
@api.route('/promotions/<promotion_id>/activate')
@api.param('promotion_id', 'The Promotion identifier')
class ActivateResource(Resource):
    """Activate one Promotion by Promotion ID"""
    @api.doc('activate_promotions')
    @api.response(404, 'Promotion not found')
    # @api.response(409, 'The Promotion is not available for activate')
    def put(self, promotion_id):
        """
        Activate a Promotion

        This endpoint will activate a Promotion by making it available
        """
        app.logger.info("Request to activate promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                 status.HTTP_404_NOT_FOUND,
                 f"Promotion with id '{promotion_id}' was not found.",
                 )
        promotion.available = True
        promotion.update()
        app.logger.info("Promotion with ID [%s] activated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /promotions/{id}/deactivate
######################################################################
@api.route('/promotions/<promotion_id>/deactivate')
@api.param('promotion_id', 'The Promotion identifier')
class DeactivateResource(Resource):
    """Activate one Promotion by Promotion ID"""
    @api.doc('activate_promotions')
    @api.response(404, 'Promotion not found')
    # @api.response(409, 'The Promotion is not available for activate')
    def put(self, promotion_id):
        """
        Deactivate a Promotion

        This endpoint will deactivate a Promotion by making it unavailable
        """
        app.logger.info("Request to deactivate promotion with id: %s", promotion_id)
        promotion = Promotion.find(promotion_id)
        if not promotion:
            abort(
                 status.HTTP_404_NOT_FOUND,
                 f"Promotion with id '{promotion_id}' was not found.",
                 )
        promotion.available = False
        promotion.update()
        app.logger.info("Promotion with ID [%s] deactivated.", promotion.id)
        return promotion.serialize(), status.HTTP_200_OK

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


@app.route("/health", methods=["GET"])
def health_endpoint():
    """Make a GET request to the /health endpoint of the service"""
    return (
        jsonify({"status": "OK"}),
        status.HTTP_200_OK,
    )


# ######################################################################
# # ADD A NEW PROMOTION
# ######################################################################


# @app.route("/promotions", methods=["POST"])
# def create_promotions():
#     """
#     Creates a Promotion
#     This endpoint will create a Promotion based the data in the body that is posted
#     """
#     app.logger.info("Request to create a promotion")
#     check_content_type("application/json")
#     promotion = Promotion()
#     promotion.deserialize(request.get_json())
#     promotion.create()
#     message = promotion.serialize()

#     location_url = url_for("get_promotion", promotion_id=promotion.id, _external=True)

#     app.logger.info("Promotion with ID [%s] created.", promotion.id)
#     return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


# ######################################################################
# # DELETE A PROMOTION
# ######################################################################


# @app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
# def delete_promotions(promotion_id):
#     """
#     deletes a Promotion
#     This endpoint will delete a Promotion based on its id
#     """
#     app.logger.info("Request to delete promotion with id: %s", promotion_id)
#     promotion = Promotion.find(promotion_id)
#     if not promotion:
#         return "", status.HTTP_204_NO_CONTENT
#     promotion.delete()
#     app.logger.info("Promotion with id '%s' deleted.", promotion_id)
#     return "", status.HTTP_204_NO_CONTENT


# ######################################################################
# # RETRIEVE A PROMOTION
# ######################################################################


# @app.route("/promotions/<int:promotion_id>", methods=["GET"])
# def get_promotion(promotion_id):
#     """
#     Retrieve a single Promotion
#     This endpoint will return a Promotion based on it's id
#     """
#     app.logger.info("Request for promotion with id: %s", promotion_id)
#     promotion = Promotion.find(promotion_id)
#     if not promotion:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             "Promotion with id '{promotion_id}' was not found.",
#         )

#     app.logger.info("Returning promotion: %s", promotion.name)
#     return jsonify(promotion.serialize()), status.HTTP_200_OK


# ######################################################################
# # UPDATE AN EXISTING PROMOTION
# ######################################################################


# @app.route("/promotions/<int:promotion_id>", methods=["PUT"])
# def update_promotions(promotion_id):
#     """
#     Update a Promotion

#     This endpoint will update a Promotion based the body that is posted
#     """
#     app.logger.info("Request to update promotion with id: %s", promotion_id)
#     check_content_type("application/json")

#     promotion = Promotion.find(promotion_id)
#     if not promotion:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Promotion with id '{promotion_id}' was not found.",
#         )

#     promotion.deserialize(request.get_json())
#     promotion.id = promotion_id
#     promotion.update()

#     app.logger.info("Promotion with ID [%s] updated.", promotion.id)
#     return jsonify(promotion.serialize()), status.HTTP_200_OK


# ######################################################################
# # LIST PROMOTIONS
# ######################################################################


# @app.route("/promotions", methods=["GET"])
# def list_promotions():
#     """Returns all of the Promotions"""
#     app.logger.info("Request for Promotion list")
#     promotions = []

#     # Process the query string if any
#     name = request.args.get("name")
#     category = request.args.get("category")
#     available = request.args.get("available")
#     if name:
#         promotions = Promotion.find_by_name(name)
#     elif category:
#         promotions = Promotion.find_by_category(category)
#     elif available:
#         promotions = Promotion.find_by_availability(available)
#     else:
#         promotions = Promotion.all()

#     # Return as an array of dictionaries
#     results = [promotion.serialize() for promotion in promotions]

#     return make_response(jsonify(results), status.HTTP_200_OK)


# ######################################################################
# # Activate PROMOTIONS
# ######################################################################


# @app.route("/promotions/<int:promotion_id>/activate", methods=["PUT"])
# def activate_promotions(promotion_id):
#     """Activate one Promotion by Promotion ID"""
#     app.logger.info("Request to activate promotion with id: %s", promotion_id)

#     promotion = Promotion.find(promotion_id)
#     if not promotion:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Promotion with id '{promotion_id}' was not found.",
#         )

#     promotion.available = True
#     promotion.update()

#     app.logger.info("Promotion with ID [%s] updated.", promotion.id)
#     return jsonify(promotion.serialize()), status.HTTP_200_OK


# ######################################################################
# # Deactivate PROMOTIONS
# ######################################################################


# @app.route("/promotions/<int:promotion_id>/deactivate", methods=["PUT"])
# def deactivate_promotions(promotion_id):
#     """Deactivate one Promotion by Promotion ID"""
#     app.logger.info("Request to deactivate promotion with id: %s", promotion_id)

#     promotion = Promotion.find(promotion_id)
#     if not promotion:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Promotion with id '{promotion_id}' was not found.",
#         )

#     promotion.available = False
#     promotion.update()

#     app.logger.info("Promotion with ID [%s] updated.", promotion.id)
#     return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


# def check_content_type(content_type):
#     """Checks that the media type is correct"""
#     if "Content-Type" not in request.headers:
#         app.logger.error("No Content-Type specified.")
#         abort(
#             status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#             f"Content-Type must be {content_type}",
#         )

#     if request.headers["Content-Type"] == content_type:
#         return

#     app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
#     abort(
#         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#         f"Content-Type must be {content_type}",
#     )
