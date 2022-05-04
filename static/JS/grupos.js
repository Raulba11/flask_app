$(document).ready(function(){

    //Al clicar al botón de crear grupo
    $('#btnCrearGrupo').click(function(){
        $('#createModal').modal('show')
    })

    //Al clicar sobre el nombre de un grupo
    $('.nombre').click(function(){
        var nombreGrupo = this.textContent

        $('#enterModal').on('shown.bs.modal', function () {
            document.getElementById("enterName").value = nombreGrupo
        });

        $('#enterModal').modal('show');
    });
})