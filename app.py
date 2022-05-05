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
# Eliminar junto a la librería si no se hace el chat
socketio = SocketIO(app, manage_session=False)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Necesitas iniciar sesión para ver esta página"

db.init_app(app)


def create_app():
    """
    Necesario para pasar el contexto al script encargado de los emails.
    """
    app = Flask(__name__)
    setup(app)
    db.init_app(app)
    return app


@login_manager.user_loader
def load_user(user_id):
    """
    Iniciar sesión automáticamente.
    """
    user = UserModel.query.filter_by(id=user_id).first()
    if user:
        return user
    return None


@app.route('/eventos')
@login_required
def eventos():
    """
    Carga la URL con el JSON de eventos que será usado para cargar estos en el calendario *NO HECHO PARA SER VISIBLE*.
    """
    return event_loader()

# FINAL DE CONFIGURACION
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO DE RUTAS VISIBLES


@app.route('/')
def index():
    """
    Página índice para la prueba de métodos *TEMPORAL*.
    """
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    """
    Página de login, si se intenta acceder ya estándolo redirige al index.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Inicia con el método GET
    email = request.form.get('email')
    password = request.form.get('password')
    user = UserModel.query.filter_by(email=email).first()

    # Al rellenar el formulario y presionar el botón pasa por la verficación
    if request.method == 'POST':
        
        if not user:
            flash("Usuario no encontrado")
        elif not check_password_hash(user.password, password):
            flash("Contraseña incorrecta")
        else:
            login_user(user, remember=request.form.get('remember'))
            return redirect(url_for('index'))
        return render_template('login.html')
    # Carga de HTML del método GET
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Página de signup.
    """
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
            return render_template('signup.html', created = True)

        return render_template('signup.html', created=False)
    # Carga de HTML del método GET
    return render_template('signup.html', created=False)


@app.route('/logout')
@login_required
def logout():
    """
    URL que cierra la sesión del usuario.
    """
    logout_user()
    return redirect(url_for('principal'))


@app.route('/calendario', methods=['GET', 'POST'])
@login_required
def calendario():
    """
    URL que carga el calendario.
    """

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

        return render_template('calendario.html', grupos=gruposAdmin, gruposPertenece=gruposPertenece, admin=admin)

    return render_template('calendario.html', grupos=gruposAdmin, gruposPertenece=gruposPertenece, admin=True)


@app.route('/grupos', methods=['GET', 'POST'])
@login_required
def grupos():
    """
    URL que carga todos los grupos.
    """

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

        return render_template('grupos.html', len=len(grupos), lista=grupos, alertar=alertar)

    return render_template('grupos.html', len=len(grupos), lista=grupos, alertar=False)


@app.route('/misGrupos', methods=['GET', 'POST'])
@login_required
def misGrupos():
    """
    URL que carga los grupos de cada usuario.
    """

    grupos = myGroup_loader()
    ownerDe = tusGrupos()

    if request.method == 'POST':
        alertar = True
        action = request.form.get('action')

        if action == "search":
            resultado = buscador(request.form.get('search'))

            if len(resultado) == 0:
                flash("No se ha encontrado ningún grupo")
            else:
                alertar = False
                grupos = resultado
        
        elif action == "grupoClicado":
            clicado = request.form.get('grupoClicado')
            return redirect(url_for('misGruposGrupo', grupo=clicado))

        elif action == "eliminar":
            grupo, pwd, conf = request.form.get('removedGroup'), request.form.get('passRemovedGroup'), request.form.get('confRemovedGroup')
            flash(eliminarGrupo(grupo, pwd, conf))
        
        elif action == "actualizar":
            grupo, pwd, confPass = request.form.get('updateGroup'), request.form.get('passRemovedGroup'), request.form.get('confPassRemovedGroup')
            flash(actualizarGrupo(grupo, pwd, confPass))

        return render_template('misGrupos.html', len=len(grupos), lista=grupos, tusGrupos=ownerDe, alertar = alertar)

    return render_template('misGrupos.html', len=len(grupos), lista=grupos, tusGrupos=ownerDe, alertar = False)


