# INICIO DE IMPORTS

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_socketio import *
from models import *
from config import *
from werkzeug.security import check_password_hash
from datetime import *
from time import *

# FINAL DE IMPORTS
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO DE CONFIGURACION

app = Flask(__name__)
setup(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, manage_session=False)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Necesitas iniciar sesión para ver esta página"

db.init_app(app)

def create_app():
    app = Flask(__name__)
    setup(app)
    db.init_app(app)
    return app

@login_manager.user_loader
def load_user(user_id):
    user = UserModel.query.filter_by(id=user_id).first()
    if user:
        return user
    return None



@app.route('/eventos')
@login_required
def eventos():
    return event_loader()

# FINAL DE CONFIGURACION
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO DE RUTAS VISIBLES

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
            flash("Usuario creado")
            return render_template('login.html')

        return render_template('signup.html', created=created)
    # Carga de HTML del método GET
    return render_template('signup.html', created=created)

@app.route('/logout')
@login_required
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

    grupos = myGroup_loader()
    gruposPertenece = []
    gruposAdmin = []

    for grupo in grupos:
        gruposPertenece.append(grupo[0])
        if esAdmin(grupo[0]):
            gruposAdmin.append(grupo[0])  

    if request.method == 'POST':
        # Añadir evento
        if request.form.get('action') == "add":            

            admin = esAdmin(request.form.get('eventGroup'))
            if admin:
                crearEvento()

        # Eliminar evento
        elif request.form.get('action') == "delete":
            admin = esAdmin(request.form.get('changeEventGroup'))
            if admin:
                eliminarEvento()

        # Actualizar evento
        elif request.form.get('action') == "update":
            admin = esAdmin(request.form.get('changeEventGroup'))
            if admin:
                actualizarEvento()

        return render_template('calendario.html', grupos = gruposAdmin, gruposPertenece = gruposPertenece, admin = admin)

    return render_template('calendario.html', grupos = gruposAdmin, gruposPertenece = gruposPertenece, admin = True)

@app.route('/grupos' , methods=['GET', 'POST'])
@login_required
def grupos():
    grupos = group_loader()

    if request.method == 'POST':
        alertar = True    
        action = request.form.get('action')

        if action == "enter": 
            name = request.form.get("enterName")
            password = request.form.get("enterPass")
            correcto = comprobarPass(name, password)
            if not correcto:
                flash("Contraseña incorrecta")
            else:
                dentro = enterGroup(name)
                if dentro:
                    flash("Ya te encuentras en el grupo")
                else:
                    flash("Te has unido sin problemas")
                

        elif action == "search":
            resultado = buscador(request.form.get('search'))
            if len(resultado) == 0:
                flash("No se ha encontrado ningún grupo")
            else:
                alertar = False
                grupos = resultado

        elif action == "create":
            name = request.form.get('createName')
            password = request.form.get('createPass')
            confPass = request.form.get('createConfPass')
            msg = crearGrupo(name, password, confPass)
            flash(msg)
        
        return render_template('grupos.html', len = len(grupos), lista = grupos, alertar = alertar)
        
    return render_template('grupos.html', len = len(grupos), lista = grupos, alertar = False)

@app.route('/misGrupos' , methods=['GET', 'POST'])
@login_required
def misGrupos():
    grupos = myGroup_loader()
    
    if request.method == 'POST':
        clicado = request.form.get('grupoClicado')
        return redirect(url_for('misGruposGrupo', grupo = clicado))
        

    return render_template('misGrupos.html', len = len(grupos), lista = grupos)

@app.route('/misGrupos/<grupo>')
@login_required
def misGruposGrupo(grupo):
    if GroupModel.query.filter_by(name = grupo).first().owner == current_user.name:
        return "<h1>Este es el grupo "+grupo+"</h1>"
    else:
        return redirect(url_for('index'))

# FINAL DE RUTAS VISIBLES
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO MÉTODOS GRUPOS

def group_loader():
    allGroups = []
    grupos = GroupModel.query.order_by(GroupModel.name).all()
    for grupo in grupos:
        admins = []
        for admin in GrupoUserRelation.query.filter_by(grupo = grupo.name).filter_by(admin = 'Y').with_entities(GrupoUserRelation.user).all():
            admins.append(admin[0])
        allGroups.append((grupo.name, admins))
    
    return allGroups

def buscador(search):
    grupos = GroupModel.query.filter(GroupModel.name.like("%" + search.upper() + "%")).all()
    return grupos

def crearGrupo(name, password, confPassword):
    grupo = GroupModel.query.filter_by(name = name.upper()).all()
    if grupo:
        return "Grupo ya existente"
    elif password != confPassword:
        return "Las contraseñas no coinciden"
    else:
        new_group = GroupModel(name = name.upper(), password = password, owner = current_user.name)
        new_relation = GrupoUserRelation(grupo = name.upper(), user = current_user.name, admin = "Y")
        db.session.add(new_group)
        db.session.add(new_relation)
        db.session.commit()
        return "Grupo creado exitosamente"

