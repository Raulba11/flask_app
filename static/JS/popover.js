$(function () {
    
  
    $('[data-bs-toggle="popover"]').popover({
        title: 'Acciones',
        container: 'body',
        placement: 'right',
        html: true, 
        content: function() {
              return $('#btn');
        }
    });
    


  })

  