@app.route('/misGrupos/<grupo>')
@login_required
def misGruposGrupo(grupo: str):
    """
    Retorna la página de un grupo concreto o el índice si se escribe a mano la URL y no se es usuario del grupo.
    """
    pertenece = GrupoUserRelation.query.filter_by(
        grupo=grupo).filter_by(user=current_user.name).first()

    if pertenece:
        owner = GroupModel.query.with_entities(
            GroupModel.owner).filter_by(name=grupo).first()
        miembros = listaMiembros(grupo)

        return render_template('grupoDentro.html', grupo=grupo, miembros=miembros, owner=owner[0])
    else:
        return redirect(url_for('index'))

@app.route('/<usuario>', methods=['GET', 'POST'])
@login_required
def perfilPersonal(usuario: str, methods = ['GET', 'POST']):
    """
    URL que carga el perfil personal del usuario actual
    """
    grupos = tusGrupos()
    
    todosEventos = misEventosTodos()
    eventosGrupo = eventosGrupoConcreto(grupos[0].name)
    if request.method == "POST":
        pass


    return render_template('perfilPersonal.html', todosEventos = todosEventos, len = len(todosEventos), eventosGrupo = eventosGrupo, lenConcreto = len(eventosGrupo))

@app.route('/principal')
def principal():
    """
    URL que contiene la página principal de la web. SUSTITUIR POR INDEX EN EL MONTAJE.
    """
    return render_template('principal.html')

# FINAL DE RUTAS VISIBLES
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO MÉTODOS GRUPOS


def group_loader() -> list:
    """
    Obtiene todos los grupos y los administradores de estos.
    """

    allGroups = []
    grupos = GroupModel.query.order_by(GroupModel.name).all()

    for grupo in grupos:
        admins = []
        for admin in GrupoUserRelation.query.filter_by(grupo=grupo.name).filter_by(admin='Y').with_entities(GrupoUserRelation.user).all():
            admins.append(admin[0])
        allGroups.append((grupo.name, admins))

    return allGroups


def buscador(search: str) -> list:
    """
    Retorna los grupos que contengan el texto pasado en el buscador.
    """
    resultado = []
    grupos = db.session.query(GroupModel).filter(
        GroupModel.name.like("%" + search.upper() + "%")).all()
    for grupo in grupos:
        admins = []
        for admin in GrupoUserRelation.query.filter_by(grupo=grupo.name).filter_by(admin='Y').with_entities(GrupoUserRelation.user).all():
            admins.append(admin[0])
        resultado.append((grupo.name, admins))

    return resultado


def crearGrupo(name: str, password: str, confPassword: str) -> str:
    """
    Valida los parámetros y si está todo correcto crea un grupo. Retorna un mensaje.
    """

    grupo = GroupModel.query.filter_by(name=name.upper()).all()
    if grupo:
        return "Grupo ya existente"
    elif password != confPassword:
        return "Las contraseñas no coinciden"
    else:
        new_group = GroupModel(
            name=name.upper(), password=password, owner=current_user.name)
        new_relation = GrupoUserRelation(
            grupo=name.upper(), user=current_user.name, admin="Y")
        db.session.add(new_group)
        db.session.add(new_relation)
        db.session.commit()
        return "Grupo creado exitosamente"


def comprobarPass(name: str, password: str) -> bool:
    """
    Comprueba si la contraseña pasada es la del grupo.
    """

    grupo = GroupModel.query.filter_by(name=name).first()
    return password == grupo.password


def enterGroup(groupName: str) -> bool:
    """
    Comprueba si el usuario está en el grupo y si no lo está lo añade.
    """

    miembrosTEMP = GrupoUserRelation.query.with_entities(
        GrupoUserRelation.user).filter_by(grupo=groupName).all()
    miembros = []
    for miembro in miembrosTEMP:
        miembros.append(miembro[0])

    if current_user.name in miembros:
        return True
    else:
        nuevo_miembro = GrupoUserRelation(
            grupo=groupName, user=current_user.name, admin="N")
        db.session.add(nuevo_miembro)
        db.session.commit()


