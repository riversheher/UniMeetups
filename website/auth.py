from flask import Blueprint, render_template, request, flash, redirect, url_for,session
from werkzeug.security import generate_password_hash, check_password_hash  #hash to store encrypted password
from flask_login import login_user, login_required, logout_user, current_user
from replit import db
from website.location_handling import get_closest_schools
from website.misc import get_tags
from website.user import User
import copy
import os
from website.misc import UPLOAD_PATH

# define form constants for sign up
MINIMUM_EMAIL_LENGTH = 5
MINIMUM_FULL_NAME_LENGTH = 5
MAX_FORM_LENGTH = 95
MINIMUM_PASSWORD_LENGTH = 10
MAXIMUM_PASSWORD_LENGTH = 40
MINIMUM_USERNAME_LENGTH = 5
MAXIMUM_USERNAME_LENGTH = 15

#defines auth blueprint view
auth = Blueprint('auth', __name__)


#login page (arg passed is the URL route to get to the page. It goes after master prefix)
#ie: if master prefix defined in init is /hi, then to get here we need /hi/login
#GET: When go to URL from url bar, POST when submit button (send info)
@auth.route('/login', methods=['GET',
                               'POST'])  #clarifies supported request types
def login():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        password = request.form.get('password1')

        #checks for any users in the database that match the email entered
        if email in db['users']:
            user_json = db['users'][email]
            user = User(email)
            if check_password_hash(user_json['password'], password):
                
                make_flash('Logged in successfully', category='yes')
                login_user(user, remember=True)
                user.authenticated = True
                return redirect(url_for('views.home'))

            else:
                make_flash('Login failed, wrong password','error')
                return redirect(url_for('auth.login'))

        #if user doesn't exist
        else:
            make_flash("USER DOES NOT EXIST!", category='error')
            return redirect(url_for('auth.login'))
      
    else:
        return render_template("login.html", user=current_user)

#logout page
@auth.route('/logout')
@login_required #login needed to access this page
def logout():
    user = current_user
    user.authenticated = False
    logout_user()
    make_flash('Successfully logged out', category='no')
    return redirect(url_for('auth.login'))


#sign up page
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    tags = get_tags()
    if request.method == 'POST':
        email = request.form.get('email')
        full_name = request.form.get('name')
        pw1 = request.form.get('password1')
        pw2 = request.form.get('password2')
        print(request.form)

      
        #No. 1: Name field must not be empty
        if len(full_name) not in range(MINIMUM_FULL_NAME_LENGTH,
                                       MAX_FORM_LENGTH + 1):
            make_flash(f'Name must be between {MINIMUM_FULL_NAME_LENGTH} and {MAX_FORM_LENGTH} characters', category='error')
            return redirect(url_for("auth.sign_up"))
                                         
        #No. 2: Email field must not be empty
        elif len(email) not in range(MINIMUM_EMAIL_LENGTH,
                                     MAX_FORM_LENGTH + 1):
            make_flash(f'Email must be between {MINIMUM_EMAIL_LENGTH} and {MAX_FORM_LENGTH} characters', category='error')
            return redirect(url_for("auth.sign_up"))

        #No. 3: Passwords must contain at least 8 characters
        elif len(pw1) not in range(MINIMUM_PASSWORD_LENGTH,
                                   MAXIMUM_PASSWORD_LENGTH + 1):
            make_flash(
                f'Password must be between {MINIMUM_PASSWORD_LENGTH} and {MAXIMUM_PASSWORD_LENGTH} characters',
                category='error')
            return redirect(url_for("auth.sign_up"))

        #No. 4: Passwords must match
        elif pw1 != pw2:
          make_flash('Passwords do not match', category='error')
          return redirect(url_for("auth.sign_up"))


        elif email in db["users"]:
          make_flash("An account associated with this email already exists!", category="error")
          return redirect(url_for("auth.sign_up"))
        else:
            # save_file_name = ".".join([full_name,file.filename.split(".")[1]])
            # file.save(os.path.join(UPLOAD_PATH,save_file_name))
            form_data = request.form
            form_keys = list(form_data.keys())
            selected_tags = [key for key in form_keys if key in tags]
            user_school = form_data["school"]
            user_data = {
              "email":email,
              "full_name":full_name,
              "password":generate_password_hash(pw1,"sha256"),
              "tags":selected_tags,
              "school":user_school
            }

              
            db['users'][email] = user_data
            
            return redirect(url_for("auth.sign_up2",email=email,name=full_name))
  
    else:
        user_ip = request.environ.get("HTTP_X_FORWARDED_FOR")
        closest_schools = get_closest_schools(user_ip)
        return render_template("sign-up.html",
                               user=current_user,
                               closest_schools=closest_schools,
                               tags=tags)


