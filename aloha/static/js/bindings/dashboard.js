$(document).ready(function() {
    $(document).on('click', '.nav-help', function() {
        $('#help_modal').dialog({
            closeOnEscape: true,
            closeText: 'close',
            modal: true,
            width: 400
        });
        MC3UTILS.bind_dialog_close_events();
    });
});