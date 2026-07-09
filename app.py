from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for
from forms import BookForm, RegisterForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


app.config["SECRET_KEY"] = "my_secret_key_123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Book(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


    def __repr__(self):
        return f"<Book {self.title}>"

class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(50), unique=True, nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
        password = db.Column(db.String(200), nullable=False)
        is_admin = db.Column(db.Boolean, default=False)

@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.username.data
        ).first()

        if user and check_password_hash(user.password, form.password.data):

            login_user(user)

            return redirect(url_for("home"))

        flash("არასწორი მომხმარებელი ან პაროლი.")
        return redirect(url_for("login"))

    return render_template(
        "login.html",
        form=form
    )

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("home"))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():

    total_books = Book.query.count()

    return render_template(
        "home.html",
        total_books=total_books
    )

@app.route("/books")
def books():

    search = request.args.get("search")

    if search:
        books = Book.query.filter(
            Book.title.contains(search)
        ).all()
    else:
        books = Book.query.all()

    return render_template(
        "books.html",
        books=books
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/add-book", methods=["GET", "POST"])
@login_required
def add_book():
    form = BookForm()

    if form.validate_on_submit():
        filename = None

        if form.image.data:
            image = form.image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        new_book = Book(
            title=form.title.data,
            author=form.author.data,
            genre=form.genre.data,
            condition=form.condition.data,
            description=form.description.data,
            price=form.price.data,
            image=filename,
            user_id=current_user.id
        )

        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for("books"))

    return render_template(
        "add_book.html",
        form=form,
        title="წიგნის დამატება",
        button="დამატება"
    )

@app.route("/delete-book/<int:id>")
@login_required
def delete_book(id):


    book = Book.query.get_or_404(id)
    if not current_user.is_admin and book.user_id != current_user.id:
        flash("თქვენ არ გაქვთ ამ წიგნის წაშლის უფლება.")
        return redirect(url_for("books"))

    db.session.delete(book)
    db.session.commit()

    return redirect(url_for("books"))

@app.route("/edit-book/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):

    book = Book.query.get_or_404(id)

    if not current_user.is_admin and book.user_id != current_user.id:
        flash("თქვენ არ გაქვთ ამ წიგნის რედაქტირების უფლება.")
        return redirect(url_for("books"))

    form = BookForm(obj=book)

    if form.validate_on_submit():
        if form.image.data and hasattr(form.image.data, "filename"):
            image = form.image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            book.image = filename
        book.title = form.title.data
        book.author = form.author.data
        book.genre = form.genre.data
        book.condition = form.condition.data
        book.description = form.description.data
        book.price = form.price.data

        db.session.commit()

        return redirect(url_for("books"))

    return render_template(
        "add_book.html",
        form=form,
        title="წიგნის რედაქტირება",
        button="შენახვა"
    )

@app.route("/book/<int:id>")
def book_detail(id):

    book = Book.query.get_or_404(id)

    return render_template(
        "book_detail.html",
        book=book
    )

@app.route("/buy/<int:id>")
@login_required
def buy_book(id):

    book = Book.query.get_or_404(id)

    flash(f"თქვენ წარმატებით აირჩიეთ '{book.title}'. გამყიდველი მალე დაგიკავშირდებათ.")

    return redirect(url_for("books"))

@app.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        existing_user = User.query.filter(
            (User.username == form.username.data) |
            (User.email == form.email.data)
        ).first()

        if existing_user:
            if existing_user.username == form.username.data:
                form.username.errors.append("ეს მომხმარებლის სახელი უკვე გამოყენებულია.")

            if existing_user.email == form.email.data:
                form.email.errors.append("ეს ელფოსტა უკვე გამოყენებულია.")

            return render_template("register.html", form=form)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )

        db.session.add(new_user)
        db.session.commit()

        flash("რეგისტრაცია წარმატებით დასრულდა. ახლა შედით სისტემაში.")
        return redirect(url_for("login"))

    return render_template(
        "register.html",
        form=form
    )

@app.route("/make-admin/<username>")
@login_required
def make_admin(username):

    if not current_user.is_admin:
        flash("თქვენ არ გაქვთ ამ მოქმედების უფლება.")
        return redirect(url_for("home"))

    user = User.query.filter_by(username=username).first()

    if user:
        user.is_admin = True
        db.session.commit()
        flash("მომხმარებელი გახდა ადმინი.")

    return redirect(url_for("home"))

@app.route("/delete-user/<int:id>")
@login_required
def delete_user(id):

    if not current_user.is_admin:
        return "წვდომა აკრძალულია."

    user = User.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for("home"))


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)