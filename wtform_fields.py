from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Length, EqualTo, Email
from wtforms.fields.html5 import DecimalRangeField
import email_validator

class RegistrationForm(FlaskForm):
    username = StringField('username_label', 
        validators=[InputRequired(message="Username required"),
        Length(min=4, max=25, message="Username must be between 4 and 25 characters")])
    
    email = StringField('email_label', 
        validators=[InputRequired(message="Email required"),
        Email("This field requires a valid email")])
    
    password = PasswordField('password_label', 
        validators=[InputRequired(message="Password required"),
        Length(min=4, max=25, message="Password must be between 4 and 25 characters")])
    
    confirm_password = PasswordField('confirm_password_label', 
        validators=[InputRequired(message="Password required"),
        EqualTo('password', message="Passwords must match")])
    

    submit_button = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('username_label', 
        validators=[InputRequired(message="Username required")])
    
    password = PasswordField('password_label', 
        validators=[InputRequired(message="Password required")])

    submit_button = SubmitField('Sign In')

class Search(FlaskForm):
    search_input = StringField('search_input_label', 
        validators=[InputRequired(message="Provide a valid input")])
    
    submit_button = SubmitField('Search')

class Review(FlaskForm):
    review = TextAreaField('Review message', validators=[InputRequired(message="Please provide a valid input")])
    rate = DecimalRangeField('Rate', default=0)

    submit_button = SubmitField('Post Review')

class Edit(FlaskForm):
    response = TextAreaField('Review message')

    submit_button = SubmitField('Update Review')