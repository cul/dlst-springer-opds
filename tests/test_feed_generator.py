import unittest
from random import randint

from sqlalchemy import select

from opds_springer.feed_generator import BookOPDS, GenerateFeed
from tests.setup_db import Book, session


class TestGenerateFeed(unittest.TestCase):
    def test_init(self):
        generate_feed = GenerateFeed()
        self.assertTrue(generate_feed)


class TestBookOPDS(unittest.TestCase):
    def get_random_book(self):
        result = session.execute(select(Book))
        all_results = result.all()
        return all_results[randint(0, 27)][0]

    def test_metadata(self):
        book_opds = BookOPDS()
        book_opds.book = self.get_random_book()
        metadata = book_opds.metadata()
        self.assertIsInstance(metadata, dict)

    def test_subject(self):
        nonfiction = {
            "scheme": "http://librarysimplified.org/terms/fiction/",
            "code": "Nonfiction",
            "name": "Nonfiction",
        }
        book_opds = BookOPDS()
        book_opds.book = self.get_random_book()
        subject = book_opds.subject()
        self.assertTrue(nonfiction in subject)
        self.assertEqual(len(subject), (len(book_opds.book.subjects) + 1))

    def test_author(self):
        book_opds = BookOPDS()
        book_opds.book = self.get_random_book()
        if book_opds.book.authors:
            authors = book_opds.author()
            self.assertIsInstance(authors, list)
            self.assertIsInstance(authors[0], dict)

    def test_editor(self):
        book_opds = BookOPDS()
        book_opds.book = self.get_random_book()
        if book_opds.book.editors:
            editors = book_opds.editor()
            self.assertIsInstance(editors, list)
            self.assertIsInstance(editors[0], dict)

    def test_images(self):
        book_opds = BookOPDS()
        book_opds.book = self.get_random_book()
        images = book_opds.images()
        self.assertEqual(len(images), 3)
        self.assertIsInstance(images[0], dict)

    def test_links(self):
        book_opds = BookOPDS()
        book_opds.book = self.get_random_book()
        links = book_opds.links()
        self.assertIsInstance(links, list)
        self.assertIsInstance(links[0], dict)
