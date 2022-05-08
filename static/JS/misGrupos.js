$(document).ready(function(){
    //Al clicar sobre el nombre de un grupo mandar este al servidor
    $('.nombre').click(function(){
        var nombreGrupo = this.textContent
        document.getElementById('grupoClicado').value = nombreGrupo
        $("#clicado").submit();
    })

    //Al clicar al botón de gestionar grupos abrir un modal con las opciones
    $('#btnConfigurarGrupos').click(function(){
        $('#configGruposModal').modal('show')
    })

    //Al clicar al botón de eliminar grupos abrir el modal para eliminar
    $('#btnOpcionEliminar').click(function(){
        $('#configGruposModal').modal('hide')
        $('#removeGroupModal').modal('show')
    })

    //Al clicar al botón de actualizar grupos abrir el modal para actualizar
    $('#btnOpcionActualizar').click(function(){
        $('#configGruposModal').modal('hide')
        $('#updateGroupModal').modal('show')
    })


})