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
        /*---FIN DE REGION DE CONFIGURACION---*/


        /*---INICIO DE REGION DE METODOS---*/
        //Añadir evento al clickar una fecha
        dateClick: function (info) {
            if (info.date < new Date().setHours(0, 0, 0, 0)) {
                alert("La fecha ya pasó")
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
                alert("La fecha de inicio es anterior que la de hoy")
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
    calendar.setOption('locale', 'ISO');
    calendar.addEventSource("/eventos");
    calendar.render();

    //Actualizar los datos de un evento
    function update(info) {
        //Obtener datos del evento
        evento = calendar.getEventById(info.event.id);
        horaInicio = new Date(((evento.start.getTime()) - (evento.start.getTimezoneOffset() * 60000))).toISOString().substring(11, 16)
        horaFinal = new Date(((evento.end.getTime()) - (evento.end.getTimezoneOffset() * 60000))).toISOString().substring(11, 16)
        inicio = evento.start.toISOString().split('T')[0]
        final = evento.end.toISOString().split('T')[0]
        color = evento.backgroundColor
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
        });
        //Si el modal se cierra con el botón close, revertir los cambios
        $('#changeModal').on('hidden.bs.modal', function () {
            document.getElementById("btnClose").onclick = info.revert()
        });
        //Mostrar el modal
        $('#changeModal').modal('show');

    }
    /*---FIN DE REGION DE METODOS---*/

});

