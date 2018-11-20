(function worker() {
  $.ajax({
    url: $SCRIPT_ROOT+'/numberOfUsers', 
    success: function(response) {
      $('#resultUser').html(response);
    },
    complete: function() {
      // Schedule the next request when the current one's complete
      setTimeout(worker, 3000);
    }
  });
})();
