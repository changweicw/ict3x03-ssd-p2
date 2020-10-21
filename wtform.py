from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, FileField, DecimalField, SubmitField
from wtforms.validators import DataRequired


class RegistrationForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class publishForm(FlaskForm):
    title = StringField("title")
    desc = StringField("desc")
    price = DecimalField("price")
    files = FileField("files")
