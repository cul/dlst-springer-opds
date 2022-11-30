import types
import unittest
from pathlib import Path

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
