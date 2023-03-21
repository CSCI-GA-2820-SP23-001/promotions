"""
Test Error Handlers Test Suite
"""
import logging
from unittest import TestCase
from service.common import error_handlers

######################################################################
#  T E S T   C A S E S
######################################################################


class TestErrorHandler(TestCase):
    """ Error handler Tests """

    def test_request_validation_error(self):
        """ request validation error Tests """
        response = error_handlers.request_validation_error("errormsg")
        logging.debug(response)
        self.assertEqual(
            response[1], 400
        )

    def test_method_not_supported(self):
        """ method not supported Tests """
        response = error_handlers.method_not_supported("errormsg")
        logging.debug(response)
        self.assertEqual(
            response[1], 405
        )

    def test_resource_conflict(self):
        """ resource conflict Tests """
        response = error_handlers.resource_conflict("errormsg")
        logging.debug(response)
        self.assertEqual(
            response[1], 409
        )

    def test_mediatype_not_supported(self):
        """ mediatype not supported Tests """
        response = error_handlers.mediatype_not_supported("errormsg")
        logging.debug(response)
        self.assertEqual(
            response[1], 415
        )

    def test_internal_server_error(self):
        """ server error Tests """
        response = error_handlers.internal_server_error("errormsg")
        logging.debug(response)
        self.assertEqual(
            response[1], 500
        )
