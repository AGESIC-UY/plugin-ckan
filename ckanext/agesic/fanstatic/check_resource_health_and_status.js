$(function(){
  let all_status_container = $('.Status')
  all_status_container.each(function() {
    let status_container = $(this);
    $.getJSON('/agesic/portal/js/resource_health_and_status/' + status_container.attr('id'), function (r) {
      var broken = r[0] != 'ok';
      var status = r[1];
      if (broken) {
        status = 'Enlace roto';
        status_container.addClass('Status--enlaceRoto');
      } else {
        $('.archiver.link-cached').toggle();
        switch (status) {
          case 'Activo':
            status_container.addClass('Status--activo');
            break;
          case 'Desactualizado':
            status_container.addClass('Status--desactualizado');
            break;
          default:
            status_container.addClass('Status--discontinuado');
        }
      }
      status_container.html(status);
    });
  });
});
