from datetime import datetime
from math import ceil

from sqlalchemy import select

from .books_db import Book, session


class GenerateFeed(object):
    PAGE_SIZE = 1000

    def opds_feed(self):
        """Creates a feed of OPDS data from saved books."""
        self.total_pubs = session.query(Book).count()
        self.total_pages = ceil(self.total_pubs / self.PAGE_SIZE)
        books = self.get_books_from_db()
        count = 0
        publications = []
        page_number = 1
        while count < self.total_pubs:
            for book in books:
                book_json = BookOPDS().create_json(book)
                publications.append(book_json)
                if count > 0 and count % self.PAGE_SIZE == 0:
                    opds_page = self.opds_page_data(page_number, publications)
                    print(opds_page)
                    page_number += 1
                    publications = []
                count += 1

    def opds_page_data(self, page_number, publications):
        """Formats data for one OPDS response page.

        Args:
            page_number (int): current page number
            publications (list): OPDS data for publications

        Returns:
            dict: OPDS response data
        """
        return {
            "metadata": {
                "title": "Springer Test Feed",
                "itemsPerPage": self.PAGE_SIZE,
                "currentPage": page_number,
                "numberOfItems": self.total_pubs,
            },
            "links": self.opds_response_links(page_number),
            "publications": publications,
        }

    def opds_response_links(self, page_number):
        """Formats links data for OPDS response.

        Args:
            page_number (int): current page number

        Returns:
            list: list of dictionaries containing link information

        """

        links = []
        self_rel = "self"
        first_rel = "first"
        last_rel = "last"
        prev_rel = "prev"
        next_rel = "next"
        if page_number == 1:
            self_rel = ["self", "first"]
            first_rel = None
            prev_rel = None
        if page_number == 2:
            first_rel = ["prev", "first"]
            prev_rel = None
        if page_number + 1 == self.total_pages:
            last_rel = ["next", "last"]
            next_rel = None
        if page_number == self.total_pages:
            self_rel = ["self", "last"]
            next_rel = None
            last_rel = None
        if self_rel:
            links.append(self.opds_response_link(page_number, self_rel))
        if first_rel:
            links.append(self.opds_response_link(1, first_rel))
        if last_rel:
            links.append(self.opds_response_link(self.total_pages, last_rel))
        if next_rel:
            links.append(self.opds_response_link(page_number + 1, next_rel))
        if prev_rel:
            links.append(self.opds_response_link(page_number - 1, prev_rel))
        return links

    def opds_response_link(self, page_number, rel):
        """Formats a link.

        Args:
            page_number (int): current page number
            rel (str): e.g., 'last'

        Returns:
            dict: link information

        """
        return {
            "rel": rel,
            "href": f"https://ebooks-test.library.columbia.edu/static-feeds/springer/springer_test_feed_{page_number}.json",
            "type": "application/opds+json",
        }

    def get_books_from_db(self):
        """Gets all book records.

        Yields:
            obj: book record
        """
        result = session.execute(select(Book))
        for book in result.all():
            yield book[0]


class BookOPDS(object):
    def create_json(self, book):
        """Creates dictionary of OPDS book data.

        Args:
            book (obj): book record

        Returns:
            dict: book data
        """
        self.book = book
        book_dict = {
            "metatadata": self.metadata(),
            "images": self.images(),
            "links": self.links(),
        }
        return book_dict

    def metadata(self):
        """Creates dictionary of book metadata."""
        metadata = {
            "identifier": f"https://dx.doi.org/{self.book.book_id}",
            "modified": datetime.utcnow().isoformat(),
            "title": self.book.title,
            "language": self.book.language,
            "@type": "http://schema.org/EBook",
            "publisher": self.book.publisher,
            "published": self.book.published,
            "subject": self.subject(),
            "author": self.author(),
            "editor": self.editor(),
        }
        return metadata

    def subject(self):
        """Creates list of book subjects."""
        subject = [
            {
                "scheme": "http://librarysimplified.org/terms/fiction/",
                "code": "Nonfiction",
                "name": "Nonfiction",
            }
        ]
        for s in self.book.subjects:
            subject.append(s.subject)
        return subject

    def author(self):
        """Creates list of book authors."""
        if self.book.authors:
            authors = []
            for a in self.book.authors.split("|"):
                authors.append({"name": f"{a}"})
            return authors

    def editor(self):
        """Creates list of book editors."""
        if self.book.editors:
            editors = []
            for a in self.book.editors.split("|"):
                editors.append({"name": f"{a}"})
            return editors

    def images(self):
        """Creates list of book images."""
        images = []
        for size in ["height_648", "width_125", "width_95"]:
            image = {
                "href": f"https://covers.springernature.com/books/jpg_{size}_pixels/{self.book.ebook_isbn}.jpg",
                "type": "image/jpeg",
            }
            if size.split("_")[0] == "width":
                image["width"] = int(size.split("_")[-1])
            images.append(image)
        return images

    def links(self):
        """Creates list of book links."""
        links = []
        for li in self.book.links:
            pub_type = (
                "application/pdf" if "pdf" in li.pub_type else "application/epub+zip"
            )
            link = {
                "rel": "http://opds-spec.org/acquisition/open-access",
                "type": pub_type,
                "href": f"https://sp.springer.com/saml/login?idp=urn%3Amace%3Aincommon%3Acolumbia.edu&targetUrl={li.href}",
            }
            links.append(link)
        return links
