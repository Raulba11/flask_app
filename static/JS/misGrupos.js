$(document).ready(function(){
    $('.nombre').click(function(){
        var nombreGrupo = this.textContent
        document.getElementById('grupoClicado').value = nombreGrupo
        $("#clicado").submit();
    })
})