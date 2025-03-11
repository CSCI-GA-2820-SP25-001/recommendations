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
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################
# Todo: Place your REST API code here ...



######################################################################
# DELETE A RECOMMENDATION
######################################################################

@api.doc("delete_recommendations")
@api.response(204, "Recommendation deleted")
def delete(self, recommendation_id):
    """
    Deletes a Recommendation

    This endpoint will delete a Recommendation based the id specified in the path
    """
    app.logger.info(
        "Request to delete recommendation with id: %s", recommendation_id
    )

    recommendation = Recommendation.find(recommendation_id)
    if recommendation:
        recommendation.delete()
        app.logger.info(
            "Recommendation with ID: %s was deleted.", recommendation_id
        )
    delete_recommendations
    return "", status.HTTP_204_NO_CONTENT

  

######################################################################
# CREATE A NEW RECOMMENDATION
######################################################################
@app.route("/recommendations", methods=["POST"])
def create_recommendation():
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

    # Save the new Pet to the database
    recommendation.create()
    app.logger.info("recommendation with new id [%s] saved!", recommendation.id)

    # Return the location of the new Pet
    location_url = url_for("get_recommendations", pet_id=recommendation.id, _external=True)
    return jsonify(recommendation.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


  
######################################################################
# UPDATE A RECOMMENDATION
######################################################################
@api.doc("update_recommendations")
@api.response(404, "Recommendation with id was not found")
@api.response(400, "The Recommendation data was not valid")
@api.expect(create_model)
@api.marshal_with(recommendation_model)
def put(self, recommendation_id):
    """
    Updates a Recommendation

    This endpoint will update a Recommendation based on the body that is passed
    """
    app.logger.info(
        "Request to update recommendation with id: %s", recommendation_id
    )
    check_content_type("application/json")

    recommendation = Recommendation.find(recommendation_id)
    if not recommendation:
        error(
            status.HTTP_404_NOT_FOUND,
            f"Recommendation with id '{recommendation_id}' was not found.",
        )

    data = api.payload
    recommendation.deserialize(data)
    recommendation.id = recommendation_id
    recommendation.update()

    app.logger.info("Recommendation with ID: %s updated.", recommendation.id)
    return recommendation.serialize(), status.HTTP_200_OK

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
