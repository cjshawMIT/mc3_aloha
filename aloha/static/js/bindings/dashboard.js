$(document).ready(function() {
    MC3AUTH.set_mc3_host('oki-dev.mit.edu');
    MC3AUTH.init_host_selector();
    MC3AUTH.init_bank_selector();

    $(document).on('click', '.nav-help', function() {
        $('#help_modal').dialog({
            closeOnEscape: true,
            closeText: 'close',
            modal: true,
            width: 400
        });
        MC3UTILS.bind_dialog_close_events();
    });

    $('#bank_selector').on('change', function(e) {
        var raw_data = $(this).select2('data');
        MC3AUTH.set_active_bank(raw_data.id);
        // Need to refresh the bank URLs for these,
        // if they are present on the page already
        MC3AUTH.init_outcome_selectors();
    });

    $('#host_selector').on('change', function(e) {
        if (e.hasOwnProperty('val')) {
            var sel = e.val;
        } else {
            var sel = $(this).val();
        }
        MC3AUTH.set_mc3_host(sel);
        MC3AUTH.init_bank_selector();
    });

    $(document).on('click', '.toggle_similar', function () {
        $('#similar_defs').slideToggle();
        var icon = $(this).find('.fa');
        MC3AUTH.toggle_icon(icon);
    });

    $(document).on('click', '.existing_mc3_def', function () {
        var _this = $(this);
        MC3AUTH.set_name(_this);
        MC3AUTH.set_definition(_this);
        MC3AUTH.set_definition_mc3_id(_this);
        MC3AUTH.close_parent_dialog(_this);
    });

    Aloha.ready(function(){
        Aloha.require(['PubSub', 'genericbutton/genericbutton-plugin'],
                function(PubSub, GenericButton){
            // Save button is disabled until something is changed
            GenericButton.getButtons()["save"].enable(false);
            $('.btn.save').html('Saved');

            function savePreview(callback_function){
                var editor = Aloha.getEditableById('canvas');
                if(editor.isModified()){
                    // setUnmodified, to avoid another concurrent save from
                    // firing while this one is still ongoing.
                    editor.setUnmodified();

                    var $html = $('<html />');
                    $html.attr('xmlns',      'http://www.w3.org/1999/xhtml');
                    $html.attr('xmlns:c',    'http://cnx.rice.edu/cnxml');
                    $html.attr('xmlns:md',   'http://cnx.rice.edu/mdml/0.4');
                    $html.attr('xmlns:qml',  'http://cnx.rice.edu/qml/1.0');
                    $html.attr('xmlns:mod',  'http://cnx.rice.edu/#moduleIds' );
                    $html.attr('xmlns:bib',  'http://bibtexml.sf.net/');
                    $html.attr('xmlns:data', 'http://dev.w3.org/html5/spec/#custom');

                    // Build simple header with title.
                    var $head = $('<head />'),
                        title = editor.obj.find('>div.title').text();
                    $('<title/>').text(title).appendTo($head);
                    $html.append($head);

                    var $body = $('<body />');
                    $body.attr('class', 'content');
                    $body.append(editor.getContents());

                    // This is going to break in IE. Which is fine, because
                    // we don't support that right now. Hint to poor person
                    // who has to develop that: ActiveXObject
                    // Microsoft.XMLDOM
                    var html = (new XMLSerializer()).serializeToString(
                        $html.append($body).get(0));
                    if(save_url !== null){
                        $.post(save_url,
                                {html: html}, function(data, statustext){
                            if(data.error){
                                $('#statusmessage').data('message')(data.error, 'error', 0);
                            } else {
                                $('#statusmessage').data('message')('Saved');
                                GenericButton.getButtons()["save"].enable(false);
                                $('.btn.save').html('Saved');
                                if (callback_function) {
                                    callback_function();
                                }
                            }
                            PubSub.pub('swordpushweb.saved');
                        });
                    } else {
                        $('#statusmessage').data('message')('Fake save of text.');
                        GenericButton.getButtons()["save"].enable(false);
                        $('.btn.save').html('Saved');
                        if (callback_function) {
                            callback_function();
                        }
                    }

                    // Added for MC3 demo for definitions
                    if ($('dl.mc3definition.aloha-oer-block').length > 0) {
                        MC3AUTH.save_definitions_to_mc3();
                    }
                }
            }

            // Attach save handler to Save button
            PubSub.sub('swordpushweb.save', function(data){
                savePreview();
                if(data && data.callback){
                    data.callback();
                }
            });

            // Set up status message area
            var statusarea = $('#statusmessage');
            statusarea.data('message', function(message, type, delay) {
                type = type || 'info';
                if(delay === undefined){
                    delay = 1500;
                }
                var ob = $("<div />",
                  {'class': type, text: message}).hide()
                  .appendTo(statusarea).center().fadeIn(700);
                if(delay>0){
                    ob.delay(delay).fadeOut(800, function() { $(this).remove(); });
                } else {
                    ob.addClass('persistent-error');
                    var close = $('<i> </i>');
                    ob.append(close);
                    close.on('click', function(e){
                        $(e.target).off('click');
                        ob.remove();
                    });
                }
            });

            // Fetch the preview
            $('#statusmessage').data('message')('Loading preview...');
            Aloha.jQuery.get(body_url, function(data){
                var $d = Aloha.jQuery('<div />').html(data);
                var $editable = Aloha.jQuery('#canvas').html(
                    $d.find('> *'));

                // Remove the pyramid debug toolbar from the preview
                // if it exists. This code should do nothing in production
                $editable.find('#pDebug').remove();
                $editable.aloha().focus();

                MathJax.Hub.Configured();

                // Auto-save periodically. This only does anything if
                // editor.isModified().
                window.setInterval(savePreview, 30000);

                setInterval(function() {
                    var editor = Aloha.getEditableById('canvas');
                    if (editor.isModified()) {
                        $('.btn.save').html('Save');
                        GenericButton.getButtons()["save"].enable(true);
                    }
                }, 250);
                Aloha.jQuery('#statusmessage').data('message')('Preview loaded');
            });
        });
    });
});