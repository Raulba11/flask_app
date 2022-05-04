import yagmail, locale
from app import create_app
from models import *
from config import *
from datetime import date, timedelta

#SETUP
locale.setlocale(locale.LC_ALL, 'es-ES')
app = create_app()
app.app_context().push()
setup(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#FIN SETUP

#MÉTODOS

def contenidoTablaEventos(eventos : EventModel, contador : int) -> tuple:
    """
    Retorna la parte de HTML correspondiente a fila con los datos de un evento.
    Además devuelve el contador actualizado para poder mostrar el diseño de forma par e impar.
    Acceder al contenido como una lista: [0] es el HTML [1] es el contador.
    """
    cuerpo = ""
    contador = contador
    for evento in eventos:
        if contador % 2 != 0:            
            cuerpo += "<tr class = 'impar'>"
        else:
            cuerpo += "<tr>"
        cuerpo += " <td>" + evento.grupo + "</td>"
        cuerpo += " <td>" + evento.title + "</td>"
        cuerpo += " <td>" + str(evento.start.strftime('%A %d-%m-%y %H:%M')).capitalize() + "</td>"
        cuerpo += " <td>" + str(evento.end.strftime('%A %d-%m-%y %H:%M')).capitalize() + "</td>"
        cuerpo += " </tr>"
        contador += 1
    return cuerpo, contador

def mandarEmail(cuerpo : str, receptor : UserModel.email) -> None:
    """
    Construye el email y lo manda.
    """
    try:    
        receiver = receptor
        content = "<style>"\
        +".container{display: flex; justify-content: center; align-items: center; margin: auto;}"\
        +"table{width: 100%; border: 1px solid #EEEEEE; border-collapse: collapse}"\
        +"th{color: white; background: #000; padding: 5px; font-size: 25px}"\
        +".impar{background: #EEEEEE;}"\
        +"td{font-size:20px; text-align:center;}"\
        +"</style>"\
        +"<h1>Eventos de esta semana</h1> " \
        +"<div class = 'container'>"\
        + "<table><tr>" \
           + "<th>GRUPO</th>" \
           + "<th>TITULO</th>" \
           + "<th>INICIO</th>" \
           + "<th>FINAL</th>" \
         + "</tr>" + cuerpo + "</table></div>"

        yag = yagmail.SMTP("MycalTFG@gmail.com", "MyCalTFG21/22")

        yag.send(
            to=receiver,
            subject="Eventos de esta semana",
            contents=content, 
        )

        print("Email enviado a " + receiver)
    except Exception as ex:
        print("Error: " + str(ex))

#FIN DE MÉTODOS

hoy = date.today()
endOfWeek = hoy + timedelta(days=6)

#Obtener todos los usuarios
usuarios = UserModel.query.all()

#Por cada usuario obtener sus grupos
for usuario in usuarios:
    cuerpo = ""
    grupos = GrupoUserRelation.query.with_entities(GrupoUserRelation.grupo).filter_by(user = usuario.name).order_by(GrupoUserRelation.grupo)
    contador = 1
#Por cada grupo sus eventos
    for grupo in grupos:
        eventos = EventModel.query.filter(EventModel.grupo == grupo[0]). filter(EventModel.start >= hoy).filter(EventModel.start <= endOfWeek).all()
        cuerpo += contenidoTablaEventos(eventos, contador)[0]
        contador = contenidoTablaEventos(eventos, contador)[1]
#Por cada usuario mandarle su email
    mandarEmail(cuerpo, usuario.email)







