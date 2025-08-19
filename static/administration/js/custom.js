/* Add here all your JS customizations */
$(function () {
    $('#btn_logout').on('click', function (e) {
      e.preventDefault();                 // evita la navegación del <a>
      // $(this).next('form').trigger('submit'); // envía el form hermano
      $('#logout-form').trigger('submit');
    });
  });