$('.button-collapse').sideNav();
$('select:not(.browser-default):not([multiple])').material_select();
$('select[multiple]').addClass('browser-default').select2();
$('.modal-trigger').leanModal();
$('ul.tabs').find('.tab').on('click', function(e) {
  window.history.pushState(null, null, e.target.hash);
});
var el = document.getElementById('product-gallery');
if (el) {
  var sortable = Sortable.create(el, {
    onUpdate: function () {
      $.ajax({
        dataType: 'json',
        contentType: "application/json",
        data: JSON.stringify({
          'order': (function () {
            var postData = [];
            $(el).find('.product-gallery-item').each(function (i) {
              postData.push($(this).data('id'));
            });
            return postData;
          })()
        }),
        headers: {
          'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        method: 'post',
        url: $(el).data('post-url')
      });
    }
  });
}
$('#select-all').on('change', function() {
  if (this.checked) {
    $('.switch-actions').prop('checked', true);
  } else {
    $('.switch-actions').prop('checked', false);
  }
});
$('.switch-actions').on('change', function() {
  var $btnChecked = $('.btn-show-when-checked');
  var $btnUnchecked = $('.btn-show-when-unchecked');
  if($('.switch-actions:checked').length) {
    $btnChecked.show();
    $btnUnchecked.hide();
  } else {
    $btnUnchecked.show();
    $btnChecked.hide();
  }
});
