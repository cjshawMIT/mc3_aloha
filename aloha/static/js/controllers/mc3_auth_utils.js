var MC3UTILS = (function(window, document, $, utils, undefined) {
    utils.bind_dialog_close_events = function () {
        $(document).on('click', '.ui-widget-overlay', function(){
            $(".ui-dialog-titlebar-close").trigger('click');
        });
    };

    utils.send_ajax = function(params, on_success, on_fail, on_always) {
        var method = 'GET';
        on_fail = typeof on_fail !== 'undefined' ? on_fail : null;
        on_always = typeof on_always !== 'undefined' ? on_always : null;

        if (params.hasOwnProperty('method')) {
            method = params['method'];
        }
        var data = {};
        if (params.hasOwnProperty('data')) {
            data = params['data'];
        }
        $.ajax({
            data: data,
            type: method,
            url: params['url']
        }).done(function (results) {
            if (on_success) {on_success(results);}
        }).fail(function(xhr, status, error) {
            if(on_fail) {on_fail();}
            vcb.update_status('Server error: ' + error);
        }).always(function(xhr, status, error) {
            if (on_always) {on_always();}
        });
    };

    utils.send_authorized_ajax = function (data) {
        function get_agent_key(_callback) {
            var key_params = {
                'url': 'get_key/'
            };

            utils.send_ajax(params, _callback, null, null);
        }

        function key_callback(key) {
            if ($.type(key) !== 'undefined') {
                var send_params = {
                    'url': ''
                };
            } else {
                utils.update_status('Error: key not generated.');
            }
        }
        // Get the agent key
        get_agent_key(key_callback);
    };

    utils.update_status = function (message) {
        $('.status_box').html(message)
                .addClass('red');
        console.log(message);
    };

    return utils;
})(this, document, jQuery, MC3UTILS || {});