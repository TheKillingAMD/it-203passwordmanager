from manager import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    passwords = db.relationship('Password', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Password('{self.site}','{self.username}')"