document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('selector').value = localStorage.getItem('temaSeleccionado')
    theme.href = "static/css/temas/"+ localStorage.getItem('temaSeleccionado') +".css"
    
    $('#selector').change(function(){
        var tema = document.getElementById('theme')
        var seleccion = document.getElementById('selector').options[selector.selectedIndex].value
        localStorage.setItem('temaSeleccionado', seleccion)
        window.location.reload(true)
    })

});