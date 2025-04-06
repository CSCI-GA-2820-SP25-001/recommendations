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
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from datetime import date
from wsgi import app
from service.models import (
    Recommendation,
    db,
    RecommendationType,
    DataValidationError,
    TextColumnLimitExceededError,
)
from tests.factories import RecommendationFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  B A S E   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCaseBase(TestCase):
    """Base Test Case for common setup"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Recommendation).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


######################################################################
#  R E C O M M E N D A T I O N S  M O D E L   T E S T   C A S E S
######################################################################
class TestPetModel(TestCaseBase):
    """Recommendation Model CRUD Tests"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    # def test_create_recommendation(self):
    #     """It should create a Recommendation"""
    #     # Todo: Remove this test case example
    #     recommendation = RecommendationFactory()
    #     recommendation.create()
    #     self.assertIsNotNone(recommendation.id)
    #     found = Recommendation.all()
    #     self.assertEqual(len(found), 1)
    #     data = Recommendation.find(recommendation.id)
    #     self.assertEqual(data.product_a_sku, recommendation.product_a_sku)
    #     self.assertEqual(data.product_b_sku, recommendation.product_b_sku)
    #     self.assertEqual(data.recommendation_type, recommendation.recommendation_type)
    #     self.assertEqual(data.likes, recommendation.likes)

    def test_recommendation_type_values(self):
        """It should contain all desired types of recommendation"""
        target_values = ["UP_SELL", "CROSS_SELL", "ACCESSORY", "BUNDLE"]
        values = [type.value for type in RecommendationType]
        for target_value in target_values:
            self.assertTrue(target_value in values)

    def test_create_a_recommendation(self):
        """It should Create a recommendation and assert that it exists"""
        recommendation = Recommendation(
            product_a_sku="AA0001",
            product_b_sku="AA0002",
            recommendation_type=RecommendationType.UP_SELL,
        )
        self.assertEqual(
            str(recommendation), "<Recommendation AA0001-AA0002 id=[None]>"
        )
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.product_a_sku, "AA0001")
        self.assertEqual(recommendation.product_b_sku, "AA0002")
        self.assertEqual(recommendation.recommendation_type, RecommendationType.UP_SELL)

        # test new recommendation
        recommendation = Recommendation(
            product_a_sku="AB1111",
            product_b_sku="BA2222",
            recommendation_type=RecommendationType.CROSS_SELL,
        )
        self.assertEqual(recommendation.product_a_sku, "AB1111")
        self.assertEqual(recommendation.product_b_sku, "BA2222")
        self.assertEqual(
            recommendation.recommendation_type, RecommendationType.CROSS_SELL
        )

    def test_add_a_recommendation(self):
        """It should create a recommendation and add it to the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendation(
            product_a_sku="A1",
            product_b_sku="B1",
            recommendation_type=RecommendationType.UP_SELL,
        )
        self.assertTrue(recommendation is not None)
        self.assertEqual(recommendation.id, None)
        recommendation.create()

        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(recommendation.id)
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].product_a_sku, "A1")
        self.assertEqual(recommendations[0].product_b_sku, "B1")
        self.assertEqual(
            recommendations[0].recommendation_type, RecommendationType.UP_SELL
        )

    def test_read_a_recommendation(self):
        """It should Read a Recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        recommendation.create()
        self.assertIsNotNone(recommendation.id)

        # Fetch it back
        found_recommendation = Recommendation.find(recommendation.id)
        self.assertEqual(found_recommendation.id, recommendation.id)
        self.assertEqual(
            found_recommendation.product_a_sku, recommendation.product_a_sku
        )
        self.assertEqual(
            found_recommendation.product_b_sku, recommendation.product_b_sku
        )
        self.assertEqual(
            found_recommendation.recommendation_type, recommendation.recommendation_type
        )

    def test_update_a_recommendation(self):
        """It should Update a Recommendation"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        recommendation.create()
        logging.debug(recommendation)
        self.assertIsNotNone(recommendation.id)

        # Change it and save it
        recommendation.product_a_sku = "ABC"
        original_id = recommendation.id
        recommendation.update()
        self.assertEqual(recommendation.id, original_id)
        self.assertEqual(recommendation.product_a_sku, "ABC")

        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, original_id)
        self.assertEqual(recommendations[0].product_a_sku, "ABC")

    def test_update_no_id(self):
        """It should not Update a Recommendation with no id"""
        recommendation = RecommendationFactory()
        logging.debug(recommendation)
        recommendation.id = None
        self.assertRaises(DataValidationError, recommendation.update)

    def test_delete_a_recommendation(self):
        """It should Delete a Recommendation"""
        recommendation = RecommendationFactory()
        recommendation.create()
        self.assertEqual(len(Recommendation.all()), 1)

        # delete the recommendation and make sure it isn't in the database
        recommendation.delete()
        self.assertEqual(len(Recommendation.all()), 0)

    def test_list_all_recommendations(self):
        """It should List all Recommendations in the database"""
        recommendations = Recommendation.all()
        self.assertEqual(recommendations, [])
        # Create 5 Recommendations
        for _ in range(5):
            recommendation = RecommendationFactory()
            recommendation.create()
        # See if we get back 5 recommendations
        recommendations = Recommendation.all()
        self.assertEqual(len(recommendations), 5)

    def test_serialize_recommendation(self):
        """It should serialize a Recommendation"""
        recommendation = RecommendationFactory()
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], recommendation.id)
        self.assertIn("product_a_sku", data)
        self.assertEqual(data["product_a_sku"], recommendation.product_a_sku)
        self.assertIn("product_b_sku", data)
        self.assertEqual(data["product_b_sku"], recommendation.product_b_sku)
        self.assertIn("recommendation_type", data)
        self.assertEqual(
            data["recommendation_type"], recommendation.recommendation_type.name
        )

    def test_deserialize_recommendation(self):
        """It should de-serialize a Recommendation"""
        data = RecommendationFactory().serialize()
        recommendation = Recommendation()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.product_a_sku, data["product_a_sku"])
        self.assertEqual(recommendation.product_b_sku, data["product_b_sku"])
        self.assertEqual(
            recommendation.recommendation_type,
            getattr(RecommendationType, data["recommendation_type"]),
        )
        self.assertEqual(recommendation.likes, data["likes"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Recommendation with missing data"""
        data = {"id": 1, "product_a_sku": "AA", "product_b_sku": "BB"}
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_long_sku(self):
        """It should not deserialize too long SKU attribute"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["product_a_sku"] = "A" * 30
        recommendation = Recommendation()
        with self.assertRaises(TextColumnLimitExceededError):
            recommendation.deserialize(data)

        # same check for product b
        data["product_a_sku"] = "A"
        data["product_b_sku"] = "B" * 30
        recommendation = Recommendation()
        with self.assertRaises(TextColumnLimitExceededError):
            recommendation.deserialize(data)

    def test_deserialize_bad_recommendation_type(self):
        """It should not deserialize a bad recommendation type attribute"""
        test_recommendation = RecommendationFactory()
        data = test_recommendation.serialize()
        data["recommendation_type"] = "cross_sale"  # wrong case
        recommendation = Recommendation()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_find_by_product_a_sku_and_type(self):
        """It should filter recommendations by product_a_sku and type and return them ordered by likes"""
        Recommendation(
            product_a_sku="SKU1",
            product_b_sku="SKU2",
            recommendation_type=RecommendationType.UP_SELL,
            likes=10,
        ).create()
        Recommendation(
            product_a_sku="SKU1",
            product_b_sku="SKU3",
            recommendation_type=RecommendationType.UP_SELL,
            likes=20,
        ).create()
        Recommendation(
            product_a_sku="SKU1",
            product_b_sku="SKU4",
            recommendation_type=RecommendationType.CROSS_SELL,
            likes=15,
        ).create()

        # Call the method under test
        results = Recommendation.find_by_product_a_sku_and_type(
            "SKU1", RecommendationType.UP_SELL
        )

        # Assert the results are as expected
        self.assertEqual(len(results), 2)
        self.assertTrue(
            all(
                rec.recommendation_type == RecommendationType.UP_SELL for rec in results
            )
        )
        self.assertEqual(
            results[0].product_b_sku, "SKU3"
        )  # Assuming the first result is the most liked
        self.assertEqual(results[1].product_b_sku, "SKU2")


######################################################################
#  T E S T   E X C E P T I O N   H A N D L E R S
######################################################################
class TestExceptionHandlers(TestCaseBase):
    """Recommendation Model Exception Handlers"""

    @patch("service.models.db.session.commit")
    def test_create_exception(self, exception_mock):
        """It should catch a create exception"""
        exception_mock.side_effect = Exception()
        recommendation = RecommendationFactory()
        self.assertRaises(DataValidationError, recommendation.create)

    @patch("service.models.db.session.commit")
    def test_update_exception(self, exception_mock):
        """It should catch a update exception"""
        exception_mock.side_effect = Exception()
        recommendation = RecommendationFactory()
        self.assertRaises(DataValidationError, recommendation.update)

    @patch("service.models.db.session.commit")
    def test_delete_exception(self, exception_mock):
        """It should catch a delete exception"""
        exception_mock.side_effect = Exception()
        recommendation = RecommendationFactory()
        self.assertRaises(DataValidationError, recommendation.delete)