def esAdmin(grupo: str) -> bool:
    """
    Comprueba si el usuario es administrador del grupo pasado.
    """

    admin = GrupoUserRelation.query.with_entities(GrupoUserRelation.admin).filter_by(
        grupo=grupo).filter_by(user=current_user.name).first()
    if admin[0] == 'Y':
        return True
    else:
        return False


# FINAL MÉTODOS GRUPOS
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO MÉTODOS MIS GRUPOS


def myGroup_loader() -> list:
    """
    Obtiene los grupos a los que pertenece el usuario y los administradores de estos.
    """

    misGrupos = []
    grupos = GrupoUserRelation.query.filter_by(
        user=current_user.name).order_by(GrupoUserRelation.grupo).all()
    for grupo in grupos:
        admins = []
        for admin in GrupoUserRelation.query.filter_by(grupo=grupo.grupo).filter_by(admin='Y').with_entities(GrupoUserRelation.user).all():
            admins.append(admin[0])
        
        owner = GroupModel.query.filter_by(name=grupo.grupo).first().owner

        if owner == current_user.name:
            misGrupos.append((grupo.grupo, admins, True))
        else:
            misGrupos.append((grupo.grupo, admins, False))

    return misGrupos


def tusGrupos() -> list:
    """
    Retorna una lista con los grupos de los que el current_user es owner.
    """
    tusGrupos = GroupModel.query.filter_by(owner=current_user.name).all()
    return tusGrupos


def listaMiembros(grupo: str) -> list:
    """
    Retorna una lista con todos los miembros de un grupo concreto.
    """
    usuarios = GrupoUserRelation.query.with_entities(GrupoUserRelation.user, GrupoUserRelation.admin).filter_by(
        grupo=grupo).order_by(GrupoUserRelation.admin.desc()).all()
    return usuarios


def actualizarGrupo(grupo: str, pwd: str, confPass: str) -> str:
    """
    Comprueba que las dos contraseñas coinciden y si es así actualiza esta. Retorna el mensaje que será usado en la alerta.
    """

    if pwd != confPass:
        return "No coinciden las contraseñas"
    else:        
        GroupModel.query.filter_by(name=grupo).update(dict(password=pwd))
        db.session.commit()
        return "Grupo actualizado correctamente"


def eliminarGrupo(grupo: str, pwd: str, conf: str) -> str:
    grupoObj = GroupModel.query.filter_by(name = grupo).first()
    if grupo != conf:
        return "Confirmación incorrecta"
    elif pwd != grupoObj.password:
        return "La contraseña introducida es incorrecta"
    else:
        relacion = GrupoUserRelation.query.filter_by(grupo = grupo).all()
        for r in relacion:
            db.session.delete(r)
        eventos = EventModel.query.filter_by(grupo = grupo).all()
        for evento in eventos:
            db.session.delete(evento)
        db.session.delete(grupoObj)

        db.session.commit()
        return "Grupo eliminado correctamente"


# FINAL MÉTODOS MIS GRUPOS
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO MÉTODOS EVENTOS


def event_loader():
    """
    Retorna en formato JSON todos los eventos de los grupos a los que pertenece el usuario.
    """

    eventos = []
    misGrupos = myGroup_loader()

    for grupo in misGrupos:
        events = EventModel.query.filter(
            EventModel.id.like(grupo[0]+"%")).all()
        for evento in events:

            if ((evento.end.date() > datetime.now().date()) and (evento.end.time() > datetime.now().time())):
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


def validarFechas(start, end) -> bool:
    """
    Valida que la fecha final del evento sea posterior a la inicial.
    """

    if datetime.strptime(end, "%Y-%m-%d %H:%M") > datetime.strptime(start, "%Y-%m-%d %H:%M"):
        return True
    else:
        return False


def crearEvento():
    """
    Crea un evento si está correcto.
    """

    grupo = request.form.get('eventGroup')
    title = request.form.get('title')
    start = str(request.form.get('startDate')) + " " + \
        str(request.form.get('startTime'))
    end = str(request.form.get('endDate')) + " " + \
        str(request.form.get('endTime'))
    color = request.form.get('eventColor')

    if validarFechas(start, end):
        new_event = EventModel(title=title, start=start,end=end, grupo=grupo, backgroundColor=color)
        db.session.add(new_event)
        db.session.commit()


