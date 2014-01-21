jQuery.curCSS = jQuery.css;
// ================
// This section primes the page on load and initializes Google Analytics, Sublime Player
$(document).ready(function(){
    "use strict";

    $("#login_tabs").tabs();

    $(".logout").on('click', function() {
        lscache.flush();
    });

    // empty the local storage on page load
    lscache.flush();

    VCB.init_search_autocomplete();
    VCB.validate_tos_and_class_codes();
});
// End of document ready functions
// ================
