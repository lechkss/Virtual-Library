from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import os
from werkzeug.utils import secure_filename

# типа базовая настройка приложения, секретный ключ как бы для сессий нужен, ну чтоб куки работали всякое такое
app = Flask(__name__)
app.secret_key = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'  # ну база данных как бы, обычный SQLite файл
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # вот сюда файлы загружаются, типа обложки

# создаём базу и логин-менеджер, чтобы потом можно было логиниться и всё такое
# честно, вот это всё с login_manager сначала не понимала, потом вроде дошло, надо чтобы Flask знал как юзера искать

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # короче, если не залогинен, то кидает на эту страницу

#### МОДЕЛИ
## вот тут прям начинается мясо
# сначала связь многие ко многим между книгами и жанрами
book_genres = db.Table('book_genres',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
)

### модель пользователя, типа базовая
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # имя должно быть уникальным
    password = db.Column(db.String(120), nullable=False)
    favorites = db.relationship('Book', secondary='favorites', backref='fav_users')  # избранные книги

## книга - заголовок, автор и обложка, плюс связи с жанрами, отзывами и рейтингами
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(100))  # !!тут имя файла, не сам файл!!
    genres = db.relationship('Genre', secondary=book_genres, backref='books')  # связь с жанрами
    reviews = db.relationship('Review', backref='book', lazy=True)
    ratings = db.relationship('Rating', backref='book', lazy=True)

# ну ктсати, про жанры, всё просто, ток id и имя
class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

## отзывы, связаны с книгой и юзером
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

### оценки - просто число от юзера к книге
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

# избранные книги, типа отдельная табличка, хотя вроде можно было и по-другому но я не справилась, к содалению с жтой залачей
class Favorite(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

## статус книги - читаю, хочу прочитать и тд
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    status = db.Column(db.String(20))  # типо строка, например read или want_to_read

# функция чтобы Flask понимал как доставать юзера по id, нужно для login_user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#### РОУТЫ

@app.route('/')
def index():
    # тут типа поиск и фильтр по жанрам
    search = request.args.get('q')
    genre_id = request.args.get('genre')
    query = Book.query
    if search:
        query = query.filter((Book.title.ilike(f"%{search}%")) | (Book.author.ilike(f"%{search}%")))
    if genre_id:
        query = query.join(Book.genres).filter(Genre.id == genre_id)
    books = query.all()
    genres = Genre.query.all()
    return render_template('index.html', books=books, genres=genres)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # регистрация юзера, если пост - сохраняем, если гет - форму показываем
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверные данные')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/book/add', methods=['GET', 'POST'])
@login_required  # только для залогиненных
def add_book():
    if request.method == 'POST':
        file = request.files['cover']  # обложку загружаем
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            cover=filename
        )
        selected_genres = Genre.query.filter(Genre.id.in_(request.form.getlist('genres'))).all()
        book.genres = selected_genres
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('index'))
    genres = Genre.query.all()
    return render_template('add_book.html', genres=genres)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    avg_rating = round(sum(r.value for r in book.ratings)/len(book.ratings), 2) if book.ratings else None
    return render_template('book_detail.html', book=book, avg_rating=avg_rating)

@app.route('/review/<int:book_id>', methods=['POST'])
@login_required
# ну просто добавляем отзыв от юзера к книжке
# я писала в у=тупую, но, в уелом, это можно было оптими0ировать

def add_review(book_id):
    review = Review(text=request.form['review'], user_id=current_user.id, book_id=book_id)
    db.session.add(review)
    db.session.commit()
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/rate/<int:book_id>', methods=['POST'])
@login_required
### !!! ДОДКЛАТЬ ДО СДАЧИ ОЦЕНИВАНИЕ КИНГ
# оцениваем книжку

def rate_book(book_id):
    rating = Rating(value=int(request.form['rating']), user_id=current_user.id, book_id=book_id)
    db.session.add(rating)
    db.session.commit()
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/favorite/<int:book_id>')
@login_required
# добавляем или убираем из избранного

def toggle_favorite(book_id):
    book = Book.query.get(book_id)
    if book in current_user.favorites:
        current_user.favorites.remove(book)
    else:
        current_user.favorites.append(book)
    db.session.commit()
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/status/<int:book_id>/<status>')
@login_required
# ставим статус, типа читаю или хочу читать

def mark_status(book_id, status):
    entry = Status.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    if entry:
        entry.status = status
    else:
        db.session.add(Status(user_id=current_user.id, book_id=book_id, status=status))
    db.session.commit()
    return redirect(url_for('book_detail', book_id=book_id))
### !!! ПРОЧИТАТЬ ПРО СОЗДАНИЕ СТАТИСТИКИ
####### СПРОСИТЬ ПРО ТО, КАК СОЗДАВАТЬ РАЗДЕЛЕНИЯ МОЖЕТ ОТДЕЛЬНА БД?
## статистики
@app.route('/statistics')
def statistics():
    # ну тут всякие цифры: сколько книг, средняя оценка, топ жанров
    total_books = Book.query.count()
    avg_rating = db.session.query(db.func.avg(Rating.value)).scalar()
    popular_genres = db.session.query(Genre.name, db.func.count(book_genres.c.book_id))\
                        .join(book_genres).group_by(Genre.name).order_by(db.func.count().desc()).limit(5).all()
    return render_template('statistics.html', total=total_books, avg=avg_rating, popular=popular_genres)

@app.route('/api/books')
def api_books():
    ### РАЗОБРАТЬСЯ С JSON Я ВООБЩЕ НИЧЕГО НЕ ПОНИМАЮЮЮЮЮЮЮ СОС 
    # апишка, можно авторов и жанры фильтровать, отдаёт json
    author = request.args.get('author')
    genre_id = request.args.get('genre')
    query = Book.query
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    if genre_id:
        query = query.join(Book.genres).filter(Genre.id == genre_id)
    books = query.all()
    return jsonify([{'title': b.title, 'author': b.author} for b in books])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # создаёт все таблички, если их нет
    app.run(debug=True)  # запускаем сервер