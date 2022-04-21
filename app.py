#Imports
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_socketio import *
from psycopg2 import Date
from models import *
from config import *
from werkzeug.security import check_password_hash
from datetime import *
from time import *
#Fin Imports
app = Flask(__name__)
setup(app)
migrate = Migrate(app, db)
db.init_app(app)
socketio = SocketIO(app, manage_session=False)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Necesitas iniciar sesión para ver esta página"

db.init_app(app)


@app.route('/')
def index():
    # ELIMINAR O EDITAR A POSTERIORI, AHORA CON ACCESO A PÁGINAS PARA TESTEO
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Inicia con el método GET
    email = request.form.get('email')
    password = request.form.get('password')
    user = UserModel.query.filter_by(email=email).first()

    # Al rellenar el formulario y presionar el botón pasa por la verficación
    if request.method == 'POST':
        if user and check_password_hash(user.password, password):
            app.logger.debug(request.form.get('remember'))
            
            login_user(user, remember= request.form.get('remember'))
            return redirect(url_for('saludo'))
        elif not user:
            flash("Usuario no encontrado")
        elif not check_password_hash(user.password, password):
            flash("Contraseña incorrecta")
        return render_template('login.html')
    # Carga de HTML del método GET
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    created = False
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmpassword = request.form.get('confirmpassword')

        # Verifica si el email está en uso o no
        emailRegistered = UserModel.query.filter_by(email=email).first()
        # Verifica si el nombre está en uso o no
        nameInUse = UserModel.query.filter_by(name=username).first()

        # Validación del registro
        if password != confirmpassword:
            flash("Las contraseñas no coinciden")
        elif emailRegistered:
            flash("Email ya registrado")
        elif nameInUse:
            flash("Nombre ya en uso")
        # Si está todo bien crea el usuario
        else:
            new_user = UserModel(name=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            created = True
            flash("Usuario registrado exitosamente")

        return render_template('signup.html', created=created)
    # Carga de HTML del método GET
    return render_template('signup.html', created=created)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/saludo')
@login_required
def saludo():
    return render_template('pruebaLoginRequired.html')

@app.route('/calendario', methods=['GET', 'POST'])
@login_required
def calendario():

    if request.method == 'POST':
        app.logger.debug("Valor del action: " + str(request.form.get('action')))
        app.logger.debug("Entra al método POST")
        
        # Añadir evento
        if request.form.get('action') == "add":
            title = request.form.get('title')
            start = str(request.form.get('startDate')) + " " + \
                str(request.form.get('startTime'))
            end = str(request.form.get('endDate')) + " " + \
                str(request.form.get('endTime'))
            color = request.form.get('eventColor')
            

            if validarFechas(start,end):
                new_event = EventModel(title=title, start=start, end=end, backgroundColor=color)            
                db.session.add(new_event)
                db.session.commit()


        # Eliminar evento
        elif request.form.get('action') == "delete":
            app.logger.debug("Entra al delete")
                        
            id = request.form.get('changeID')
            evento = EventModel.query.filter_by(id=id).first()
            app.logger.debug(evento.title)
            db.session.delete(evento)
            db.session.commit()

        # Actualizar evento
        elif request.form.get('action') == "update":
            app.logger.debug("Entra al update")
            
            id = request.form.get('changeID')
            newTitle = request.form.get('changeTitle')
            newStart = str(request.form.get('changeStartDate')) + " " + str(request.form.get('changeStartTime'))
            newEnd = str(request.form.get('changeEndDate')) + " " + str(request.form.get('changeEndTime'))
            newColor = request.form.get('changeEventColor')


            if validarFechas(newStart, newEnd):
                EventModel.query.filter_by(id=id).update(
                    dict(title=newTitle, start=newStart, end=newEnd, backgroundColor=newColor))
                db.session.commit()

        return render_template('calendario.html')

    app.logger.debug("Prueba flask log")
    return render_template('calendario.html')

#Chat
@app.route("/chat", methods=['GET', 'POST'])
def chat():
    ROOMS = ["lounge", "news", "games", "coding", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a"]

    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))
    return render_template("chat.html", username=current_user.name, rooms=ROOMS)

@socketio.on('loadHistorial')
def on_load(data):
    mensaje1 = mensaje("user1", "Mensaje 1", datetime.now())
    mensaje2 = mensaje("user2", "Mensaje 2", datetime.now())
    mensaje3 = mensaje("user1", "Mensaje 3", datetime.now())
    mensaje4 = mensaje("user2", "Mensaje 4", datetime.now())
    mensajes = [mensaje1, mensaje2, mensaje3, mensaje4]    
    room = data["room"]
    for msg in mensajes:      
        send({"username": msg.usuario, "msg": msg.mensaje, "time_stamp": str(msg.tiempo)}, room=room)


@socketio.on('incoming-msg')
def on_message(data):
    """Broadcast messages"""
    msg = data["msg"]
    username = data["username"]
    room = data["room"]
    # Set timestamp
    time_stamp = datetime.strftime(datetime.now(),'%b-%d %I:%M%p')
    send({"username": username, "msg": msg, "time_stamp": time_stamp}, room=room)


@socketio.on('join')
def on_join(data):
    """User joins a room"""

    username = data["username"]
    room = data["room"]
    join_room(room)

    # Broadcast that new user has joined
    send({"msg": username.capitalize() + " ha entrado en la sala " + room }, room=room)


@socketio.on('leave')
def on_leave(data):
    """User leaves a room"""

    username = data['username']
    room = data['room']
    leave_room(room)
    send({"msg": username.capitalize() + " ha abandonado la sala"}, room=room)

#Fin chat






# Extra
@login_manager.user_loader
def load_user(user_id):
    user = UserModel.query.filter_by(id=user_id).first()
    if user:
        return user
    return None

def event_loader(user_name):
    eventos = []
    events = db.session.query(EventModel).filter(
        EventModel.id.match(user_name)).all()
    for evento in events:

        if not (evento.end.date() < datetime.now().date()):
            eventos.append(            
                {
                    "id": evento.id,
                    "title": evento.title,
                    "start": evento.start.isoformat(),
                    "end": evento.end.isoformat(),
                    "backgroundColor": evento.backgroundColor
                }
            )

    return jsonify(eventos)

@app.route('/eventos')
@login_required
def eventos():
    return event_loader(current_user.name)

def validarFechas(start, end):
    if datetime.strptime(end, "%Y-%m-%d %H:%M") > datetime.strptime(start, "%Y-%m-%d %H:%M"):
        return True
    else:
        return False










class mensaje:
    def __init__(self, usuario, mensaje, tiempo):
        self.usuario = usuario
        self.mensaje = mensaje
        self.tiempo = tiempo
        


if __name__ == "__main__":
    socketio.run(app, debug = True)
