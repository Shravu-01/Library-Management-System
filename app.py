from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from datetime import datetime
from models import db, Book, Member, BorrowingHistory, Fine

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:DelulU1848$@localhost/base'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'library-management-secret-key'
    
    db.init_app(app)
    
    return app

app = create_app()

# -------------------------------
# Routes
# -------------------------------

@app.route('/')
def index():
    # Get some stats for dashboard
    total_books = Book.query.count()
    total_members = Member.query.count()
    available_books = Book.query.filter(Book.copies_available > 0).count()
    
    return render_template('index.html', 
                         total_books=total_books,
                         total_members=total_members,
                         available_books=available_books)

@app.route('/books')
def books():
    all_books = Book.query.all()
    return render_template('books.html', books=all_books)

@app.route('/books/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        authors = request.form['authors']
        isbn = request.form['isbn']
        publisher = request.form.get('publisher', '')
        average_rating = request.form.get('average_rating')
        num_pages = request.form.get('num_pages')
        copies_available = request.form.get('copies_available', 1)
        
        new_book = Book(
            title=title, 
            authors=authors, 
            isbn=isbn,
            publisher=publisher if publisher else None,
            average_rating=float(average_rating) if average_rating else None,
            num_pages=int(num_pages) if num_pages else None,
            copies_available=int(copies_available)
        )
        db.session.add(new_book)
        db.session.commit()
        
        flash('Book added successfully!', 'success')
        return redirect(url_for('books'))
    
    return render_template('add_book.html')

@app.route('/books/search')
def search_books():
    query = request.args.get("query", "")
    results = []
    if query:
        results = Book.query.filter(
            or_(
                Book.title.ilike(f"%{query}%"),
                Book.authors.ilike(f"%{query}%")
            )
        ).all()
    return render_template("search.html", results=results, query=query)

@app.route('/members')
def members():
    all_members = Member.query.all()
    return render_template('members.html', members=all_members)

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        new_member = Member(name=name, email=email)
        db.session.add(new_member)
        db.session.commit()
        
        flash('Member added successfully!', 'success')
        return redirect(url_for('members'))
    
    return render_template('add_member.html')

# -------------------------------
# CRUD Operations for Books
# -------------------------------

# UPDATE Book - Edit book details
@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        # Update book details
        book.title = request.form['title']
        book.authors = request.form['authors']
        book.isbn = request.form['isbn']
        book.average_rating = float(request.form['average_rating']) if request.form['average_rating'] else None
        book.num_pages = int(request.form['num_pages']) if request.form['num_pages'] else None
        book.publication_date = request.form['publication_date'] or None
        book.publisher = request.form['publisher'] or None
        book.status = request.form['status']
        book.copies_available = int(request.form['copies_available'])
        
        db.session.commit()
        flash('Book updated successfully!', 'success')
        return redirect(url_for('books'))
    
    return render_template('edit_book.html', book=book)

# DELETE Book - Remove book
@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('books'))

# -------------------------------
# CRUD Operations for Members
# -------------------------------

# UPDATE Member - Edit member details
@app.route('/members/edit/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    member = Member.query.get_or_404(member_id)
    
    if request.method == 'POST':
        member.name = request.form['name']
        member.email = request.form['email']
        db.session.commit()
        flash('Member updated successfully!', 'success')
        return redirect(url_for('members'))
    
    return render_template('edit_member.html', member=member)

# DELETE Member - Remove member
@app.route('/members/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('members'))

# -------------------------------
# Borrowing Operations
# -------------------------------

# BORROW Book - Create borrowing record
@app.route('/books/borrow/<int:book_id>', methods=['GET', 'POST'])
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        member_id = request.form['member_id']
        
        # Check if book is available
        if book.copies_available <= 0:
            flash('No copies available for borrowing!', 'error')
            return redirect(url_for('books'))
        
        # Create borrowing record
        borrowing = BorrowingHistory(
            UserID=member_id,
            BookID=book_id,
            BorrowDate=datetime.utcnow().date()
        )
        
        # Update book availability
        book.copies_available -= 1
        if book.copies_available == 0:
            book.status = "Borrowed"
        
        db.session.add(borrowing)
        db.session.commit()
        flash('Book borrowed successfully!', 'success')
        return redirect(url_for('books'))
    
    members = Member.query.all()
    return render_template('borrow_book.html', book=book, members=members)

# RETURN Book - Update borrowing record
@app.route('/books/return/<int:borrowing_id>', methods=['POST'])
def return_book(borrowing_id):
    borrowing = BorrowingHistory.query.get_or_404(borrowing_id)
    book = Book.query.get(borrowing.BookID)
    
    # Update borrowing record
    borrowing.ReturnDate = datetime.utcnow().date()
    
    # Update book availability
    book.copies_available += 1
    book.status = "Available"
    
    db.session.commit()
    flash('Book returned successfully!', 'success')
    return redirect(url_for('view_borrowings'))

# View all borrowings
@app.route('/borrowings')
def view_borrowings():
    borrowings = BorrowingHistory.query.all()
    return render_template('borrowings.html', borrowings=borrowings)

# -------------------------------
# Fine Operations
# -------------------------------

@app.route('/fines')
def view_fines():
    fines = Fine.query.all()
    return render_template('fines.html', fines=fines)

# Pay Fine
@app.route('/fines/pay/<int:fine_id>', methods=['POST'])
def pay_fine(fine_id):
    fine = Fine.query.get_or_404(fine_id)
    fine.PaidDate = datetime.utcnow().date()
    db.session.commit()
    flash('Fine paid successfully!', 'success')
    return redirect(url_for('view_fines'))


# -------------------------------
# Reports
# -------------------------------

@app.route('/reports')
def reports():
    # Get statistics for reports
    total_books = Book.query.count()
    total_members = Member.query.count()
    
    # Available vs borrowed books
    available_books = Book.query.filter(Book.copies_available > 0).count()
    borrowed_books = total_books - available_books
    
    # Active borrowings (not returned)
    active_borrowings = BorrowingHistory.query.filter_by(ReturnDate=None).count()
    
    # Unpaid fines
    unpaid_fines = Fine.query.filter_by(PaidDate=None).count()
    total_fine_amount = db.session.query(db.func.sum(Fine.FineAmount)).filter_by(PaidDate=None).scalar() or 0
    
    # Popular books (most borrowed)
    popular_books = db.session.query(
        Book.title, 
        db.func.count(BorrowingHistory.BorrowingID).label('borrow_count')
    ).join(BorrowingHistory).group_by(Book.book_id).order_by(db.desc('borrow_count')).limit(5).all()
    
    # Recent activities
    recent_borrowings = BorrowingHistory.query.order_by(BorrowingHistory.BorrowDate.desc()).limit(10).all()
    
    return render_template('reports.html',
                         total_books=total_books,
                         total_members=total_members,
                         available_books=available_books,
                         borrowed_books=borrowed_books,
                         active_borrowings=active_borrowings,
                         unpaid_fines=unpaid_fines,
                         total_fine_amount=total_fine_amount,
                         popular_books=popular_books,
                         recent_borrowings=recent_borrowings)

# -------------------------------
# Run app
# -------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)