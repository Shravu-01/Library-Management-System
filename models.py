from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = "books"
    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    authors = db.Column(db.Text, nullable=False)
    average_rating = db.Column(db.Float, nullable=True)
    isbn = db.Column(db.String(20), nullable=False)
    num_pages = db.Column(db.Integer, nullable=True)
    ratings_count = db.Column(db.Integer, nullable=True)
    publication_date = db.Column(db.Text, nullable=True)
    publisher = db.Column(db.Text, nullable=True)
    status = db.Column(db.Text, nullable=True)
    copies_available = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Book {self.title}>"

class Member(db.Model):
    __tablename__ = "members"
    member_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Member {self.name}>"

class BorrowingHistory(db.Model):
    __tablename__ = "borrowinghistory"
    BorrowingID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey("members.member_id"), nullable=False)
    BookID = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable=False)
    BorrowDate = db.Column(db.Date, nullable=False)
    ReturnDate = db.Column(db.Date, nullable=True)

    member = db.relationship("Member", backref="borrowings")
    book = db.relationship("Book", backref="borrowings")

    def __repr__(self):
        return f"<BorrowingHistory UserID={self.UserID}, BookID={self.BookID}>"

class Fine(db.Model):
    __tablename__ = "fines"
    FineID = db.Column(db.Integer, primary_key=True)
    BorrowingID = db.Column(db.Integer, db.ForeignKey("borrowinghistory.BorrowingID"), nullable=False)
    FineAmount = db.Column(db.Float, nullable=False)
    FineDate = db.Column(db.Date, nullable=False)
    PaidDate = db.Column(db.Date, nullable=True)

    borrowing = db.relationship("BorrowingHistory", backref="fines")

    def __repr__(self):
        return f"<Fine {self.FineAmount} for Borrowing {self.BorrowingID}>"