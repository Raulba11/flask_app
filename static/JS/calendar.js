document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {        
        


        displayEventTime: true,
        editable: true,
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay,listMonth'
        },
        
        
        dateClick: function (info) {
            if (info.date < new Date()) {
                alert("La fecha ya pasó")
            } else {
                clickedDate = new Date((info.date))
                clickedDate.setDate(clickedDate.getDate() + 1)
                diaInicio = clickedDate.toISOString().split('T')[0]
                document.getElementById("startDate").value = diaInicio

                $('#addModal').on('shown.bs.modal',function(){
                    document.getElementById("endDate").setAttribute("min", diaInicio)
                });

                
                $('#addModal').modal('show');
                                
                
            }
        },

        eventClick: function (info){
            evento = calendar.getEventById(info.event.id);

            horaInicio = evento.start.toISOString().substring(11,16)
            horaFinal = evento.end.toISOString().substring(11,16)
            inicio = evento.start.toISOString().split('T')[0]
            final = evento.end.toISOString().split('T')[0]
            color = evento.backgroundColor


            $('#changeModal').on('show.bs.modal',function(){

                document.getElementById("changeEndDate").setAttribute("min", inicio)
                $("#changeTitle").val(evento.title);
                $("#changeID").val(evento.id);
                document.getElementById("changeStartTime").value = horaInicio
                document.getElementById("changeEndTime").value = horaFinal
                document.getElementById("changeStartDate").value = inicio
                document.getElementById("changeEndDate").value = final
                document.getElementById("changeEventColor").value = color
            });

            $('#changeModal').modal('show');

        }
    }
    );
    calendar.setOption('locale', 'ISO');
    calendar.addEventSource("/eventos");
    calendar.render();
});
