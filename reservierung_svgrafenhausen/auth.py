from reservierung_svgrafenhausen.models import Event, User
from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .getSeatNumber import get_seat_number

import re
REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

auth = Blueprint('auth', __name__)


@auth.route('/home', methods=['GET', 'POST'])
@auth.route('/', methods=['GET', 'POST'])
def sign_up():
    
    if request.method == 'POST' and 'password1' in request.form and 'password2' in request.form:
        email = request.form.get('email')

        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')

        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        valid = True

        # Check if the user with this email is already in the database. If so -> throw error message
        if User.query.filter_by(email=email).first() is not None:
            flash("Diese E-Mail Adresse wird bereits verwendet. Loggen Sie sich ein, oder versuchen Sie eine andere E-Mail Adresse!", category="error")
            valid = False

        # Check if the given E-Mail adress is valid
        if(not re.match(REGEX, email)):
            flash("Eine ungültige E-Mail Adresse wurde eingegeben. Versuchen Sie eine andere Adresse!", category="error")
            valid = False

        # Check if the given first name is valid
        if (len(first_name) <= 2):
            flash("Eine ungültiger Vornamen wurde eingegeben. Der Vorname muss mindestens drei (3) Buchstaben enthalten!", category="error")
            valid = False

        # Check if the given second name is valid
        if (len(last_name) <= 2):
            flash("Eine ungültiger Nachnamen wurde eingegeben. Der Nachnamen muss mindestens drei (3) Buchstaben enthalten!", category="error")
            valid = False

        # Check if the given passwords match
        if (password1 != password2):
            flash("Die eingegebenen Passwörter stimmen nicht überein. Versuchen Sie es erneut!", category="error")
            valid = False

        # Check if the matching passwords has the minimal number of chars
        elif (len(password1) <= 5):
            flash("Das eingegebene Passwort muss mindestens sechs (6) Zeichen enthalten!", category="error")
            valid = False

        
        # If all the checks have passed -> create user in the DB
        if (valid):
            # Create the new user based on the parameters
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(password1, method='sha256'))

            # Add the user to the database
            db.session.add(new_user)
            db.session.commit()

            # Login the user and therefore create a remembered session  
            login_user(new_user, remember=True)

            flash('Sie haben erfolgreich einen Account erstellt!', category='success')

            return redirect(url_for('views.reservierung'))


    elif request.method == 'POST' and 'password' in request.form:
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
        
                login_user(user, remember=True)
                
                if current_user.admin:
                    return redirect(url_for('auth.admin'))
                
                else:
                    flash('Sie haben sich erfolgreich angemeldet!', category='success')
                    return redirect(url_for('views.reservierung'))

            else:
                flash('Das eingegebene Passwort ist falsch. Versuchen Sie es erneut!', category='error')
        else:
            flash('Die eingegebene E-Mail Adresse ist nicht vorhanden. Versuchen Sie eine andere oder registrieren Sie sich!', category='error')

    s = get_seat_number()

    return render_template("home.html", seat_number=int(s), user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sie haben sich erfolgreich abgemeldet!', category='success')
    return redirect(url_for('auth.sign_up'))


@auth.route('/admin')
@login_required
def admin():
    if current_user.admin is False:
        return redirect(url_for('auth.sign_up'))

    
    result = []
    tmp_users = User.query.all()

    for user in tmp_users:
        result.append((user, user.events))


    return render_template("admin.html", user=current_user, result=result)
