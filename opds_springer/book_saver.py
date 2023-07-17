import logging
from configparser import ConfigParser
from csv import QUOTE_NONE, DictReader
from datetime import date, datetime, timedelta

import requests

from .books_db import Book, Link, Subject, session


class APIException(Exception):
    pass


class BookData(object):
    def __init__(self):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            filename=datetime.now().strftime("book_saver_%Y%m%d.log"),
            format="%(asctime)s %(message)s",
            level=logging.INFO,
        )
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")
        self.api_key = self.config.get("Springer", "api_key")
        self.entitlement_id = self.config.get("Springer", "entitlement")
        self.kbart_file = self.config.get("Springer", "kbart_path")
        self.springer_client = SpringerClient(self.api_key, self.entitlement_id)

    def save_books_from_api(self, days=30):
        """Saves books from Springer API loaded after x days ago.

        Args:
            days (int): number of days ago to load from
        """
        from_date = (date.today() - timedelta(days=days)).isoformat()
        recent_books = self.springer_client.books_loaded_from(from_date)
        for record in recent_books:
            try:
                book_id = record["doi"]
                if not session.get(Book, book_id):
                    logging.info(f"Saving {book_id}...")
                    links = self.springer_client.get_links(record)
                    book = Book(
                        book_id=book_id,
                        title=record["publicationName"],
                        print_isbn=record["printIsbn"],
                        ebook_isbn=record["electronicIsbn"],
                        publisher=record["publisherName"],
                        series_id=record.get("seriesId"),
                        language=record["language"],
                        description=record["abstract"],
                        published=record["publicationDate"],
                        authors=self.springer_client.parse_contributors(
                            record.get("creators"), "creator"
                        ),
                        editors=self.springer_client.parse_contributors(
                            record.get("bookEditors"), "bookEditor"
                        ),
                    )
                    for pub_type, link in links:
                        new_link = Link(pub_type=pub_type, href=link)
                        book.links.append(new_link)
                    for subject in record["subjects"]:
                        if (
                            session.query(Subject)
                            .filter_by(subject=subject, source="springer")
                            .first()
                        ):
                            subject_record = (
                                session.query(Subject)
                                .filter_by(subject=subject, source="springer")
                                .first()
                            )
                            book.subjects.append(subject_record)
                        else:
                            new_subject = Subject(subject=subject, source="springer")
                            session.add(new_subject)
                            subject_record = (
                                session.query(Subject)
                                .filter_by(subject=subject, source="springer")
                                .first()
                            )
                            book.subjects.append(subject_record)
                    session.add(book)
                    session.commit()
            except APIException as e:
                logging.error(e)
                pass
            except Exception as e:
                logging.error(e)
                pass

    def save_books_from_kbart(self):
        """Saves books from a kbart file to database.

        Supplements kbart data with data from Springer API.
        """
        kbart_rows = self.parse_kbart_tsv()
        for kbart_row in kbart_rows:
            try:
                book_id = kbart_row["title_id"]
                if not session.get(Book, book_id):
                    logging.info(f"Saving {book_id}...")
                    springer_data = self.springer_client.supplement_book_data(book_id)
                    book = Book(
                        book_id=book_id,
                        title=kbart_row["publication_title"],
                        print_isbn=kbart_row["print_identifier"],
                        ebook_isbn=kbart_row["online_identifier"],
                        publisher=kbart_row["publisher_name"],
                        series_id=kbart_row["parent_publication_title_id"],
                        language=springer_data["language"],
                        description=springer_data["description"],
                        published=springer_data["publication_date"],
                    )
                    if springer_data.get("authors"):
                        book.authors = springer_data["authors"]
                    if springer_data.get("editors"):
                        book.authors = springer_data["editors"]
                    for pub_type, link in springer_data["links"]:
                        new_link = Link(pub_type=pub_type, href=link)
                        book.links.append(new_link)
                    for subject in springer_data["subjects"]:
                        if (
                            session.query(Subject)
                            .filter_by(subject=subject, source="springer")
                            .first()
                        ):
                            subject_record = (
                                session.query(Subject)
                                .filter_by(subject=subject, source="springer")
                                .first()
                            )
                            book.subjects.append(subject_record)
                        else:
                            new_subject = Subject(subject=subject, source="springer")
                            session.add(new_subject)
                            subject_record = (
                                session.query(Subject)
                                .filter_by(subject=subject, source="springer")
                                .first()
                            )
                            book.subjects.append(subject_record)
                    session.add(book)
                    session.commit()
            except APIException as e:
                logging.error(e)
                pass
            except Exception as e:
                logging.error(e)
                pass

    def parse_kbart_tsv(self):
        """Parses a kbart tsv file as a dictionary.

        Args:
            kbart_file (obj or str): Path object or string to kbart tsv file

        Yields:
            dict: row data
        """
        with open(self.kbart_file, mode="r") as tsv:
            tsv_reader = DictReader(tsv, delimiter="\t", quoting=QUOTE_NONE)
            for row in tsv_reader:
                yield row


