from manager import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    passwords = db.relationship('Password', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"


class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(100),nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    users = db.relationship(User)
    
    def __repr__(self):
        return f"Password('{self.id}','{self.site}','{self.username}','{self.image_file})"
