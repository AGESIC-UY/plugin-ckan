(function() {
  /**
   * Ajustar altura de contenedor de Servicios (provisorio)
   */

  function ajustarAltoServicios() {
    var sectionHeight = $('.Section--tramites').height();
    $('.Servicios').css({ height: sectionHeight });
  }

  /**
   * Variable de ancho de pantalla
   */

  // var $body = $('body');
  var md = 992;
  var windowWidth = $(window).width();

  /**
   * Click event del menu local en moviles
   */

  $(window).resize(function() {
    windowWidth = $(window).width();

    if (windowWidth < md) {
      // $('.js-toggleLocalNav').click(function() {
      //   $(this).parent('.Page-nav').toggleClass('is-open');
      // });
    } else {
      ajustarAltoServicios();
    }
  });

  if (windowWidth < md) {
    // $('.js-toggleLocalNav').click(function() {
    //   $(this).parent('.Page-nav').toggleClass('is-open');
    // });
  } else {
    ajustarAltoServicios();
  }

  /* GENERAL
  ============================================================== */

  /**
   * Colapsable items tramite ampliado
   */

  $('.Tramite-title').on('click', function() {
    $(this).toggleClass('is-open');
    $(this).next('.Tramite-content').toggleClass('is-open');
  });

  $('.js-colapsarDirecciones').on('click', function(ev) {
    ev.preventDefault();
    $(this).toggleClass('Button--primary');
    $(this).next('.Tramite-direcciones').slideToggle();
  });

  /**
   * Tramite Tabs
   */

  $('.Tramite-tabs').on('click enter', '.Tramite-canal', function() {
    $('.Tramite-tabs .Tramite-canal').removeClass('is-active');
    $('.Tramite-tabs .Tramite-canal').find('.Checkbox').removeClass('Checkbox--selected');
    $(this).addClass('is-active');
    $(this).find('.Checkbox').addClass('Checkbox--selected');

    var canal = $(this).data('canal');

    var canalTitle = '';
    if (canal === 'presencial') { canalTitle = 'en persona'; };
    if (canal === 'internet') { canalTitle = 'por Internet'; };

    if (canal === 'todos') {
      $('.Tramite-info').removeClass('u-hide');
      $('.Tramite-info h4').removeClass('u-hide').removeAttr('class');
      $('.js-tramite-title-canal').text('');
    } else {
      $('.Tramite-info').addClass('u-hide');
      $('.Tramite-info h4').addClass('u-hide');
      $('.Tramite-info--' + canal).removeClass('u-hide');
      $('.js-tramite-title-canal').text(' ' + canalTitle);
    }
  }).on('keypress', function(e) {
    if (e.which === 13) {
      $(this).trigger('enter');
    }
  });
})();

/**
 * Inicializar Menu Accesible
 */

if (jQuery().accessibleMenuHome) {
  if ($('.Nav-inner')) {
    $('.Nav-inner').accessibleMenuHome();
  }
}

/**
 * Check if input for resource format is empty (templates/package/snippets/resource_form.html)
 */

function check_resource_fields_are_empty() {
  const fields = ["field-name", "field-description", "field-format"]
  let fields_not_empty = 0
  for (const field of fields) {
      const field_obj=document.getElementById(field);
      if (field_obj) {
        if (field_obj.value) {
          // Count required and not empty
          fields_not_empty++
        }
      } else {
        // Count if field not exist
        fields_not_empty++
      }
  }
  // If all field are not empty is ok
  if (fields_not_empty == fields.length)
    return true
  alert("Por favor complete todos los campos obligatorios");
  return false;
}

// (function() {
//   if (is_test_enviroment()) {
//     show_element("button_publicador_da_2")
//   }
// })();
//
// function is_test_enviroment() {
//   if (window.location.host == 'test.catalogodatos.gub.uy') {
//     return true
//   }
//   return false
// }

function show_element(elementId) {
  const el = document.getElementById(elementId)
  if (el) {
    el.style.visibility = 'visible'
  }
}

// Buscar todos los elementos de la página que contengan números
const elementsNumber = document.querySelectorAll('p, span, div');
// Iterar sobre cada elemento y formatear el número si es necesario
    elementsNumber.forEach((element) => {
    const text = element.textContent;
      if (/^\d+(\.\d+)?$/.test(text)) { // Verificar si el texto es un número
      const number = parseFloat(text.replace(',', '.'));
      const options = { style: 'decimal', currency: 'UYU' };
      const formattedNumber = number.toLocaleString('es-UY', options);
      element.textContent = formattedNumber.replace('.', '.');
  }
});
