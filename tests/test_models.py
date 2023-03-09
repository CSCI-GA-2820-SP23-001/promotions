# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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

"""
Test cases for Promotion Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_promotions.py:TestPromotionModel

"""
import os
import logging
import unittest
from datetime import date
from werkzeug.exceptions import NotFound
from service.models import Promotion, Gender, DataValidationError, db
from service import app
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  P E T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPromotionModel(unittest.TestCase):
    """Test Cases for Promotion Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Promotion.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_promotion(self):
        """It should Create a promotion and assert that it exists"""
        promotion = Promotion(name="Fido", category="dog",
                              available=True, gender=Gender.MALE)
        self.assertEqual(str(promotion), "<Promotion Fido id=[None]>")
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.name, "Fido")
        self.assertEqual(promotion.category, "dog")
        self.assertEqual(promotion.available, True)
        self.assertEqual(promotion.gender, Gender.MALE)
        promotion = Promotion(name="Fido", category="dog",
                              available=False, gender=Gender.FEMALE)
        self.assertEqual(promotion.available, False)
        self.assertEqual(promotion.gender, Gender.FEMALE)

    def test_add_a_promotion(self):
        """It should Create a promotion and add it to the database"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        promotion = Promotion(name="Fido", category="dog",
                              available=True, gender=Gender.MALE)
        self.assertTrue(promotion is not None)
        self.assertEqual(promotion.id, None)
        promotion.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(promotion.id)
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)

    def test_read_a_promotion(self):
        """It should Read a Promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        promotion.create()
        self.assertIsNotNone(promotion.id)
        # Fetch it back
        found_promotion = Promotion.find(promotion.id)
        self.assertEqual(found_promotion.id, promotion.id)
        self.assertEqual(found_promotion.name, promotion.name)
        self.assertEqual(found_promotion.category, promotion.category)

    def test_update_a_promotion(self):
        """It should Update a Promotion"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        promotion.create()
        logging.debug(promotion)
        self.assertIsNotNone(promotion.id)
        # Change it an save it
        promotion.category = "k9"
        original_id = promotion.id
        promotion.update()
        self.assertEqual(promotion.id, original_id)
        self.assertEqual(promotion.category, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0].id, original_id)
        self.assertEqual(promotions[0].category, "k9")

    def test_update_no_id(self):
        """It should not Update a Promotion with no id"""
        promotion = PromotionFactory()
        logging.debug(promotion)
        promotion.id = None
        self.assertRaises(DataValidationError, promotion.update)

    def test_delete_a_promotion(self):
        """It should Delete a Promotion"""
        promotion = PromotionFactory()
        promotion.create()
        self.assertEqual(len(Promotion.all()), 1)
        # delete the promotion and make sure it isn't in the database
        promotion.delete()
        self.assertEqual(len(Promotion.all()), 0)

    def test_list_all_promotions(self):
        """It should List all Promotions in the database"""
        promotions = Promotion.all()
        self.assertEqual(promotions, [])
        # Create 5 Promotions
        for _ in range(5):
            promotion = PromotionFactory()
            promotion.create()
        # See if we get back 5 promotions
        promotions = Promotion.all()
        self.assertEqual(len(promotions), 5)

    def test_serialize_a_promotion(self):
        """It should serialize a Promotion"""
        promotion = PromotionFactory()
        data = promotion.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], promotion.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], promotion.name)
        self.assertIn("category", data)
        self.assertEqual(data["category"], promotion.category)
        self.assertIn("available", data)
        self.assertEqual(data["available"], promotion.available)
        self.assertIn("gender", data)
        self.assertEqual(data["gender"], promotion.gender.name)
        self.assertIn("birthday", data)
        self.assertEqual(date.fromisoformat(
            data["birthday"]), promotion.birthday)

    def test_deserialize_a_promotion(self):
        """It should de-serialize a Promotion"""
        data = PromotionFactory().serialize()
        promotion = Promotion()
        promotion.deserialize(data)
        self.assertNotEqual(promotion, None)
        self.assertEqual(promotion.id, None)
        self.assertEqual(promotion.name, data["name"])
        self.assertEqual(promotion.category, data["category"])
        self.assertEqual(promotion.available, data["available"])
        self.assertEqual(promotion.gender.name, data["gender"])
        self.assertEqual(promotion.birthday,
                         date.fromisoformat(data["birthday"]))

    def test_deserialize_missing_data(self):
        """It should not deserialize a Promotion with missing data"""
        data = {"id": 1, "name": "Kitty", "category": "cat"}
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not deserialize a bad available attribute"""
        test_promotion = PromotionFactory()
        data = test_promotion.serialize()
        data["available"] = "true"
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_deserialize_bad_gender(self):
        """It should not deserialize a bad gender attribute"""
        test_promotion = PromotionFactory()
        data = test_promotion.serialize()
        data["gender"] = "male"  # wrong case
        promotion = Promotion()
        self.assertRaises(DataValidationError, promotion.deserialize, data)

    def test_find_promotion(self):
        """It should Find a Promotion by ID"""
        promotions = PromotionFactory.create_batch(5)
        for promotion in promotions:
            promotion.create()
        logging.debug(promotions)
        # make sure they got saved
        self.assertEqual(len(Promotion.all()), 5)
        # find the 2nd promotion in the list
        promotion = Promotion.find(promotions[1].id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promotions[1].id)
        self.assertEqual(promotion.name, promotions[1].name)
        self.assertEqual(promotion.available, promotions[1].available)
        self.assertEqual(promotion.gender, promotions[1].gender)
        self.assertEqual(promotion.birthday, promotions[1].birthday)

    def test_find_by_category(self):
        """It should Find Promotions by Category"""
        promotions = PromotionFactory.create_batch(10)
        for promotion in promotions:
            promotion.create()
        category = promotions[0].category
        count = len(
            [promotion for promotion in promotions if promotion.category == category])
        found = Promotion.find_by_category(category)
        self.assertEqual(found.count(), count)
        for promotion in found:
            self.assertEqual(promotion.category, category)

    def test_find_by_name(self):
        """It should Find a Promotion by Name"""
        promotions = PromotionFactory.create_batch(10)
        for promotion in promotions:
            promotion.create()
        name = promotions[0].name
        count = len(
            [promotion for promotion in promotions if promotion.name == name])
        found = Promotion.find_by_name(name)
        self.assertEqual(found.count(), count)
        for promotion in found:
            self.assertEqual(promotion.name, name)

    def test_find_by_availability(self):
        """It should Find Promotions by Availability"""
        promotions = PromotionFactory.create_batch(10)
        for promotion in promotions:
            promotion.create()
        available = promotions[0].available
        count = len(
            [promotion for promotion in promotions if promotion.available == available])
        found = Promotion.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for promotion in found:
            self.assertEqual(promotion.available, available)

    def test_find_by_gender(self):
        """It should Find Promotions by Gender"""
        promotions = PromotionFactory.create_batch(10)
        for promotion in promotions:
            promotion.create()
        gender = promotions[0].gender
        count = len(
            [promotion for promotion in promotions if promotion.gender == gender])
        found = Promotion.find_by_gender(gender)
        self.assertEqual(found.count(), count)
        for promotion in found:
            self.assertEqual(promotion.gender, gender)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        promotions = PromotionFactory.create_batch(3)
        for promotion in promotions:
            promotion.create()

        promotion = Promotion.find_or_404(promotions[1].id)
        self.assertIsNot(promotion, None)
        self.assertEqual(promotion.id, promotions[1].id)
        self.assertEqual(promotion.name, promotions[1].name)
        self.assertEqual(promotion.available, promotions[1].available)
        self.assertEqual(promotion.gender, promotions[1].gender)
        self.assertEqual(promotion.birthday, promotions[1].birthday)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Promotion.find_or_404, 0)
