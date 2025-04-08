######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Recommendation Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Recommendation
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Recommendation, RecommendationType
from service.common import status  # HTTP Status Codes


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Recommendations REST API Service",
            version="1.0",
            paths=[
                (
                    {
                        "path": str(rule),
                        "methods": list(rule.methods),
                        "description": globals()[rule.endpoint].__doc__,
                    }
                )
                for rule in app.url_map.iter_rules()
                if rule.endpoint != "static"
            ],
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# CREATE A NEW RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendations():
    """
    Create a Recommendation
    This endpoint will create a recommendation based the data in the body that is posted
    """
    app.logger.info("Request to Create a Recommendation...")
    check_content_type("application/json")

    recommendation = Recommendation()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    recommendation.deserialize(data)

    # Check for duplicates before saving
    existing_rec = Recommendation.query.filter_by(
        product_a_sku=recommendation.product_a_sku,
        product_b_sku=recommendation.product_b_sku,
        recommendation_type=recommendation.recommendation_type,
    ).first()

    if existing_rec:
        app.logger.warning("Duplicate recommendation found")
        return (
            jsonify({"message": "Recommendation already exists"}),
            status.HTTP_409_CONFLICT,
        )

    # Save the new Pet to the database
    recommendation.create()
    app.logger.info("recommendation with new id [%s] saved!", recommendation.id)

    # Return the location of the new Pet
    location_url = url_for(
        "get_recommendations", recommendation_id=recommendation.id, _external=True
    )
    return (
        jsonify(recommendation.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# READ A RECOMMENDATION
######################################################################


@app.route("/recommendations/<int:recommendation_id>", methods=["GET"])
def get_recommendations(recommendation_id):
    """
    Retrieves a single Recommendation

    This endpoint will return a Recommendation based on its id
    """

    app.logger.info("Request for recommendation with id: %s", recommendation_id)

    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    app.logger.info("Returning recommendation: %s", recommendation_id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["PUT"])
def update_recommendations(recommendation_id):
    """
    Updates a Recommendation

    This endpoint will update a Recommendation based on the body that is passed
    """
    app.logger.info("Request to update recommendation with id: %s", recommendation_id)
    check_content_type("application/json")

    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    data = request.get_json()
    app.logger.info("Processing: %s", data)
    recommendation.deserialize(data)
    recommendation.id = recommendation_id
    recommendation.update()

    app.logger.info("Recommendation with ID: %s updated.", recommendation.id)
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# LIST ALL PETS
######################################################################
@app.route("/recommendations", methods=["GET"])
def list_recommendations():
    """Returns all of the Recommendations"""
    app.logger.info("Request for recommendation list")

    recommendations = []
    # See if any query filters were passed in
    a_sku = request.args.get("product_a_sku")
    recommendation_type = request.args.get("recommendation_type")

    if a_sku and recommendation_type:
        type_value = getattr(RecommendationType, recommendation_type.upper())
        recommendations = Recommendation.find_by_product_a_sku_and_type(
            a_sku, type_value
        )
    elif a_sku:
        recommendations = Recommendation.find_by_product_a_sku(a_sku)
    elif recommendation_type:
        type_value = getattr(RecommendationType, recommendation_type.upper())
        recommendations = Recommendation.find_by_type(type_value)
    else:
        recommendations = Recommendation.all()
    results = [recommendation.serialize() for recommendation in recommendations]
    app.logger.info("Returning %d recommendations", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# DELETE A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>", methods=["DELETE"])
def delete_recommendations(recommendation_id):
    """
    Deletes a Recommendation

    This endpoint will delete a Recommendation based the id specified in the path
    """
    app.logger.info("Request to delete recommendation with id: %s", recommendation_id)

    recommendation = Recommendation.find(recommendation_id)
    if recommendation:
        recommendation.delete()
        app.logger.info("Recommendation with ID: %s was deleted.", recommendation_id)
    return {}, status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
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

######################################################################
# INCREMENT LIKES FIELD FOR A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/like", methods=["PUT"])
def increment_like(recommendation_id):
    """
    Increment likes for a Recommendation
    This endpoint will increment the likes for the Recommendation with ID specified in URL
    """
    app.logger.info(
        "Request to increment recommendation's likes field with id: %d",
        recommendation_id,
    )

    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id: '{recommendation_id}' was not found.",
        )

    recommendation.add_like()

    app.logger.info(
        "Recommendation with ID: %d - likes field incremented.", recommendation.id
    )
    return jsonify(recommendation.serialize()), status.HTTP_200_OK


######################################################################
# DECREMENT LIKES FIELD FOR A RECOMMENDATION
######################################################################
@app.route("/recommendations/<int:recommendation_id>/like", methods=["DELETE"])
def decrement_like(recommendation_id):
    """
    Decrement likes for a Recommendation
    This endpoint will decrement the likes for the Recommendation with ID specified in URL
    """
    app.logger.info(
        "Request to decrement recommendation's likes field with id: %d",
        recommendation_id,
    )

    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id: '{recommendation_id}' was not found.",
        )

    recommendation.remove_like()

    app.logger.info(
        "Recommendation with ID: %d - likes field decremented.", recommendation.id
    )
    return jsonify(recommendation.serialize()), status.HTTP_200_OK