def comprobarPass(name, password):
    grupo = GroupModel.query.filter_by(name = name).first()
    return password == grupo.password

def enterGroup(groupName):
    miembrosTEMP = GrupoUserRelation.query.with_entities(GrupoUserRelation.user).filter_by(grupo = groupName).all()
    miembros = []
    for miembro in miembrosTEMP:
        miembros.append(miembro[0])
    

    if current_user.name in miembros:
        return True
    else:
        nuevo_miembro = GrupoUserRelation(grupo = groupName, user = current_user.name, admin = "N")
        db.session.add(nuevo_miembro)
        db.session.commit()

def esAdmin(grupo):
    
    admin = GrupoUserRelation.query.with_entities(GrupoUserRelation.admin).filter_by(grupo = grupo).filter_by(user = current_user.name).first()
    if admin[0] == 'Y':
        return True
    else:
        return False
    
    

# FINAL MÉTODOS GRUPOS
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO MÉTODOS MIS GRUPOS

def myGroup_loader():
    misGrupos = []
    grupos = GrupoUserRelation.query.filter_by(user = current_user.name).order_by(GrupoUserRelation.grupo).all()
    for grupo in grupos:
        admins = []
        for admin in GrupoUserRelation.query.filter_by(grupo = grupo.grupo).filter_by(admin = 'Y').with_entities(GrupoUserRelation.user).all():
            admins.append(admin[0])
        misGrupos.append((grupo.grupo, admins))
    
    return misGrupos

# FINAL MÉTODOS MIS GRUPOS
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO MÉTODOS EVENTOS

def event_loader():
    eventos = []

    misGrupos = myGroup_loader()

    for grupo in misGrupos:
        events = EventModel.query.filter(EventModel.id.like(grupo[0]+"%")).all()
        for evento in events:

            if not (evento.end.date() < datetime.now().date()):
                eventos.append(            
                    {
                        "id": evento.id,
                        "title": evento.title,
                        "start": evento.start.isoformat(),
                        "end": evento.end.isoformat(),
                        "grupo": evento.grupo,
                        "backgroundColor": evento.backgroundColor
                    }
                )

    return jsonify(eventos)

def validarFechas(start, end):
    if datetime.strptime(end, "%Y-%m-%d %H:%M") > datetime.strptime(start, "%Y-%m-%d %H:%M"):
        return True
    else:
        return False

def crearEvento():
    grupo = request.form.get('eventGroup')
    title = request.form.get('title')
    start = str(request.form.get('startDate')) + " " + str(request.form.get('startTime'))
    end = str(request.form.get('endDate')) + " " + str(request.form.get('endTime'))
    color = request.form.get('eventColor')
    
    if validarFechas(start,end):
        new_event = EventModel(title=title, start=start, end=end, grupo = grupo, backgroundColor=color)           
        db.session.add(new_event)
        db.session.commit()

def actualizarEvento():
    id = request.form.get('changeID')
    newTitle = request.form.get('changeTitle')
    newStart = str(request.form.get('changeStartDate')) + " " + str(request.form.get('changeStartTime'))
    newEnd = str(request.form.get('changeEndDate')) + " " + str(request.form.get('changeEndTime'))
    newColor = request.form.get('changeEventColor')


    if validarFechas(newStart, newEnd):
        EventModel.query.filter_by(id=id).update(
            dict(title=newTitle, start=newStart, end=newEnd, backgroundColor=newColor))
        db.session.commit()

def eliminarEvento():
    id = request.form.get('changeID')
    evento = EventModel.query.filter_by(id=id).first()
    db.session.delete(evento)
    db.session.commit()

# FINAL MÉTODOS EVENTOS
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO DE CHAT /*ACABAR SI SOBRA TIEMPO*/

@app.route("/chat", methods=['GET', 'POST'])
def chat():
    ROOMS = ["lounge", "news", "games", "coding", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a"]

    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))
    return render_template("chat.html", username=current_user.name, rooms=ROOMS)

@socketio.on('loadHistorial')
# def on_load(data):
#     mensaje1 = mensaje("user1", "Mensaje 1", datetime.now())
#     mensaje2 = mensaje("user2", "Mensaje 2", datetime.now())
#     mensaje3 = mensaje("user1", "Mensaje 3", datetime.now())
#     mensaje4 = mensaje("user2", "Mensaje 4", datetime.now())
#     mensajes = [mensaje1, mensaje2, mensaje3, mensaje4]    
#     room = data["room"]
#     for msg in mensajes:      
#         send({"username": msg.usuario, "msg": msg.mensaje, "time_stamp": str(msg.tiempo)}, room=room)

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

# FINAL DE CHAT /*ACABAR SI SOBRA TIEMPO*/
        


if __name__ == "__main__":
    socketio.run(app, debug = True)