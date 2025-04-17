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
Recommendations Steps

Steps file for Recommendations.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following recommendations")
def step_impl(context):
    """Delete all Recommendations and load new ones"""

    # Get a list all of the pets
    rest_endpoint = f"{context.base_url}/recommendations"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    assert context.resp.status_code == HTTP_200_OK
    # and delete them one by one
    for recommendation in context.resp.json():
        recommendation_id = recommendation["id"]
        context.resp = requests.delete(
            f"{rest_endpoint}/{recommendation_id}", timeout=WAIT_TIMEOUT
        )
        assert context.resp.status_code == HTTP_204_NO_CONTENT

    # load the database with new Recommendations
    for row in context.table:
        payload = {
            "product_a_sku": row["product_a_sku"],
            "product_b_sku": row["product_b_sku"],
            "recommendation_type": row["recommendation_type"],
            "likes": int(row["likes"]),
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        assert context.resp.status_code == HTTP_201_CREATED
