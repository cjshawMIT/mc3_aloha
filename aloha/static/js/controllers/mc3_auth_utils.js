var MC3UTILS = (function(window, document, $, utils, undefined) {
    utils.bind_dialog_close_events = function () {
        $(document).on('click', '.ui-widget-overlay', function(){
            $(".ui-dialog-titlebar-close").trigger('click');
        });
    };

    return utils;
})(this, document, jQuery, MC3UTILS || {});