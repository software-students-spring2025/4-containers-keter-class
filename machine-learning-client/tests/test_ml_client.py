"""
Testing for ML Client
"""

import pytest
import main
from mongomock import MongoClient


class Tests:
    """
    tests
    """

    @pytest.fixture
    def mock_db(self):
        """
        Mock db for testing
        """
        client = MongoClient()
        db = client.test_flaskdb
        yield db
        client.close()

    @pytest.fixture
    def client(self):
        """
        idk
        """
        return

    def parse_card_info_invalid_card(self, mock_db):
        """
        Testing invalid card inputs
        """

        test_card_scan_incorrect_num = (
            "realawesomebank.com 12345 AB 03/20 123456ABC "
            "1234 4321 1010 54546 Valid Thru: 01/26 Sec code: 123 "
            "JOHN JACOB JINGLEHEIMER SCHMIDT US and Canada 800.421.211 "
            "Int'l: 302-594-8200 Made from recycled plastic"
        )
        test_username = "j3schmidt"
        test_cardname = "realawesomebank card 1"

        test_card_scan_incorrect_name = (
            "realawesomebank.com 12345 AB 03/20 123456ABC "
            "1234 4321 1010 5454 Valid Thru: 01/26 Sec code: 123 "
            "JOHN US and Canada 800.421.211 "
            "Int'l: 302-594-8200 Made from recycled plastic"
        )

        test_card_scan_incorrect_expiry = (
            "realawesomebank.com 12345 AB 03/20 123456ABC "
            "1234 4321 1010 5454 Valid Thru: 01/26 Sec code: 123 "
            "JOHN JACOB JINGLEHEIMER SCHMIDT US and Canada 800.421.211 "
            "Int'l: 302-594-8200 Made from recycled plastic"
        )

        test_card_scan_incorrect_cvv = (
            "realawesomebank.com 12345 AB 03/20 123456ABC "
            "1234 4321 1010 5454 Valid Thru: 01/26 Sec code: 12345 "
            "JOHN JACOB JINGLEHEIMER SCHMIDT US and Canada 800.421.211 "
            "Int'l: 302-594-8200 Made from recycled plastic"
        )
