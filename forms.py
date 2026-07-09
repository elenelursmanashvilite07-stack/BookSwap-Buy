from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms import PasswordField
from wtforms.validators import Email, EqualTo
from flask_wtf.file import FileField

class RegisterForm(FlaskForm):

    username = StringField(
        "მომხმარებლის სახელი",
        validators=[DataRequired()]
    )

    email = StringField(
        "ელფოსტა",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "პაროლი",
        validators=[DataRequired()]
    )

    confirm_password = PasswordField(
        "გაიმეორე პაროლი",
        validators=[
            DataRequired(),
            EqualTo("password")
        ]
    )

    submit = SubmitField("რეგისტრაცია")

class LoginForm(FlaskForm):

    username = StringField(
        "მომხმარებლის სახელი",
        validators=[DataRequired()]
    )

    password = PasswordField(
        "პაროლი",
        validators=[DataRequired()]
    )

    submit = SubmitField("შესვლა")

class BookForm(FlaskForm):

    title = StringField(
        "📖 წიგნის სახელი",
        validators=[DataRequired()]
    )

    author = StringField(
        "✍️ ავტორი",
        validators=[DataRequired()]
    )

    genre = SelectField(
        "📚 ჟანრი",
        choices=[
            ("ფანტასტიკა", "ფანტასტიკა"),
            ("რომანი", "რომანი"),
            ("დეტექტივი", "დეტექტივი"),
            ("ისტორიული", "ისტორიული"),
            ("ბიოგრაფია", "ბიოგრაფია"),
            ("სხვა", "სხვა")
        ],
        validators=[DataRequired()]
    )

    condition = SelectField(
        "⭐ მდგომარეობა",
        choices=[
            ("ახალი", "ახალი"),
            ("ძალიან კარგი", "ძალიან კარგი"),
            ("კარგი", "კარგი"),
            ("გამოყენებული", "გამოყენებული")
        ],
        validators=[DataRequired()]
    )

    description = TextAreaField(
        "📝 აღწერა"
    )

    price = FloatField(
        "💰 ფასი",
        validators=[DataRequired()]
    )

    image = FileField("📷 წიგნის ფოტო (არასავალდებულო)")


    submit = SubmitField("📚 წიგნის დამატება")