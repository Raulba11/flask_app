
document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    var calendar = new FullCalendar.Calendar(calendarEl, {
        /*---INICIO DE REGION DE CONFIGURACION---*/
        displayEventTime: true,
        editable: true,
        displayEventEnd: true,
        dayMaxEventRows: true,
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        dayHeaderFormat: {
            weekday: 'long'
        },
        /*---FIN DE REGION DE CONFIGURACION---*/


        /*---INICIO DE REGION DE METODOS---*/
        //Añadir evento al clickar una fecha
        dateClick: function (info) {
            if (info.date < new Date().setHours(0, 0, 0, 0)) {
                Swal.fire({
                    title: '¡Error!',
                    text: 'La fecha seleccionada ya pasó',
                    icon: 'error'
                })
            } else {
                clickedDate = new Date((info.date))
                clickedDate.setDate(clickedDate.getDate() + 1)
                diaInicio = clickedDate.toISOString().split('T')[0]
                document.getElementById("startDate").value = diaInicio

                $('#addModal').on('shown.bs.modal', function () {
                    document.getElementById("endDate").setAttribute("min", diaInicio)
                });


                $('#addModal').modal('show');


            }
        },

        //Actualizar o eliminar un evento al clickarlo
        eventClick: function (info) {
            update(info)
        },

        //Mostrar el menú para eliminar o actualizar, cambiando las fechas a las nuevas
        eventDrop: function (info) {
            evento = calendar.getEventById(info.event.id);
            if (evento.start < new Date().setHours(0, 0, 0, 0)) {
                Swal.fire({
                    title: '¡Error!',
                    text: 'La fecha de inicio es menor a la actual',
                    icon: 'error'
                })
                info.revert()
            } else {
                update(info)
            }

        },

        //Mostrar el menú para eliminar o actualizar, cambiando la hora de fin a la nueva (ver como implementar que funcione para fechas en dayGridMonth)
        eventResize: function (info) {
            update(info)
        }


    }
    );
    //Cargar idioma, datos al final
    calendar.setOption('locale', 'es');
    //Cargar los eventos, guardados en esa URL
    calendar.addEventSource("/eventos");

    //Actualizar los datos de un evento
    function update(info) {
        //Obtener datos del evento
        evento = calendar.getEventById(info.event.id);
        horaInicio = new Date(((evento.start.getTime()) - (evento.start.getTimezoneOffset() * 60000))).toISOString().substring(11, 16)
        horaFinal = new Date(((evento.end.getTime()) - (evento.end.getTimezoneOffset() * 60000))).toISOString().substring(11, 16)
        inicio = evento.start.toISOString().split('T')[0]
        final = evento.end.toISOString().split('T')[0]
        color = evento.backgroundColor
        grupo = evento.id.substring(0, (evento.id.length - 37))
        
        //Precargar el modal con los datos obtenidos
        $('#changeModal').on('show.bs.modal', function () {
            document.getElementById("changeEndDate").setAttribute("min", inicio)
            $("#changeTitle").val(evento.title);
            $("#changeID").val(evento.id);
            document.getElementById("changeStartTime").value = horaInicio
            document.getElementById("changeEndTime").value = horaFinal
            document.getElementById("changeStartDate").value = inicio
            document.getElementById("changeEndDate").value = final
            document.getElementById("changeEventColor").value = color
            document.getElementById("changeEventGroup").value = grupo
        });
        //Si el modal se cierra con el botón close, revertir los cambios
        $('#changeModal').on('hidden.bs.modal', function () {
            document.getElementById("btnClose").onclick = info.revert()
        });
        //Mostrar el modal
        $('#changeModal').modal('show');
    }
    //Cargar el calendario después de que ya se cargó toda la página para evitar un mal renderizado inicial
        $(window).on('load', function () {
            calendar.render();
        });
    /*---FIN DE REGION DE METODOS---*/

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