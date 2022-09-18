from flask import Flask, render_template, g, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, FloatField
from wtforms.validators import Email, Length, InputRequired, EqualTo, DataRequired, NumberRange
# I have done this before. which makes this project slighlty easier

import db # if error, right-click parent directory "mark directory as" "sources root"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Funnykey'


@app.before_request
def before_request():
    db.open_db_connection()


@app.teardown_request
def teardown_request(exception):
    db.close_db_connection()



#Login checkder
def checkLogin(returnPage):
    if loggedIn():
        return render_template(returnPage)
    else:
        return redirect(url_for('login_page'))


# login 
class LoginForm(FlaskForm):
    valid_pword = []
    email = StringField('Email')
    password = PasswordField('Password')
    submit = SubmitField('Log In')

@app.route('/login', methods=['GET','POST'])
def login_page():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        validationResult = db.authenticate(login_form.email.data, login_form.password.data)
        if validationResult[0]:
            print(session,validationResult)
            session['email'] = login_form.email.data
            session['userID'] = validationResult[1]['id']
            session['userData'] = validationResult[1]
            #db.update_user_status(session['userID'],1)
            return redirect(url_for('user_details',email= validationResult[1]['email']))
        else:
            flash('Login Incorrect')
    return render_template('login.html', form=login_form)



def loggedIn():
    if 'userID' not in session:
        return False 
    else:
        return True


@app.route('/logout')
def logout():
    #session = []
    return redirect(url_for('index'))


@app.route('/')
def index(): # if not logged in
    return render_template('index.html') # will display user email and first name and last name



@app.route('/users/<email>')
def user_details(email):
    print("finding user",email)
    return render_template('user-details.html', user=db.find_user(email))



class UserForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    first_name = StringField('First Name', validators=[Length(min=1, max=40)])
    last_name = StringField('Last Name', validators=[Length(min=1, max=40)])
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')


@app.route('/register', methods=['GET', 'POST'])
def create_user():

    user_form = UserForm()

    # The validate_on_submit() method checks for two conditions.
    # 1. If we're handling a GET request, it returns false,
    #    and we fall through to render_template(), which sends the empty form.
    # 2. Otherwise, we're handling a POST request, so it runs the validators on the form,
    #    and returns false if any fail, so we also fall through to render_template()
    #    which renders the form and shows any error messages stored by the validators.
    if user_form.validate_on_submit():
        use = db.find_user(user_form.email.data)

        if use is not None:
            flash("user {} already exists".format(user_form.email.data))
        else:
            rowcount = db.create_user(user_form.email.data,
                                        user_form.first_name.data,
                                        user_form.last_name.data,
                                        user_form.password.data)

            if rowcount == 1:
                flash("you've been registered! please login: {}".format(user_form.email.data))
                return redirect(url_for('index'))
            else:
                flash("New user not created")

    # We will get here under any of the following conditions:
    # 1. We're handling a GET request, so we render the (empty) form.
    # 2. We're handling a POST request, and some validator failed, so we render the
    #    form with the same values so that the user can try again. The template
    #    will extract and display the error messages stored on the form object
    #    by the validators that failed.
    # 3. The email entered in the form corresponds to an existing user.
    #    The template will render an error message from the flash.
    # 4. Something happened when we tried to update the database (rowcount != 1).
    #    The template will render an error message from the flash.
    return render_template('user-form.html', form=user_form)


app.run(debug=True)