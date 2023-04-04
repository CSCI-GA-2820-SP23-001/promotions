"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, make_response, abort
from service.common import status  # HTTP Status Codes
from service.models import Promotion

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify({"status": "OK"}),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


# Place your REST API code here ...


@app.route("/health", methods=["GET"])
def health_endpoint():
    """Make a GET request to the /health endpoint of the service"""
    return (
        jsonify({"status": "OK"}),
        status.HTTP_200_OK,
    )


######################################################################
# ADD A NEW PROMOTION
######################################################################


@app.route("/promotions", methods=["POST"])
def create_promotions():
    """
    Creates a Promotion
    This endpoint will create a Promotion based the data in the body that is posted
    """
    app.logger.info("Request to create a promotion")
    check_content_type("application/json")
    promotion = Promotion()
    promotion.deserialize(request.get_json())
    promotion.create()
    message = promotion.serialize()

    location_url = url_for("get_promotion", promotion_id=promotion.id, _external=True)

    app.logger.info("Promotion with ID [%s] created.", promotion.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# DELETE A PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["DELETE"])
def delete_promotions(promotion_id):
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
# RETRIEVE A PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["GET"])
def get_promotion(promotion_id):
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
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING PROMOTION
######################################################################


@app.route("/promotions/<int:promotion_id>", methods=["PUT"])
def update_promotions(promotion_id):
    """
    Update a Promotion

    This endpoint will update a Promotion based the body that is posted
    """
    app.logger.info("Request to update promotion with id: %s", promotion_id)
    check_content_type("application/json")

    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    promotion.deserialize(request.get_json())
    promotion.id = promotion_id
    promotion.update()

    app.logger.info("Promotion with ID [%s] updated.", promotion.id)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# LIST PROMOTIONS
######################################################################


@app.route("/promotions", methods=["GET"])
def list_promotions():
    """Returns all of the Promotions"""
    app.logger.info("Request for Promotion list")
    promotions = []

    # Process the query string if any
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")
    if name:
        promotions = Promotion.find_by_name(name)
    elif category:
        promotions = Promotion.find_by_category(category)
    elif available:
        promotions = Promotion.find_by_availability(available)
    else:
        promotions = Promotion.all()

    # Return as an array of dictionaries
    results = [promotion.serialize() for promotion in promotions]

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# Activate PROMOTIONS
######################################################################


@app.route("/promotions/<int:promotion_id>/activate", methods=["PUT"])
def activate_promotions(promotion_id):
    """Activate one Promotion by Promotion ID"""
    app.logger.info("Request to activate promotion with id: %s", promotion_id)

    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    promotion.available = True
    promotion.update()

    app.logger.info("Promotion with ID [%s] updated.", promotion.id)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
# Deactivate PROMOTIONS
######################################################################


@app.route("/promotions/<int:promotion_id>/deactivate", methods=["PUT"])
def deactivate_promotions(promotion_id):
    """Deactivate one Promotion by Promotion ID"""
    app.logger.info("Request to deactivate promotion with id: %s", promotion_id)

    promotion = Promotion.find(promotion_id)
    if not promotion:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Promotion with id '{promotion_id}' was not found.",
        )

    promotion.available = False
    promotion.update()

    app.logger.info("Promotion with ID [%s] updated.", promotion.id)
    return jsonify(promotion.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
