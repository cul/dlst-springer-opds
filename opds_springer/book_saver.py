import logging
from configparser import ConfigParser
from csv import DictReader

import requests

from .books_db import Book, Subject, session


class BookData(object):
    def __init__(self):
        logging.basicConfig(
            datefmt="%m/%d/%Y %I:%M:%S %p",
            filename="book_saver.log",
            format="%(asctime)s %(message)s",
            level=logging.INFO,
        )
        self.config = ConfigParser()
        self.config.read("local_settings.cfg")

    def save_books(self):
        """Saves books from a kbart file to database.

        Supplements kbart data with data from Springer API.
        """
        # TODO: download kbart file? - will need api key
        springer_client = SpringerClient(self.config.get("Springer", "api_key"))
        kbart_rows = self.parse_kbart_tsv("path/to/file.txt")
        for kbart_row in kbart_rows:
            try:
                book_id = kbart_row["title_id"]
                if not session.get(Book, book_id):
                    springer_data = springer_client.get_book_from_api(book_id)
                    book = Book(
                        book_id=book_id,
                        title=kbart_row["publication_title"],
                        print_isbn=kbart_row["print_identifier"],
                        ebook_isbn=kbart_row["online_identifier"],
                        publisher=kbart_row["publisher_name"],
                        series_id=kbart_row["parent_publication_title_id"],
                        language=springer_data["language"],
                        description=springer_data["description"],
                    )
                    session.add(book)
                    for subject in springer_data["subjects"]:
                        if session.query(Subject).filter_by(
                            subject=subject, source="springer"
                        ):
                            subject_record = (
                                session.query(Subject)
                                .filter_by(subject=subject, source="springer")
                                .first()
                            )
                            print(subject_record)
                            # TODO: connect subject to book
                        else:
                            new_subject = Subject(subject=subject, source="springer")
                            session.add(new_subject)
                            # TODO: connect subject to book
                    session.commit()
            except Exception as e:
                raise (e)

    def parse_kbart_tsv(self, kbart_file):
        """Parses a kbart tsv file as a dictionary.

        Args:
            kbart_file (obj or str): Path object or string to kbart tsv file

        Yields:
            dict: row data
        """
        with open(kbart_file, mode="r") as tsv:
            tsv_reader = DictReader(tsv, dialect="excel-tab")
            for row in tsv_reader:
                yield row


class SpringerClient(object):
    BASE_URL = "https://api.springernature.com/bookmeta/v1/json"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_book_data(self, doi):
        """Gets and formats book data from the Springer API.

        Args:
            doi (string): identifier of book to retrieve. May or may not include
        "doi" at beginning of identifier.

        Returns:
            dict: data about a book
        """
        record, facets = self.request_book(doi)
        book_data = {
            "language": record["language"],
            "description": record["abstract"],
            "publication_date": record["publicationDate"],
            "subjects": self.parse_subjects(facets),
            "authors": self.parse_contributors(record["creators"], "creator"),
            "editors": self.parse_contributors(record["bookEditors"], "bookEditor"),
        }
        return book_data

    def request_book(self, doi):
        """Gets and formats the JSON response for the Springer single book endpoint.

        Args:
            doi (string): identifier of book to retrieve. May or may not include
        "doi" at beginning of identifier

        Returns:
            tuple: main book information and facets
        """
        # check if "doi:" is in beginning of string; if not, add
        doi = f"doi:{doi}" if not doi.startswith("doi") else doi
        try:
            params = {"q": doi, "api_key": self.api_key}
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            page_data = response.json()
            return page_data["records"][0], page_data["facets"]
        except Exception as err:
            raise Exception(err)

    def parse_subjects_from_json(self, facets):
        """Gets a list of subjects from the facets portion of an API response.

        Args:
            facets (list): list of Springer facets

        Returns:
            list: list of subjects
        """
        subject_facets = [f["values"] for f in facets if f["name"] == "subject"][0]
        subjects = [sf["value"] for sf in subject_facets]
        return subjects

    def parse_contributors(self, list_of_contributors, contributor_type):
        """Gets a list of creators or editors.

        Args:
            list_of_contributors (list): list of Springer creators or bookEditors
            contributor_type (string): creator or bookEditor

        Returns:
            list: list of creators or editors
        """
        return [c[contributor_type] for c in list_of_contributors]
