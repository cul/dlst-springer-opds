import json
import types
import unittest
from pathlib import Path

import responses
from responses import matchers

from opds_springer.book_saver import BookData, SpringerClient


class TestBookData(unittest.TestCase):
    def test_init(self):
        book_data = BookData()
        self.assertTrue(book_data)

    def test_parse_kbart_tsv(self):
        kbart_file = Path("fixtures", "springer_kbart_example.txt")
        parsed_kbart = BookData().parse_kbart_tsv(kbart_file)
        self.assertIsInstance(parsed_kbart, types.GeneratorType)
        self.assertEqual(len([x for x in parsed_kbart]), 51)


class TestSpringerClient(unittest.TestCase):
    def test_init(self):
        springer_client = SpringerClient("api_key")
        self.assertTrue(springer_client)

    def test_get_book_data(self):
        pass

    @responses.activate
    def test_request_book(self):
        springer_client = SpringerClient("3ee6153f5ef441579808d667c16df936")
        with open(Path("fixtures", "springer_book_example.json")) as f:
            response_json = json.load(f)
        params = {
            "q": "doi:10.1007/978-1-349-11550-1",
            "api_key": "3ee6153f5ef441579808d667c16df936",
        }
        responses.get(
            url="https://api.springernature.com/bookmeta/v1/json",
            json=response_json,
            match=[matchers.query_param_matcher(params)],
        )
        requested_book = springer_client.request_book("doi:10.1007/978-1-349-11550-1")
        self.assertIsInstance(requested_book, dict)

    def test_parse_contributors(self):
        list_of_creators = [{"creator": "Fultz, Brent"}, {"creator": "Howe, James"}]
        list_of_editors = []
        parsed_creators = SpringerClient("api_key").parse_contributors(
            list_of_creators, "creator"
        )
        parsed_editors = SpringerClient("api_key").parse_contributors(
            list_of_editors, "bookEditor"
        )
        self.assertIsInstance(parsed_creators, list)
        self.assertTrue("Fultz, Brent" in parsed_creators)
        self.assertIsInstance(parsed_editors, list)
        self.assertEqual(len(parsed_editors), 0)