def actualizarEvento():
    """
    Actualiza un evento si está correcto.
    """
    id = request.form.get('changeID')
    newTitle = request.form.get('changeTitle')
    newStart = str(request.form.get('changeStartDate')) + \
        " " + str(request.form.get('changeStartTime'))
    newEnd = str(request.form.get('changeEndDate')) + " " + \
        str(request.form.get('changeEndTime'))
    newColor = request.form.get('changeEventColor')

    if validarFechas(newStart, newEnd):
        EventModel.query.filter_by(id=id).update(
            dict(title=newTitle, start=newStart, end=newEnd, backgroundColor=newColor))
        db.session.commit()


def eliminarEvento():
    """
    Elimina un evento.
    """

    id = request.form.get('changeID')
    evento = EventModel.query.filter_by(id=id).first()
    db.session.delete(evento)
    db.session.commit()

# FINAL MÉTODOS EVENTOS
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO MÉTODOS PERFIL PERSONAL


def misEventosTodos() -> list:
    """
    Retorna una lista con todos los eventos de los grupos a los que pertenece el usuario.
    """

    eventos = []
    misGrupos = myGroup_loader()

    for grupo in misGrupos:
        events = EventModel.query.filter(
            EventModel.id.like(grupo[0]+"%")).all()

        for evento in events:
            if ((evento.end.date() > datetime.now().date()) and (evento.end.time() > datetime.now().time())):
                eventos.append(evento)

    return eventos

def eventosGrupoConcreto(grupo):
    eventos = []
    events = EventModel.query.filter_by(grupo = grupo).all()

    for evento in events:        
        if ((evento.end > datetime.now()) and (evento.end > datetime.now())):
            eventos.append(evento)

    return eventos    

# FINAL MÉTODOS PERFIL PERSONAL
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# INICIO DE CHAT /*ACABAR SI SOBRA TIEMPO*/


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    """
    *PROBABLEMENTE ELIMINAR*
    """
    ROOMS = ["lounge", "news", "games", "coding", "a", "a", "a", "a", "a", "a", "a", "a", "a",
             "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a", "a"]

    if not current_user.is_authenticated:
        flash('Please login', 'danger')
        return redirect(url_for('login'))
    return render_template("chat.html", username=current_user.name, rooms=ROOMS)


@socketio.on('loadHistorial')
def on_load(data):
    # mensaje1 = mensaje("user1", "Mensaje 1", datetime.now())
    # mensaje2 = mensaje("user2", "Mensaje 2", datetime.now())
    # mensaje3 = mensaje("user1", "Mensaje 3", datetime.now())
    # mensaje4 = mensaje("user2", "Mensaje 4", datetime.now())
    # mensajes = [mensaje1, mensaje2, mensaje3, mensaje4]
    # room = data["room"]
    # for msg in mensajes:
    #     send({"username": msg.usuario, "msg": msg.mensaje, "time_stamp": str(msg.tiempo)}, room=room)
    pass


@socketio.on('incoming-msg')
def on_message(data):
    """Broadcast messages"""
    msg = data["msg"]
    username = data["username"]
    room = data["room"]
    # Set timestamp
    time_stamp = datetime.strftime(datetime.now(), '%b-%d %I:%M%p')
    send({"username": username, "msg": msg, "time_stamp": time_stamp}, room=room)


@socketio.on('join')
def on_join(data):
    """User joins a room"""

    username = data["username"]
    room = data["room"]
    join_room(room)

    # Broadcast that new user has joined
    send({"msg": username.capitalize() + " ha entrado en la sala " + room}, room=room)


@socketio.on('leave')
def on_leave(data):
    """User leaves a room"""

    username = data['username']
    room = data['room']
    leave_room(room)
    send({"msg": username.capitalize() + " ha abandonado la sala"}, room=room)


# FINAL DE CHAT /*ACABAR SI SOBRA TIEMPO*/


if __name__ == "__main__":
    socketio.run(app, debug=True)
