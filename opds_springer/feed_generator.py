from datetime import datetime

from sqlalchemy import select

from .books_db import Book, session

# from math import ceil


class GenerateFeed(object):
    def run(self):
        # page_size = 1000
        # total_pages = ceil(count / page_size)
        books = self.get_books_from_db()
        for book in books:
            book_json = BookOPDS().create_json(book)
            print(book_json)

    def opds_response(self, page_number, count, page_size):
        # total_pages = ceil(count / page_size)
        return {
            "metadata": {
                "title": "Springer Test Feed",
                "itemsPerPage": page_size,
                "currentPage": page_number,
                "numberOfItems": count,
            },
            # "links": opds_response_links(page_number, total_pages),
            "publications": [],
        }

    def get_books_from_db(self):
        result = session.execute(select(Book))
        for book in result.all():
            yield book[0]


class BookOPDS(object):
    def create_json(self, book):
        self.book = book
        book_dict = {
            "metatadata": self.metadata(),
            "images": self.images(),
            "links": self.links(),
        }
        return book_dict

    def metadata(self):
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
        }
        return metadata

    def subject(self):
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
        if self.book.authors:
            authors = []
            for a in self.book.authors.split("|"):
                authors.append({"name": f"{a}"})
            return authors

    def images(self):
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
