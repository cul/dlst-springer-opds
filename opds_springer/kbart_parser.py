class KbartParser(object):
    FIELDS = [
        "publication_title",
        "print_identifier",
        "online_identifier",
        "date_first_issue_online",
        "num_first_vol_online",
        "num_first_issue_online",
        "date_last_issue_online",
        "num_last_vol_online",
        "num_last_issue_online",
        "title_url",
        "first_author",
        "title_id",
        "embargo_info",
        "coverage_depth",
        "coverage_notes",
        "publisher_name",
        "publication_type",
        "date_monograph_published_print",
        "date_monograph_published_online",
        "monograph_volume",
        "monograph_edition",
        "first_editor",
        "parent_publication_title_id",
        "preceding_publication_title_id",
        "access_type",
    ]

    def get_all_books_from_csv(self, csv_file):
        pass

    def get_data_from_row(self, row):
        book_data = {
            "title": row[0],
            "print isbn": row[1],
            "ebook isbn": row[2],
            "identifier": row[11],
            "publisher": row[15],
        }
        return book_data
