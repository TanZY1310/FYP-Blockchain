# from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models import User

#from web.models import which class

class LoginForm(FlaskForm):
    user_name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    #User details 
    user_name = StringField('Name',  validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = StringField('Role', validators=[DataRequired()]) #test dropdown role

    # supplier = BooleanField('Supplier')
    # manufacturer = BooleanField('Manufacturer') #find a way to separate three users
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

    # Adress
    street = StringField('Street', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State')
    zip_code = StringField('ZIP Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])

    submit = SubmitField('Register')

    def validate_name(self, user_name):
        user = User.query.filter_by(user_name = user_name.data).first()
        if user is not None:
            raise ValidationError("Please use a different name.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ProductForm(FlaskForm):
    product_name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Add new product')

class BatchForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired()])



