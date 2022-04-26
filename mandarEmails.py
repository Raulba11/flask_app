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
def obtenerEventos():
    hoy = date.today()
    endOfWeek = hoy + timedelta(days=6)
    eventos = db.session.query(EventModel).filter(EventModel.start >= hoy).filter(EventModel.end <= endOfWeek).all()
    return eventos

def contenidoTablaEventos(eventos):
    cuerpo = ""
    for evento in eventos:
        cuerpo += "<tr>"
        cuerpo += "<td>" + evento.title + "</td>"
        cuerpo += "<td>" + str(evento.start.strftime('%A %d-%m-%y %H:%M')).capitalize() + "</td>"
        cuerpo += "<td>" + str(evento.end.strftime('%A %d-%m-%y %H:%M')).capitalize() + "</td>"
        cuerpo += "</tr>"
    return cuerpo
#FIN DE MÉTODOS





try:
    eventos = obtenerEventos()
    cuerpo = contenidoTablaEventos(eventos)
    receiver = "hifika5091@viemery.com"
    body = "<table style = 'width:100%'>"
    body += "<h1>Eventos de esta semana</h1>   <tr><th>Título</th>    <th>Inicio</th>  <th>Final</th></tr>" + cuerpo + "</table>"

    yag = yagmail.SMTP("MycalTFG@gmail.com", "MyCalTFG21/22")

    yag.send(
        to=receiver,
        subject="Eventos de esta semana",
        contents=body, 
    )

    print("Email enviado a " + receiver)
except Exception as ex:
    print("Error: " + str(ex))





