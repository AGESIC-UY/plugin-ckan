$(function () {
    $("li.resource-item").each(function (index, li) {
        let url = '/agesic/portal/js/resource_health_and_status/' + $(li).attr('data-id')
        $.getJSON(url)
            .done(function(data) {
                // Handle successful response
                let broken = data[0] != 'ok';
                if (broken) {
                    if ($('.archiver', li).length) {
                        $('.Status-archiver', li).toggle();
                        $('.archiver-outer', li).toggle();
                    } else {
                        $('.Button-main', li).toggle();
                        $('.Status-main', li).addClass('Status--enlaceRoto').html('Enlace roto').toggle();
                    }
                } else {
                    $('.Button', li).addClass('Button--primary');
                    let status = data[1];
                    switch (status) {
                        case 'Activo':
                            $('.Status-main', li).addClass('Status--activo');
                            break;
                        case 'Desactualizado':
                            $('.Status-main', li).addClass('Status--desactualizado');
                            break;
                        default:
                            $('.Status-main', li).addClass('Status--discontinuado');
                    }
                    $('.Status-main', li).html(status).toggle();
                    $('.Button-main', li).toggle();
                }
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                // Handle other errors
                console.log("Error: " + textStatus + " - " + errorThrown);
                $('.Button-main', li).toggle();
                $('.Status-main', li).addClass('Status--enlaceRoto').html('Enlace roto').toggle();
            });
    });
});
