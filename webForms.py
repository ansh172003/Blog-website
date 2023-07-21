from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea


class UserForm(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired()])
    username = StringField("Enter your username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash_2', message="Passwords must match")])
    password2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class AddUserForm(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired()])
    username = StringField("Enter your username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash_2', message="Passwords must match")])
    password_hash_2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
