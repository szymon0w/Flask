from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(400))
    date_added = db.Column(db.DateTime, default=datetime.now())
    borrowed = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return '<Book %r>' % self.id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<User %r>' % self.id

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    date_borrowed = db.Column(db.DateTime, default=datetime.now())
    date_expected_return = db.Column(db.DateTime, default=(datetime.now()+timedelta(days = 14)))
    date_returned = db.Column(db.DateTime, default=None)

    def __repr__(self):
        return '<Borrow %r>' % self.id


@app.route('/books', methods=['POST', 'GET'])
def books():
    if request.method == 'POST':
        book_name = request.form['name']
        book_description = request.form['description']
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


if __name__ == '__main__':
    app.run(debug=True)
