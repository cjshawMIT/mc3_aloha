var MC3UTILS = (function(window, document, $, utils, undefined) {
    function arrayify (str) {
        return str.toLowerCase().split(' ').sort(SortText);
    }

    function intersection_destructive (a, b) {
        // From:
        // http://stackoverflow.com/questions/1885557/simplest-code-for-array-intersection-in-javascript
        var result = new Array();
        while( a.length > 0 && b.length > 0 )
        {
            if      (a[0] < b[0] ){ a.shift(); }
            else if (a[0] > b[0] ){ b.shift(); }
            else /* they're equal */
            {
                result.push(a.shift());
                b.shift();
            }
        }

        return result;
    }

    //This will sort your array
    // From:
    // http://stackoverflow.com/questions/5503900/how-to-sort-an-array-of-objects-with-jquery-or-javascript
    function SortText(a, b){
      var aName = a.toLowerCase();
      var bName = b.toLowerCase();
      return ((aName < bName) ? -1 : ((aName > bName) ? 1 : 0));
    }

    utils.aloha_message = function (message) {
        $('#statusmessage').data('message')(message);
    };

    utils.bind_dialog_close_events = function () {
        $(document).on('click', '.ui-widget-overlay', function(){
            $(".ui-dialog-titlebar-close").trigger('click');
        });
    };

    utils.get_new_definition = function (ele) {
        return $(ele).data('new_value');
    };

    utils.search_bank_objectives = function (ele) {
        var term = utils.get_new_definition(ele);
        var params = {
            'url': MC3AUTH.get_objectives_url()
        };

        function all_objectives_results (results) {
            // If there are other objectives with
            // the same / similar term, could
            // prompt the user; if they want to add it
            // then put the description into the
            // 'body' class closest to this ele.
            try {
                var data = results;
                var matches = [];
                var counter = data.length;
                $.each(data, function (index, obj) {
                    if (utils.term_present(obj, term)) {
                        matches.push(obj);
                    }
                    if (--counter === 0) {
                        if (matches.length > 0) {
                            MC3AUTH.prompt_user_with_similar_terms(matches, ele);
                        }
                    }
                });
            } catch (e) {
                utils.update_status('Error in retrieving objectives from Handcar: ' + e);
            }
        }

        utils.send_ajax(params, all_objectives_results, null, null);
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

    utils.send_authorized_ajax = function (data, def) {
        function get_agent_key(_callback) {
            var key_params = {
                'data': {
                    'host': MC3AUTH.get_mc3_host()
                },
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
                if ($.parseJSON(data).hasOwnProperty('id')) {
                    send_params['method'] = 'PUT';
                }
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
                $(def).data('mc3_id', results.id);
            }
        }

        if (MC3AUTH.get_active_bank() === '') {
            utils.aloha_message('No MC3 bank selected; not saving definitions.');
        } else {
            // Get the agent key
            get_agent_key(key_callback);
        }
    };

    utils.term_present = function (obj, term) {
        var search_values = obj.displayName.text + ' ' + obj.description.text;
        search_values = arrayify(search_values);
        var search_terms = arrayify(term);
        if (intersection_destructive(search_values, search_terms).length > 0) {
            return true;
        } else {
            return false;
        }
    };

    utils.update_status = function (message) {
        $('.status_box').html(message)
                .addClass('red');
        console.log(message);
    };

    return utils;
})(this, document, jQuery, MC3UTILS || {});