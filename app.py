from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import services
import filtering_algorithm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
engine = create_engine('sqlite:///library.db', echo = True)

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(400))
    date_added = db.Column(db.DateTime, default=datetime.now())
    is_borrowed = db.Column(db.Boolean, default=False)
    borrowed_by = db.Column(db.Integer, db.ForeignKey('user.id'), default=None)
    date_borrowed = db.Column(db.DateTime, default=datetime.now())
    date_expected_return = db.Column(db.DateTime, default=None)

    def __repr__(self):
        return '<Book %r>' % self.id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<User %r>' % self.id

@app.route('/', methods=['GET'])
def home():
    books = Book.query.order_by(Book.date_added).all()
    users = User.query.order_by(User.date_added).all()
    Session = sessionmaker(bind = engine)
    session = Session()
    books_not_returned = session.query(Book).filter(Book.is_borrowed == True and Book.date_expected_return < datetime.now())

    return render_template('home.html', books=books, users=users, books_not_returned=books_not_returned)

@app.route('/search/user', methods=['POST'])
def search_user():
    searched_name = request.form['name']
    books = Book.query.order_by(Book.date_added).all()
    users = User.query.order_by(User.date_added).all()
    users = filtering_algorithm.filter_by_word(searched_name, users)
    Session = sessionmaker(bind = engine)
    session = Session()
    books_not_returned = session.query(Book).filter(Book.is_borrowed == True and Book.date_expected_return < datetime.now())

    return render_template('home.html', books=books, users=users, books_not_returned=books_not_returned)

@app.route('/search/book', methods=['POST'])
def search_book():
    searched_name = request.form['name']
    books = Book.query.order_by(Book.date_added).all()
    users = User.query.order_by(User.date_added).all()
    books = filtering_algorithm.filter_by_word(searched_name, books)
    Session = sessionmaker(bind = engine)
    session = Session()
    books_not_returned = session.query(Book).filter(Book.is_borrowed == True and Book.date_expected_return < datetime.now())

    return render_template('home.html', books=books, users=users, books_not_returned=books_not_returned)

@app.route('/books', methods=['POST', 'GET'])
def books():
    if request.method == 'POST':
        book_name = request.form['name']
        book_description = request.form['description']
        if not book_description:
            book_description = services.get_definition(book_name)
 
        new_book = Book(name = book_name, description = book_description)
        try:
            db.session.add(new_book)
            db.session.commit()
            return redirect('/books')
        except:
            return 'There was an issue adding the book'

    else:
        books = Book.query.order_by(Book.date_added).all()
        return render_template('books.html', books=books)

@app.route('/books/delete/<int:id>')
def deletebook(id):
    book_to_delete = Book.query.get_or_404(id)
    try:
        db.session.delete(book_to_delete)
        db.session.commit()
        return redirect('/books')
    except:
        return 'There was an issue deleting the book'

@app.route('/books/update/<int:id>', methods=['GET', 'POST'])
def updatebook(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.name = request.form['name']
        book.description = request.form['description']
        try: 
            db.session.commit()
            return redirect('/books')  
        except:
            return 'There was an issue updating the book'                
    else:
        return render_template('update.html', book=book)

@app.route('/users', methods=['POST', 'GET'])
def users():
    if request.method == 'POST':
        user_name = request.form['name']
        new_user = User(name = user_name)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')
        except:
            return 'There was an issue adding the user'
    else:
        users = User.query.order_by(User.date_added).all()
        return render_template('users.html', users=users)

@app.route('/users/delete/<int:id>')
def deleteuser(id):
    user_to_delete = User.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return redirect('/users')
    except:
        return 'There was an issue deleting the user'

@app.route('/user/<int:id>', methods=['GET'])
def user(id):
    user = User.query.get_or_404(id)
    user_books = Book.query.filter_by(borrowed_by=id).order_by(Book.date_expected_return).all()
    free_books = Book.query.filter_by(is_borrowed=False).all()

    return render_template('user.html', user = user, user_books = user_books, free_books = free_books)

@app.route('/user/borrow/<int:user_id>/<int:book_id>')
def borrow_book(user_id, book_id):
    book = Book.query.get_or_404(book_id)
    four_weeks = timedelta(days = 28)
    book.date_expected_return = datetime.now() + four_weeks
    book.is_borrowed = True
    book.borrowed_by = user_id
    book.date_borrowed = datetime.now()
    try: 
        db.session.commit()
        return redirect('/user/' + format(user_id))  
    except:
        return 'There was an issue updating the book'                

@app.route('/user/return/<int:user_id>/<int:book_id>')
def return_book(user_id, book_id):
    book = Book.query.get_or_404(book_id)
    book.date_expected_return = None
    book.is_borrowed = False
    book.borrowed_by = None
    book.date_borrowed = None
    try: 
        db.session.commit()
        return redirect('/user/' + format(user_id))  
    except:
        return 'There was an issue updating the book'                

@app.route('/user/borrow/extend/<int:user_id>/<int:book_id>')
def borrow_extend_book(user_id, book_id):
    book = Book.query.get_or_404(book_id)
    two_weeks = timedelta(days = 14)
    book.date_expected_return = book.date_expected_return + two_weeks
    try: 
        db.session.commit()
        return redirect('/user/' + format(user_id))  
    except:
        return 'There was an issue updating the book'


if __name__ == '__main__':
    app.run(debug=True)
