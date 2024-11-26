from app import app
from models import db, User, Feedback

db.drop_all()
db.create_all()

# Create users
u1 = User(
    username="cherry234",
    password="large123",
    email='meemer@gmail.com',
    first_name='greg',
    last_name='nonono'
)

u2 = User(
    username="king234",
    password="mouse123",
    email='meowers@gmail.com',
    first_name='Shawn',
    last_name='lickername'
)

db.session.add_all([u1, u2])
db.session.commit()


f1 = Feedback(
    title='feedbacky1',
    content='Some feedback content for user 1.',
    user_id= 1  
)

f2 = Feedback(
    title='feedbacky2',
    content='Some feedback content for user 2.',
    user_id= 2
)

db.session.add_all([f1, f2])
db.session.commit()






