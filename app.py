#Imports
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_socketio import *
from models import *
from config import *
from werkzeug.security import check_password_hash
from datetime import datetime
#Fin Imports
app = Flask(__name__)
setup(app)
migrate = Migrate(app, db)
db.init_app(app)
socketio = SocketIO(app)

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
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/chat/sala')
def sala():
    return render_template('sala.html')




def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')







@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    app.logger.debug(rooms())
    
    listaSalas = rooms()
    sala = listaSalas[0]
    socketio.emit('my response', json, callback=messageReceived, to = sala)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    app.logger.debug(username)
    
    join_room(room)
    emit('redirect', url_for('sala'), room = [room])
    emit('user joined',username + " ha entrado en la sala.", to = room)
    app.logger.debug(rooms())

    

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('user left',username + " has left the room.", to = room)

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





if __name__ == "__main__":
    socketio.run(app, debug = True)