class SpringerClient(object):
    BASE_URL = "https://spdi.public.springernature.app/bookmeta/v1/json"

    def __init__(self, api_key, entitlement_id):
        self.api_key = api_key
        self.entitlement_id = entitlement_id

    def books_loaded_from(self, date_string):
        """Gets book data from the Springer API for books added since a date.

        Args:
            date_string (str): date to start from, formatted YYYY-MM-DD
        """
        self.page_length = 100
        try:
            params = {
                "q": f"dateloadedfrom:{date_string}",
                "p": self.page_length,
                "api_key": self.api_key,
                "entitlement": self.entitlement_id,
            }
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            total_results = int(response.json()["result"][0]["total"])
            if total_results <= self.page_length:
                for record in response.json()["records"]:
                    yield record
            else:
                start = 1
                while response.json().get("nextPage"):
                    params["s"] = start
                    response = requests.get(self.BASE_URL, params=params)
                    for record in response.json()["records"]:
                        yield record
                    start += self.page_length
        except Exception as err:
            raise APIException(err)

    def supplement_book_data(self, doi):
        """Gets and formats book data from the Springer API.

        Args:
            doi (string): identifier of book to retrieve. May or may not include
        "doi" at beginning of identifier.

        Returns:
            dict: data about a book
        """
        record = self.request_book(doi)
        book_data = {
            "language": record["language"],
            "description": record["abstract"],
            "publication_date": record["publicationDate"],
            "subjects": record["subjects"],
            "authors": self.parse_contributors(record.get("creators"), "creator"),
            "editors": self.parse_contributors(record.get("bookEditors"), "bookEditor"),
            "links": self.get_links(record),
        }
        return book_data

    def request_book(self, doi):
        """Gets and formats the JSON response for the Springer single book endpoint.

        Args:
            doi (string): identifier of book to retrieve. May or may not include
        "doi" at beginning of identifier

        Returns:
            dict: main book information
        """
        # check if "doi:" is in beginning of string; if not, add
        doi = f"doi:{doi}" if not doi.startswith("doi") else doi
        try:
            params = {
                "q": doi,
                "api_key": self.api_key,
                "entitlement": self.entitlement_id,
            }
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            page_data = response.json()
            if page_data["records"]:
                return page_data["records"][0]
            else:
                raise APIException(f"{doi} not found in API")
        except Exception as err:
            raise Exception(err)

    def parse_contributors(self, list_of_contributors, contributor_type):
        """Gets a list of creators or editors.

        Args:
            list_of_contributors (list): list of Springer creators or bookEditors
            contributor_type (string): creator or bookEditor

        Returns:
            list: list of creators or editors
        """
        if list_of_contributors:
            return "|".join([c[contributor_type] for c in list_of_contributors])

    def get_links(self, record):
        """Gets links to media formats.

        Args:
            record (dict): main book information

        Returns:
            list: list of links to ebooks
        """
        links = []
        for url in record["url"]:
            if url.get("format"):
                links.append((url["format"], url["value"]))
        return links
