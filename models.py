from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()


class UserModel(db.Model, UserMixin):
    __tablename__ = 'Usuarios'

    id = db.Column(db.String(), primary_key=True)
    email = db.Column(db.String(), nullable = False, unique = True)
    name = db.Column(db.String(), nullable = False, unique = True)
    password = db.Column(db.String(), nullable = False)

    def __init__(self, name, email, password):
        self.id = uuid.uuid4()
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<Nombre: {self.name} - Email: {self.email}>"



class EventModel(db.Model):
    __tablename__ = 'Eventos'

    id = db.Column(db.String(), primary_key=True)
    title = db.Column(db.String(), nullable = False)
    start = db.Column(db.DateTime(), nullable = False)
    end = db.Column(db.DateTime(), nullable = False)
    backgroundColor = db.Column(db.String(), nullable = False)

    def __init__(self, title, start, end, backgroundColor):
        self.id = current_user.name + "%" + str(uuid.uuid4())
        self.title = title
        self.start = start
        self.end = end
        self.backgroundColor = backgroundColor

    def __repr__(self):
        return f"<Título: {self.title}>"