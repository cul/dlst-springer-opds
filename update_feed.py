import argparse

from opds_springer.book_saver import BookData
from opds_springer.feed_generator import GenerateFeed


def main():
    parser = argparse.ArgumentParser(
        description="Add recent books to database and create an updated OPDS feed."
    )
    parser.add_argument("days", help="Number of days ago to get books from.", type=int)
    args = parser.parse_args()
    BookData().save_books_from_api(args.days)
    GenerateFeed().opds_feed()


if __name__ == "__main__":
    main()
