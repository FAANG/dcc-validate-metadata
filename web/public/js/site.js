$(document).ready(function(){
  $(function(){
    $('[data-toggle="popover"]').popover({
      html: true,
      content: function () {
        return $(this).next('.popover-content').html();
      }
    })
  })
});
