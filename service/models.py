"""
Models for Recommendation

All of the models are stored in this module
"""

import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint


logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class PrimaryKeyNotSetError(Exception):
    """Used when tried to set primary key to None"""


class TextColumnLimitExceededError(Exception):
    """Used when column character limit has been exceeded"""


class RecommendationType(Enum):
    """Enum representing types of recommendation"""

    UP_SELL = "UP_SELL"
    CROSS_SELL = "CROSS_SELL"
    ACCESSORY = "ACCESSORY"
    BUNDLE = "BUNDLE"


class Recommendation(db.Model):
    """
    Class that represents a Recommendation
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    product_a_sku = db.Column(db.String(25), nullable=False)
    product_b_sku = db.Column(db.String(25), nullable=False)
    recommendation_type = db.Column(db.Enum(RecommendationType), nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    __table_args__ = (
        UniqueConstraint(
            "product_a_sku",
            "product_b_sku",
            "recommendation_type",
            name="unique_recommendation",
        ),
    )

    name = db.column_property(product_a_sku + "-" + product_b_sku)

    def __repr__(self):
        return f"<Recommendation {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Recommendation to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Recommendation from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Recommendation into a dictionary"""
        return {
            "id": self.id,
            "product_a_sku": self.product_a_sku,
            "product_b_sku": self.product_b_sku,
            "recommendation_type": self.recommendation_type.name,
            "likes": self.likes,
        }

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_a_sku = self._validate_sku(
                data.get("product_a_sku"), "product_a_sku"
            )
            self.product_b_sku = self._validate_sku(
                data.get("product_b_sku"), "product_b_sku"
            )

            self.recommendation_type = self._validate_enum(
                data.get("recommendation_type"), RecommendationType
            )

            self.likes = self._validate_likes(data.get("likes", 0))
        except AttributeError as error:
            raise DataValidationError(f"Invalid attribute: {error.args[0]}") from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Recommendations in the database"""
        logger.info("Processing all Recommendations")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Recommendation by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Recommendations with the given name

        Args:
            name (string): the name of the Recommendations you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @staticmethod
    def _validate_sku(value, field_name):
        """Ensures SKU values are within the character limit."""
        if not value or len(value) > 25:
            raise TextColumnLimitExceededError(f"{field_name} exceeds limit")
        return value

    @staticmethod
    def _validate_enum(value, enum_type):
        """Validates enum fields from a string."""
        if not value or value.upper() not in enum_type.__members__:
            raise DataValidationError(
                f"Invalid value for {enum_type.__name__}: {value}"
            )
        return enum_type[value.upper()]

    @staticmethod
    def _validate_likes(value):
        """Ensures likes are non-negative integers."""
        if not isinstance(value, int) or value < 0:
            raise DataValidationError(f"Invalid likes value: {value}")
        return value
