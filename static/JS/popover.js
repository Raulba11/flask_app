$(function () {
    //Al clicar al botón de gestionar grupos abrir un modal con las opciones
    $('#btnConfigurarGrupos').click(function(){
        $('#configGruposModal').modal('show')
    })

    //Al clicar al botón de eliminar grupos abrir el modal para eliminar
    $('#btnOpcionEliminar').click(function(){
        $('#configGruposModal').modal('hide')
        $('#removeGroupModal').modal('show')
    })
     //Al clicar al botón de hacer admin abrir el modal para hacer admin
     $('#btnOpcionHacerAdminr').click(function(){
        $('#configGruposModal').modal('hide')
        $('#adminGroupModal').modal('show')
    })
      //Al clicar al botón de deshacer admin abrir el modal para deshacer
    $('#btnOpcionDeshacerAdminr').click(function(){
        $('#configGruposModal').modal('hide')
        $('#desadminGroupModal').modal('show')
    })

    
  
    $('[data-bs-toggle="popover"]').popover({
        title: 'Acciones',
        container: 'body',
        placement: 'right',
        html: true, 
        content: function() {
              return $('#removeUser');
        }
    });
    


  })

  