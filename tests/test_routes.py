"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from service import app
from service.models import db, init_db, Promotion
from service.common import status  # HTTP Status Codes
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/promotions"
######################################################################
#  T E S T   C A S E S
######################################################################


class TestPromotionService(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_promotions(self, count):
        """Factory method to create promotions in bulk"""
        promotions = []
        for _ in range(count):
            test_promotion = PromotionFactory()
            response = self.client.post(
                BASE_URL, json=test_promotion.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test promotion"
            )
            new_promotion = response.get_json()
            test_promotion.id = new_promotion["id"]
            promotions.append(test_promotion)
        return promotions

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_health_endpoint(self):
        """ It should return status OK """
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_promotion_list(self):
        """It should Get a list of Promotion"""
        self._create_promotions(5)
        response = self.client.get(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_promotion_list_with_name(self):
        """It should Query Promotions by name"""
        promotions = self._create_promotions(10)
        test_name = promotions[0].name
        name_promotions = [
            promotion for promotion in promotions if promotion.name == test_name]
        response = self.client.get(
            BASE_URL,
            query_string=f"name={test_name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(name_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["name"], test_name)

    def test_get_promotion_list_with_category(self):
        """It should Query Promotions by category"""
        promotions = self._create_promotions(10)
        test_category = promotions[0].category
        category_promotions = [
            promotion for promotion in promotions if promotion.category == test_category]
        response = self.client.get(
            BASE_URL,
            query_string=f"category={test_category}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(category_promotions))
        # check the data just to be sure
        for promotion in data:
            self.assertEqual(promotion["category"], test_category)

    # def test_get_promotion_list_with_available(self):
    #     """It should Query Promotions by available"""
    #     promotions = self._create_promotions(10)
    #     logging.debug(promotions)
    #     test_available = promotions[0].available
    #     available_promotions = [
    #         promotion for promotion in promotions if promotion.available == test_available]
    #     logging.debug(available_promotions)
    #     response = self.client.get(
    #         BASE_URL,
    #         query_string=f"available={test_available}"
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()
    #     self.assertEqual(len(data), len(available_promotions))
    #     # check the data just to be sure
    #     for promotion in data:
    #         self.assertEqual(promotion["available"], test_available)

    def test_get_promotion(self):
        """It should Get a single Promotion"""
        # get the id of a promotion
        test_promotion = self._create_promotions(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_promotion.name)

    def test_get_promotion_not_found(self):
        """It should not Get a Promotion thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_delete_promotion(self):
        '''This should delete a promotion'''
        test_promotion = self._create_promotions(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # Check to see if the promotion was deleted
        response = self.client.get(f"{BASE_URL}/{test_promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_promotion_not_found(self):
        '''This should test delete promotion not found'''
        response = self.client.delete(f"{BASE_URL}/1")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_promotion(self):
        """It should Create a new promotion"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["category"], test_promotion.category)
        self.assertEqual(new_promotion["available"], test_promotion.available)
        self.assertEqual(new_promotion["promotype"],
                         test_promotion.promotype.name)

        # Check that the location header was correct

        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_promotion = response.get_json()
        self.assertEqual(new_promotion["name"], test_promotion.name)
        self.assertEqual(new_promotion["category"], test_promotion.category)
        self.assertEqual(new_promotion["available"], test_promotion.available)
        self.assertEqual(new_promotion["promotype"],
                         test_promotion.promotype.name)

    def test_create_promotion_without_json(self):
        """It should not Create a new promotion, instead, give 415 error"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_promotion_with_bad_json(self):
        """It should not Create a new promotion, instead, give 400 error"""
        test_promotion = PromotionFactory()
        logging.debug("Test Promotion: %s", test_promotion.serialize())
        response = self.client.post(BASE_URL, json="")
        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)

    def test_update_promotion(self):
        """It should Update an existing Promotion"""
        # create a promotion to update
        test_promotion = PromotionFactory()
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the promotion
        new_promotion = response.get_json()
        logging.debug(new_promotion)
        new_promotion["category"] = "unknown"
        response = self.client.put(
            f"{BASE_URL}/{new_promotion['id']}", json=new_promotion)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_promotion = response.get_json()
        self.assertEqual(updated_promotion["category"], "unknown")

    def test_update_promotion_not_found(self):
        '''This should test update promotion not found'''
        test_promotion = PromotionFactory()
        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # update the promotion
        new_promotion = response.get_json()
        logging.debug(new_promotion)
        response = self.client.put(f"{BASE_URL}/0", json=new_promotion)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_activate_promotions(self):
        '''This should test activating promotions using non-CRUD route'''
        test_promotion = PromotionFactory()
        test_promotion.available = False
        logging.debug(test_promotion)

        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_promotion = response.get_json()

        response = self.client.put(
            f"{BASE_URL}/{new_promotion['id']}/activate")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_promotion = response.get_json()

        self.assertEqual(updated_promotion["available"], True)

        # testing activating a non existent promotion
        response = self.client.put(f"{BASE_URL}/0/activate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deactivate_promotions(self):
        '''This should test deactivating promotions using non-CRUD route'''
        test_promotion = PromotionFactory()
        test_promotion.available = True
        logging.debug(test_promotion)

        response = self.client.post(BASE_URL, json=test_promotion.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_promotion = response.get_json()

        response = self.client.put(
            f"{BASE_URL}/{new_promotion['id']}/deactivate")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_promotion = response.get_json()

        self.assertEqual(updated_promotion["available"], False)

        # testing deactivating a non existent promotion
        response = self.client.put(f"{BASE_URL}/0/deactivate")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
