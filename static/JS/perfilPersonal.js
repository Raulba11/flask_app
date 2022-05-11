
document.addEventListener('DOMContentLoaded', function () {
  var calendarEl = document.getElementById('calendar');
  var calendar = new FullCalendar.Calendar(calendarEl, {
    /*---INICIO DE REGION DE CONFIGURACION---*/
    displayEventTime: true,
    displayEventEnd: true,
    dayMaxEventRows: true,
    initialView: 'dayGridMonth',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth',
    },
    dayHeaderFormat: {
      weekday: 'long'
    }
    /*---FIN DE REGION DE CONFIGURACION---*/
  }
  );
  //Cargar idioma, datos al final
  calendar.setOption('locale', 'es');
  //Cargar los eventos, guardados en esa URL
  calendar.addEventSource("/eventos");
  calendar.render()
});

FullCalendar.globalLocales.push(function () {
  'use strict';
  var es = {
    code: 'es',
    week: {
      dow: 1, // Monday is the first day of the week.
      doy: 4, // The week that contains Jan 4th is the first week of the year.
    },
    buttonText: {
      prev: 'Ant',
      next: 'Sig',
      today: 'Hoy',
      month: 'Mes',
      week: 'Semana',
      day: 'Día',
      list: 'Agenda',
    },
    buttonHints: {
      prev: '$0 antes',
      next: '$0 siguiente',
      today(buttonText) {
        return (buttonText === 'Día') ? 'Hoy' :
          ((buttonText === 'Semana') ? 'Esta' : 'Este') + ' ' + buttonText.toLocaleLowerCase()
      },
    },
    viewHint(buttonText) {
      return 'Vista ' + (buttonText === 'Semana' ? 'de la' : 'del') + ' ' + buttonText.toLocaleLowerCase()
    },
    weekText: 'Sm',
    weekTextLong: 'Semana',
    allDayText: 'Todo el día',
    moreLinkText: 'más',
    moreLinkHint(eventCnt) {
      return `Mostrar ${eventCnt} eventos más`
    },
    noEventsText: 'No hay eventos para mostrar',
    navLinkHint: 'Ir al $0',
    closeHint: 'Cerrar',
    timeHint: 'La hora',
    eventHint: 'Evento',
  };

  return es;

}());


$(document).ready(function () {
  $('#grupoEventos').on('change', function () {
    document.forms['formGrupoEventos'].submit()
  });

  if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
  }

});