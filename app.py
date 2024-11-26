"""Flask app Authentication"""
from flask import Flask, render_template, redirect, session, flash , url_for
from flask_debugtoolbar import DebugToolbarExtension
from forms import UserForm , LoginForm , FeedbackForm
from models import connect_db, db , User , Feedback
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///user_authen"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.app_context().push() 

connect_db(app)

debug = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = UserForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        email = form.email.data
        password = form.password.data

        new_user = User.register(first_name, last_name, username, email, password)
        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username is taken. Please pick another")
            form.email.errors.append("Email is taken. Please pick another")
            return render_template('register.html', form=form)

        session['user_id'] = new_user.id
        return redirect(url_for('secret_page', username=username))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!")
            session['user_id'] = user.id
            return redirect(url_for('secret_page', username=username))  
        else:
            form.username.errors = ['Invalid username or password.']

    return render_template('login.html', form=form)


@app.route('/logout', methods = ['GET','POST'])
def logout_user():
    if 'user_id' in session: 
        session.pop('user_id')  
        flash("Goodbye!")
       
    return redirect('/')

@app.route('/users/<username>')
def secret_page(username):
    if 'user_id' not in session:
        flash("You must be logged in to view that page.")
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    
    if user.username != username:
        flash('You dont have authorization to view this page')
        return redirect("/login")
    
    user_feedback = Feedback.query.filter_by(user_id=user.id).all()
    return render_template('secret.html', user=user , user_feedback = user_feedback)

@app.route('/users/<username>/delete', methods = ['POST'])
def delete_user(username):
    if 'user_id' not in session:
        flash("You must be logged in Delete account.")
        return redirect('/login')
    user = User.query.get(session['user_id'])

    if user.username != username:
        flash('You dont have authorization to Delete this accouunt')
        return redirect("/login")
    
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash("Your account has been deleted.")
    return redirect ('/')

@app.route('/users/<username>/feedback/add', methods = ['GET','POST'])
def feedback_add(username):
    form = FeedbackForm()
    user = User.query.get(session['user_id'])

    if user.username != username:
        flash('You dont have authorization to add feedback.')
        return redirect("/login")

    if form.validate_on_submit():
        title= form.title.data
        content = form.content.data

        new_feedback = Feedback(title=title, content=content, user_id=user.id)
        db.session.add(new_feedback)
       
        db.session.commit()
        flash('Feedback added successfully!', 'success')
        return redirect(url_for('secret_page', username=username))

    return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def feedback_patch(feedback_id):
    form = FeedbackForm()
    user = User.query.get(session['user_id'])
    feedback = Feedback.query.get(feedback_id)

    if not feedback:
        flash('Feedback not found')
        return redirect(url_for('secret_page', username=user.username))

    if feedback.user_id != user.id:
        flash('You don’t have authorization to edit this feedback.')
        return redirect(url_for('secret_page', username=user.username))

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()

        flash('Feedback updated successfully!', 'success')
        return redirect(url_for('secret_page', username=user.username))

    form.title.data = feedback.title
    form.content.data = feedback.content

    return render_template('update_feedback.html', form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods = ['POST'])
def delete_feedback(feedback_id):
    
    if 'user_id' not in session:
        flash("You must be logged in Delete this feedback.")
        return redirect('/login')
    user = User.query.get(session['user_id'])
    feedback = Feedback.query.get(feedback_id)
    
    if not feedback:
        flash("Feedback not found.")
        return redirect(url_for('secret_page', username=user.username))

    if feedback.user_id != user.id:
        flash('You dont have authorization to Delete this feedback.')
        return redirect(url_for('secret_page', username=user.username))
    
    db.session.delete(feedback)
    db.session.commit()
  

    flash("Your feedback has been deleted.")
    return redirect(url_for('secret_page', username=user.username))