@auth.route('/sign_up2',methods=["GET","POST"])
def sign_up2():
  if request.method == "POST":
    if 
    file = request.files["file"]
    f_name = file.filename
    email = request.args.get("email")
    full_name = request.args.get("name")
    save_name = ".".join([full_name,f_name.split(".")[1]])
    file.save(os.path.join(UPLOAD_PATH,save_name))
    db["users"][email]["profile_photo"] = f"{UPLOAD_PATH}/{save_name}"
    make_flash("Account created succesfully!", "yes")
    return redirect(url_for("auth.login"))
  
  else:
    make_flash("Please select a profile picture!", "caution")
    return render_template("sign-up2.html",user=current_user)


    
def make_flash(message,category):
  session.pop('_flashes', None)
  flash(message, category)


# #settings page
# @auth.route('/settings', methods=['GET', 'POST'])
# #@login_required
# def settings():
  
#     if request.method == 'POST':

#         if request.form['submit'] == 'e':
#             email = request.form.get('email').lower()

#             if len(email) not in range(MINIMUM_EMAIL_LENGTH,
#                                        MAX_FORM_LENGTH + 1):
#                 make_flash('Email cannot be empty', category='error')
#                 return redirect(url_for("auth.settings"))

#             else:
              
#               user = current_user
#               old_key = user.get_id()
#               print(old_key)
#               copy_data = copy.deepcopy(db["users"][old_key])
#               del db['users'][old_key]
#               db["users"][email] = copy_data
#               user.id = email
#               make_flash('Email has been updated successfully', category='yes')
#               return redirect(url_for("auth.settings"))
              
#         if request.form['submit'] == 'p':
#             pw1 = request.form.get('password1')
#             pw2 = request.form.get('password2')

#             if len(pw1) not in range(MINIMUM_PASSWORD_LENGTH,
#                                      MAXIMUM_PASSWORD_LENGTH + 1):
#                 make_flash('INVALID PASSWORD', category='error')
#                 return redirect(url_for("auth.settings"))

#             elif pw1 != pw2:
#                 make_flash('PASSWORDS DONT MATCH', category='error')
#                 return redirect(url_for("auth.settings"))

#             else:
#               user = current_user
#               cur_email = user.get_id()
#               db["users"][cur_email]["password"] = pw1
#               make_flash('Password has been updated successfully', category='yes')
#               return redirect(url_for("auth.settings"))

#         if request.form['submit'] == 'n':
#             name = request.form.get('name')

#             if len(name) not in range(MINIMUM_FULL_NAME_LENGTH,
#                                       MAX_FORM_LENGTH + 1):
#                 make_flash(
#                     f'Name must be between {MINIMUM_FULL_NAME_LENGTH} and {MAX_FORM_LENGTH} characters',
#                     category='error')
#                 return redirect(url_for("auth.settings"))

#             else:
#               user = current_user
#               cur_email = user.get_id()
#               db["users"][cur_email]['name'] = name
#               make_flash('Password has been updated successfully', category='yes')
#               return redirect(url_for("auth.settings"))

#     else:
#         return render_template("settings.html", user=current_user)
