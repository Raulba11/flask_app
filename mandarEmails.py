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
        cuerpo += " <tr>"
        cuerpo += " <td style = 'border: 1px solid black'>" + evento.title + "</td>"
        cuerpo += " <td style = 'border: 1px solid black'>" + str(evento.start.strftime('%A %d-%m-%y %H:%M')).capitalize() + "</td>"
        cuerpo += " <td style = 'border: 1px solid black'>" + str(evento.end.strftime('%A %d-%m-%y %H:%M')).capitalize() + "</td>"
        cuerpo += " </tr>"
    return cuerpo
#FIN DE MÉTODOS





try:
    eventos = obtenerEventos()
    cuerpo = contenidoTablaEventos(eventos)
    receiver = "boyag57673@wowcg.com"
    content = " <h1 style = 'font-size: 2.5vw'>Eventos de esta semana</h1>  <table style = 'border: 1px solid black; font-size: 2vw'> <tr><th style = 'border: 1px solid black'>Título</th>    <th style = 'border: 1px solid black'>Inicio</th>  <th style = 'border: 1px solid black'>Final</th></tr>" + cuerpo + " </table>"

    yag = yagmail.SMTP("MycalTFG@gmail.com", "MyCalTFG21/22")

    yag.send(
        to=receiver,
        subject="Eventos de esta semana",
        contents=content, 
    )

    print("Email enviado a " + receiver)
except Exception as ex:
    print("Error: " + str(ex))

