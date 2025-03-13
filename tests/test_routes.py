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
TestRecommendation API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Recommendation
from tests.factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/recommendations"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestRecommendationService(TestCase):
    """Recommendation Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ############################################################
    # Utility function to bulk create pets
    ############################################################
    def _create_recommendations(self, count):
        """Factory method to create recommendations in bulk"""
        recommendations = []
        for _ in range(count):
            test_recommendation = RecommendationFactory()
            response = self.client.post(BASE_URL, json=test_recommendation.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test recommendation",
            )
            new_recommendation = response.get_json()
            test_recommendation.id = new_recommendation["id"]
            recommendations.append(test_recommendation)
        return recommendations

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("name", resp.json)
        self.assertIn("version", resp.json)
        self.assertIn("paths", resp.json)
        self.assertEqual(
            len(list(resp.json["paths"])),
            len(
                list(
                    filter(
                        lambda rule: rule.endpoint != "static", app.url_map.iter_rules()
                    )
                )
            ),
        )

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_recommendation_list(self):
        """It should Get a list of Recommendations"""
        self._create_recommendations(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_recommendation(self):
        """It should Create a new Recommendation"""
        test_rec = RecommendationFactory()
        logging.debug("Test Recommendation: %s", test_rec.serialize())
        response = self.client.post(BASE_URL, json=test_rec.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_rec = response.get_json()
        self.assertIsInstance(new_rec["id"], int)
        self.assertEqual(new_rec["product_a_sku"], test_rec.product_a_sku)
        self.assertEqual(new_rec["product_b_sku"], test_rec.product_b_sku)
        self.assertEqual(
            new_rec["recommendation_type"], test_rec.recommendation_type.name
        )
        self.assertEqual(new_rec["likes"], test_rec.likes)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_rec_data = response.get_json()
        self.assertEqual(new_rec_data["product_a_sku"], test_rec.product_a_sku)
        self.assertEqual(new_rec_data["product_b_sku"], test_rec.product_b_sku)
        self.assertEqual(
            new_rec_data["recommendation_type"], test_rec.recommendation_type.name
        )
        self.assertEqual(new_rec_data["likes"], test_rec.likes)

    def test_create_recommendation_duplicate(self):
        """It should not create a duplicate Recommendation"""
        recommendation_data = RecommendationFactory().serialize()
        # Create the first recommendation, which should succeed
        response = self.client.post(BASE_URL, json=recommendation_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Attempt to create a duplicate recommendation, which should fail
        response = self.client.post(BASE_URL, json=recommendation_data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn("Recommendation already exists", response.get_json()["message"])

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_recommendation(self):
        """It should Get a single Recommendation"""
        # get the id of a recommendation
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["product_a_sku"], test_recommendation.product_a_sku)
        self.assertEqual(data["product_b_sku"], test_recommendation.product_b_sku)
        self.assertEqual(
            data["recommendation_type"], test_recommendation.recommendation_type.name
        )

    def test_get_recommendation_not_found(self):
        """It should not Get a Recommendation thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_recommendation(self):
        """It should Update an existing Recommendation"""
        # create a recommendation to update
        test_recommendation = RecommendationFactory()
        response = self.client.post(BASE_URL, json=test_recommendation.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the recommendation
        new_recommendation = response.get_json()
        logging.debug(new_recommendation)
        new_recommendation["product_a_sku"] = "unknown"
        response = self.client.put(
            f"{BASE_URL}/{new_recommendation['id']}", json=new_recommendation
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_recommendation = response.get_json()
        self.assertEqual(updated_recommendation["product_a_sku"], "unknown")

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_recommendation(self):
        """It should Delete a Recommendation"""
        test_recommendation = self._create_recommendations(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_recommendation.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_recommendation(self):
        """It should Delete a recommendation even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_data_validation_error(self):
        """It should not create recommendation if giving invalid data"""
        # test missing field
        invalid_data = {
            "product_a_sku": "123",
            "product_b_sku": None,
            "recommendation_type": "UP_SELL",
        }
        response = self.client.post(BASE_URL, json=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.get_json())
        self.assertEqual(response.get_json()["error"], "Bad Request")

        # test invalid recommendation_type
        invalid_data = {
            "product_a_sku": "123",
            "product_b_sku": "123",
            "recommendation_type": "InvalidType",
        }
        response = self.client.post(BASE_URL, json=invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.get_json())
        self.assertEqual(response.get_json()["error"], "Bad Request")
        self.assertIn(
            "Invalid value for RecommendationType: InvalidType",
            response.get_json()["message"],
        )


######################################################################
#  T E S T   S A D   P A T H S
######################################################################
class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()

    def test_method_not_allowed(self):
        """It should not allow update without a Recommendation id"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_recommendation_no_data(self):
        """It should not Create a Recommendation with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recommendation_no_content_type(self):
        """It should not Create a Recommendation with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_recommendation_wrong_content_type(self):
        """It should not Create a Recommendation with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
