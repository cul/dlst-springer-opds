from sqlalchemy import Column, ForeignKey, Integer, String, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine("sqlite:///test.db", echo=True)

Base = declarative_base()


association_table = Table(
    "association_table",
    Base.metadata,
    Column("book_id", ForeignKey("book.book_id")),
    Column("subject_id", ForeignKey("subject.subject_id")),
)


class Book(Base):
    __tablename__ = "book"

    book_id = Column(String(length=50), primary_key=True)
    title = Column(String(length=256))
    print_isbn = Column(String(length=50))
    ebook_isbn = Column(String(length=50))
    publisher = Column(String(length=256))
    published = Column(String(length=256))
    series_id = Column(Integer())
    language = Column(String(length=50))
    description = Column(String(length=50))
    authors = Column(String(length=256))
    editors = Column(String(length=256))
    subjects = relationship("Subject", secondary=association_table)
    links = relationship("Link", backref="book")


class Link(Base):
    __tablename__ = "link"

    id = Column(Integer(), primary_key=True)
    rel = Column(String(length=256), default="http://opds-spec.org/acquisition")
    pub_type = Column(String(length=50))
    href = Column(String(length=256))
    book_id = Column(String(length=50), ForeignKey("book.book_id"))


class Subject(Base):
    __tablename__ = "subject"

    subject_id = Column(Integer(), primary_key=True)
    subject = Column(String(length=256))
    source = Column(String(length=50))


Base.metadata.create_all(engine)

session_maker = sessionmaker()
session_maker.configure(bind=engine)
session = session_maker()
