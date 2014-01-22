var MC3UTILS = (function(window, document, $, utils, undefined) {
    utils.aloha_message = function (message) {
        $('#statusmessage').data('message')(message);
    };

    utils.bind_dialog_close_events = function () {
        $(document).on('click', '.ui-widget-overlay', function(){
            $(".ui-dialog-titlebar-close").trigger('click');
        });
    };

    utils.send_ajax = function(params, on_success, on_fail, on_always) {
        var method = 'GET';
        var contentType = 'application/json';
        on_fail = typeof on_fail !== 'undefined' ? on_fail : null;
        on_always = typeof on_always !== 'undefined' ? on_always : null;

        if (params.hasOwnProperty('method')) {
            method = params['method'];
        }
        var data = {};
        if (params.hasOwnProperty('data')) {
            data = params['data'];
        }
        if (params.hasOwnProperty('contentType')) {
            contentType = params['contentType'];
        }

        $.ajax({
            contentType: contentType,
            data: data,
            type: method,
            url: params['url']
        }).done(function (results) {
            if (on_success) {on_success(results);}
        }).fail(function(xhr, status, error) {
            var msg = 'Server error: ' + error;
            utils.update_status(msg);
            if (on_fail) {on_fail(msg);}
        }).always(function(xhr, status, error) {
            if (on_always) {on_always();}
        });
    };

    utils.send_authorized_ajax = function (data) {
        function get_agent_key(_callback) {
            var key_params = {
                'url': 'get_key/'
            };

            utils.send_ajax(key_params, _callback, null, null);
        }

        function key_callback(key) {
            if ($.type(key) !== 'undefined') {
                var send_params = {
                    'data': data,
                    'method': 'POST',
                    'url': MC3AUTH.get_objectives_url(key)
                };

                utils.send_ajax(send_params, notify_mc3_save, notify_mc3_error, null);
            } else {
                utils.update_status('Error: key not generated.');
            }
        }

        function notify_mc3_error(msg) {
            if (msg) {
                utils.aloha_message(msg);
            }
        }

        function notify_mc3_save(results) {
            if (results) {
                utils.aloha_message('Saved definition to MC3.');
            }
        }

        if (MC3AUTH.get_active_bank() === '') {
            utils.aloha_message('No MC3 bank selected; not saving definitions.');
        } else {
            // Get the agent key
            get_agent_key(key_callback);
        }
    };

    utils.update_status = function (message) {
        $('.status_box').html(message)
                .addClass('red');
        console.log(message);
    };

    return utils;
})(this, document, jQuery, MC3UTILS || {});