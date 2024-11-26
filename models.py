"""Models for authorising Users"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
import logging


db = SQLAlchemy()
bcrypt = Bcrypt()  # Initialize Bcrypt


class User(db.Model):
    """Users"""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    username = db.Column(
        db.String(20),
        unique=True,
        nullable=False,
    )

    password = db.Column(
        db.String(), 
        nullable=False,
    )

    email = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
    )

    first_name = db.Column(
        db.String(30),
        nullable=False,
    )

    last_name = db.Column(
        db.String(30),
        nullable=False,
    )

    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        """Register user with hashed password & return user."""
        
        # Ensure that the password is properly hashed and decoded
        hashed = bcrypt.generate_password_hash(pwd).decode('utf-8')
        
        # Create and return the user instance
        return cls(
            username=username,
            password=hashed,  # Store the hashed password
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

    @classmethod
    def authenticate(cls, username, pwd):
        """
        Validate that the user exists and the password is correct.
        Return the user if valid; else return False.
        """
        # Query the user by username
        user = cls.query.filter_by(username=username).first()

        logging.debug(f"Attempting to authenticate user: {username}")

        if user:
           
            try:
                # Check if the password matches the stored hash
                if bcrypt.check_password_hash(user.password, pwd):
                    
                    return user
            except ValueError:
                return False

        return False  # Invalid credentials
    
class Feedback(db.Model):
    """Feedback model."""

    __tablename__ = "feedback"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    title = db.Column(
        db.String(100),
        nullable=False,
    )

    content = db.Column(
        db.Text,
        nullable=False,
    )

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'),  #
        nullable=False,
    )

    user = db.relationship('User', backref=db.backref("feedbacks", lazy=True))



def connect_db(app):
    """Connect to the database."""
    db.app = app
    db.init_app(app)
