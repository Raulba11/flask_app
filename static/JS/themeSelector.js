document.addEventListener('DOMContentLoaded', function () {

    valorGuardado = localStorage.getItem('temaSeleccionado')

    if (valorGuardado === null){
        valorGuardado = "original"
    }

    document.getElementById('selector').value = valorGuardado
    theme.href = "static/css/temas/"+ valorGuardado +".css"
    
    $('#selector').change(function(){
        var seleccion = document.getElementById('selector').options[selector.selectedIndex].value
        localStorage.setItem('temaSeleccionado', seleccion)
        window.location.reload(true)
    })

});
