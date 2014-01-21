var VCB = (function (window, document, $, vcb, undefined) {
    vcb.bind_dialog_close_events = function () {
        $('div[role="dialog"] button.ui-dialog-titlebar-close').text('x');

        $(document).on('click', '.ui-widget-overlay', function(){
            $(".ui-dialog-titlebar-close").trigger('click');
        });
    }

    vcb.block_body = function (message) {
        $('body').block({
            message: '<h1>' + message + '</h1>',
            centerY: false,
            css: {
                border: '3px solid #a00',
                position: 'fixed',
                padding: '5px 15px 5px 15px',
                top: '100px',
                'z-index': '2010',
                opacity: 1
            },
            overlayCSS: {
                'z-index': '2000'
            }
        });
    }

    vcb.block_nav = function () {
        $('.navbar').block({
            message: null
        });
    }

    vcb.block_page = function (message) {
        vcb.block_body(message);
        vcb.block_nav();
    }

    vcb.clear_status_boxes = function () {
        $('.status_box').text('');
    }

    // For parsing the XML file with timestamps
    vcb.convert_time = function(time_secs){
        // from http://stackoverflow.com/questions/6312993/javascript-seconds-to-time-with-format-hhmmss
        var sec_num = parseInt(time_secs, 10); // don't forget the second param
        var hours   = Math.floor(sec_num / 3600);
        var minutes = Math.floor((sec_num - (hours * 3600)) / 60);
        var seconds = sec_num - (hours * 3600) - (minutes * 60);

        if (hours   < 10) {hours   = "0"+hours;}
        if (minutes < 10) {minutes = "0"+minutes;}
        if (seconds < 10) {seconds = "0"+seconds;}
        var time    = hours+':'+minutes+':'+seconds;
        return time;
    };

    vcb.init_powertip = function (identifier) {
        $(identifier).powerTip({
            mouseOnToPopup: true,
            placement: 'e',
            smartPlacement: true
        });
    };

    vcb.length = function (obj) {
        if ($.isArray(obj)) {
            return obj.length;
        } else {
            return Object.keys(obj).length;
        }
    };

    vcb.reset_upload_form = function () {
        $('#upload_form')[0].reset();
        $('.progress').hide();
    };

    vcb.reset_upload_progress = function () {
        $(".progress").show();
        $(".bar").width('0%');
        $(".percent").html("0%");
    };

    vcb.send_ajax = function (params, on_success, on_fail, on_always) {
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
    }

    // http://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript
    vcb.toTitle = function (string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    vcb.update_status = function (message) {
        $('.status_box').html(message)
                .addClass('red');
//        if ($('#modal_status_box').length === 0) {
//            if ($('#upload_status_box').length === 0) {
//                if ($('#admin_status_box').length === 0) {
//                    if ($('#status_box').length === 0) {
//                        $('#main_status_box').html(message)
//                                .addClass('red');
//                    } else {
//                        $('#status_box').html(message)
//                                .addClass('red');
//                    }
//                } else {
//                    $('#admin_status_box').html(message)
//                            .addClass('red');
//                }
//            } else {
//                $('#upload_status_box').html(message)
//                        .addClass('red');
//            }
//        } else {
//            $('#modal_status_box').html(message)
//                    .addClass('red');
//        }
        console.log(message);
    }

    vcb.unblock_body = function () {
        $('body').unblock();
    }

    vcb.unblock_nav = function () {
        $('.navbar').unblock();
    }

    vcb.unblock_page = function () {
        vcb.unblock_body();
        vcb.unblock_nav();
    }
    return vcb;
})(this, document, jQuery, VCB || {});