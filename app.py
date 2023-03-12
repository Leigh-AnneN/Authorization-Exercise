"""Feedback Flask app"""

from flask import Flask, flash, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, DeleteForm, FeedbackForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flask-feedback"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "shhhhh"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
# db.create_all()

@app.route("/")
def homepage():
    """Homepage of site. Redirect to register"""
    return redirect("/register")

@app.route('/secrets')
def show_secret():
      if "user_id" not in session:
            flash ("Please login first!")
            return redirect('/')
      """only show page to logged in/registered user """
      return render_template("secret.html")

@app.route("/register", methods = ['GET', 'POST'])
def register_user():
        """Register a user and produce a form, handle the form submission"""
        if "username" in session:
              return redirect (f"/users/{session['username']}")
        
        form = RegisterForm()

        if form.validate_on_submit():
              username = form.username.data
              password = form.password.data
              first_name = form.first_name.data
              last_name =  form.last_name.data
              email = form.email.data

              user = User.register(username, password, first_name, last_name, email)
              
              db.session.commit()
              session['username'] = user.username           
              return redirect(f"/users/{user.username}")

        else:
            return render_template('users/register.html', form=form)

@app.route("/login", methods = ['GET','POST'])
def login_user():
    """Login user by showing a login form and handling the form submission"""

    if "username" in session:
          return redirect(f"/users/{session['username']}")
    
    form = LoginForm()

    if form.validate_on_submit():
          username = form.username.data
          password = form.password.data

          user = User.authenticate(username,password) #<User> or False
          if user:
                flash(f"Welcome Back, {user.username}")
                session['username'] = user.username
                return redirect(f'/user/{user.username}')
          else: 
                form.username.errors = ['Invalid username/password']
                return render_template("users/login.html", form=form)
    
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
      session.pop('username')
      flash("Good-bye!")
      return redirect('/login')

@app.route('/users/<username>')
def show_user_info(username):
      """Show info about given user, and all feedback that user has given
      each piece of feedback has a form that allow editing"""
      if "username" not in session or username !=session['username']:
            raise Unauthorized()
      
      user = User.query.get(username)
      form = DeleteForm()

      return render_template("users/show.html", user=user, form=form)

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
      """Remove user and redirect to login"""

      if "username" not in session or username !=session['username']:
            raise Unauthorized()
      
      user = User.query.get(username)
      db.session.delete(user)
      db.session.commit()
      session.pop("username")

      return redirect ("/login")

@app.route('/users/<username>/feedback/new', methods=["GET", "POST"])
def new_feedback(username):
      """Show add feed back form and handle it"""

      if "username" not in session or username != session['username']:
            raise Unauthorized()
      
      form = FeedbackForm()

      if form.validate_on_submit():
            title = title.form.data
            content = content.form.data
          

            feedback = Feedback(
                  title = title,
                  content = content, 
                  username = username 
            )

            db.session.add(feedback)
            db.session.commit()

            return redirect (f"/users/{feedback.username}")
      
      else:
            return render_template("feedback/new.html", form=form)
      
@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """show update feedback form and process it"""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
          raise Unauthorized()
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
          feedback.title= form.title.data
          feedback.content= form.content.data

          db.session.commit()
          return redirect(f"/users/{feedback.username}")
    return render_template("/feedback/edit.html", form=form, feedback=feedback)