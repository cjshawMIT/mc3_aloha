/**
 * bootbox.js v3.3.0
 *
 * http://bootboxjs.com/license.txt
 *
 * Modified:
 * August 2013
 * Cole Shaw, MIT OEIT
 */
var bootbox = window.bootbox || (function(document, $) {
    /*jshint scripturl:true sub:true */

    var _locale        = 'en',
        _defaultLocale = 'en',
        _animate       = true,
        _backdrop      = 'static',
        _defaultHref   = 'javascript:;',
        _classes       = '',
        _btnClasses    = {},
        _icons         = {},
        /* last var should always be the public object we'll return */
        that           = {};


    /**
     * public API
     */
    that.setLocale = function(locale) {
        for (var i in _locales) {
            if (i == locale) {
                _locale = locale;
                return;
            }
        }
        throw new Error('Invalid locale: '+locale);
    };

    that.addLocale = function(locale, translations) {
        if (typeof _locales[locale] === 'undefined') {
            _locales[locale] = {};
        }
        for (var str in translations) {
            _locales[locale][str] = translations[str];
        }
    };

    that.setIcons = function(icons) {
        _icons = icons;
        if (typeof _icons !== 'object' || _icons === null) {
            _icons = {};
        }
    };

    that.setBtnClasses = function(btnClasses) {
        _btnClasses = btnClasses;
        if (typeof _btnClasses !== 'object' || _btnClasses === null) {
            _btnClasses = {};
        }
    };

    that.alert = function(/*str, label, cb*/) {
        var str   = "",
            label = _translate('OK'),
            cb    = null;

        switch (arguments.length) {
            case 1:
                // no callback, default button label
                str = arguments[0];
                break;
            case 2:
                // callback *or* custom button label dependent on type
                str = arguments[0];
                if (typeof arguments[1] == 'function') {
                    cb = arguments[1];
                } else {
                    label = arguments[1];
                }
                break;
            case 3:
                // callback and custom button label
                str   = arguments[0];
                label = arguments[1];
                cb    = arguments[2];
                break;
            default:
                throw new Error("Incorrect number of arguments: expected 1-3");
        }

        return that.dialog(str, {
            // only button (ok)
            "label"   : label,
            "icon"    : _icons.OK,
            "class"   : _btnClasses.OK,
            "callback": cb
        }, {
            // ensure that the escape key works; either invoking the user's
            // callback or true to just close the dialog
            "onEscape": cb || true
        });
    };

    that.confirm = function(/*str, labelCancel, labelOk, cb*/) {
        var str         = "",
            labelCancel = _translate('CANCEL'),
            labelOk     = _translate('CONFIRM'),
            cb          = null;

        switch (arguments.length) {
            case 1:
                str = arguments[0];
                break;
            case 2:
                str = arguments[0];
                if (typeof arguments[1] == 'function') {
                    cb = arguments[1];
                } else {
                    labelCancel = arguments[1];
                }
                break;
            case 3:
                str         = arguments[0];
                labelCancel = arguments[1];
                if (typeof arguments[2] == 'function') {
                    cb = arguments[2];
                } else {
                    labelOk = arguments[2];
                }
                break;
            case 4:
                str         = arguments[0];
                labelCancel = arguments[1];
                labelOk     = arguments[2];
                cb          = arguments[3];
                break;
            default:
                throw new Error("Incorrect number of arguments: expected 1-4");
        }

        var cancelCallback = function() {
            if (typeof cb === 'function') {
                return cb(false);
            }
        };

        var confirmCallback = function() {
            if (typeof cb === 'function') {
                return cb(true);
            }
        };

        return that.dialog(str, [{
            // first button (cancel)
            "label"   : labelCancel,
            "icon"    : _icons.CANCEL,
            "class"   : _btnClasses.CANCEL,
            "callback": cancelCallback
        }, {
            // second button (confirm)
            "label"   : labelOk,
            "icon"    : _icons.CONFIRM,
            "class"   : _btnClasses.CONFIRM,
            "callback": confirmCallback
        }], {
            // escape key bindings
            "onEscape": cancelCallback
        });
    };

    that.prompt = function(/*str, labelCancel, labelOk, cb, defaultVal*/) {
        var str         = "",
            labelCancel = _translate('CANCEL'),
            labelOk     = _translate('CONFIRM'),
            cb          = null,
            defaultVal  = "";

        switch (arguments.length) {
            case 1:
                str = arguments[0];
                break;
            case 2:
                str = arguments[0];
                if (typeof arguments[1] == 'function') {
                    cb = arguments[1];
                } else {
                    labelCancel = arguments[1];
                }
                break;
            case 3:
                str         = arguments[0];
                labelCancel = arguments[1];
                if (typeof arguments[2] == 'function') {
                    cb = arguments[2];
                } else {
                    labelOk = arguments[2];
                }
                break;
            case 4:
                str         = arguments[0];
                labelCancel = arguments[1];
                labelOk     = arguments[2];
                cb          = arguments[3];
                break;
            case 5:
                str         = arguments[0];
                labelCancel = arguments[1];
                labelOk     = arguments[2];
                cb          = arguments[3];
                defaultVal  = arguments[4];
                break;
            default:
                throw new Error("Incorrect number of arguments: expected 1-5");
        }

        var header = str;

        // let's keep a reference to the form object for later
        var form = $("<form></form>");
        form.append("<input class='input-block-level' autocomplete=off type=text value='" + defaultVal + "' />");

        var cancelCallback = function() {
            if (typeof cb === 'function') {
                // yep, native prompts dismiss with null, whereas native
                // confirms dismiss with false...
                return cb(null);
            }
        };

        var confirmCallback = function() {
            if (typeof cb === 'function') {
                return cb(form.find("input[type=text]").val());
            }
        };

        var div = that.dialog(form, [{
            // first button (cancel)
            "label"   : labelCancel,
            "icon"    : _icons.CANCEL,
            "class"   : _btnClasses.CANCEL,
            "callback":  cancelCallback
        }, {
            // second button (confirm)
            "label"   : labelOk,
            "icon"    : _icons.CONFIRM,
            "class"   : _btnClasses.CONFIRM,
            "callback": confirmCallback
        }], {
            // prompts need a few extra options
            "header"  : header,
            // explicitly tell dialog NOT to show the dialog...
            "show"    : false,
            "onEscape": cancelCallback
        });

        // ... the reason the prompt needs to be hidden is because we need
        // to bind our own "shown" handler, after creating the modal but
        // before any show(n) events are triggered
        // @see https://github.com/makeusabrew/bootbox/issues/69

        div.on("shown", function() {
            form.find("input[type=text]").focus();

            // ensure that submitting the form (e.g. with the enter key)
            // replicates the behaviour of a normal prompt()
            form.on("submit", function(e) {
                e.preventDefault();
                div.find(".btn-primary").click();
            });
        });

        div.modal("show");

        return div;
    };

    // admin help page:
    that.admin_help = function(/*str, labelCancel, labelOk, cb, defaultVal*/) {
        var str         = "",
            labelCancel = _translate('CANCEL'),
            labelOk     = _translate('CONFIRM'),
            cb          = null,
            defaultVal  = "";

        switch (arguments.length) {
            case 1:
                str = arguments[0];
                break;
            case 2:
                str = arguments[0];
                if (typeof arguments[1] == 'function') {
                    cb = arguments[1];
                } else {
                    labelCancel = arguments[1];
                }
                break;
            case 3:
                str         = arguments[0];
                labelCancel = arguments[1];
                if (typeof arguments[2] == 'function') {
                    cb = arguments[2];
                } else {
                    labelOk = arguments[2];
                }
                break;
            case 4:
                str         = arguments[0];
                labelCancel = arguments[1];
                labelOk     = arguments[2];
                cb          = arguments[3];
                break;
            case 5:
                str         = arguments[0];
                labelCancel = arguments[1];
                labelOk     = arguments[2];
                cb          = arguments[3];
                defaultVal  = arguments[4];
                break;
            default:
                throw new Error("Incorrect number of arguments: expected 1-5");
        }

        var header = str;

        function add_note_to_list(parent, text) {
            var ele = $('<li></li>')
                    .text(text);
            parent.append(ele);
        }

        var wrapper = $('<div></div>');
        var list = $('<ul></ul>');
        add_note_to_list(list, 'Uploading videos is bandwidth limited. ' +
                'Users are only allowed 1500 seconds--' +
                'this is adequate for the MIT network, but may not be adequate off campus. ' +
                'If this is an issue, contact the VCB admins (oeit-vcb-admin [at] mit [dot] edu).');
        add_note_to_list(list, 'You can upload multiple videos at a time, ' +
                'but ONLY for different classes. Anything saved for a class ' +
                "automatically overwrites the previous save, so don't try to " +
                'open multiple tabs and upload multiple videos to the same class.');
        add_note_to_list(list, 'Right-click on the different elements in the tree ' +
                'to see what actions you can take.');
        add_note_to_list(list, 'You can edit the headings and text in-line, but ' +
                'give the items unique names.');

        wrapper.append(list);

        var cancelCallback = function() {
            if (typeof cb === 'function') {
                // yep, native prompts dismiss with null, whereas native
                // confirms dismiss with false...
                return cb(null);
            }
        };

        var confirmCallback = function() {
            if (typeof cb === 'function') {
                return cb(true);
            }
        };

        var div = that.dialog(wrapper, [{
            // first button (cancel)
            "label"   : labelCancel,
            "icon"    : _icons.CANCEL,
            "class"   : _btnClasses.CANCEL,
            "callback":  cancelCallback
        }, {
            // second button (confirm)
            "label"   : labelOk,
            "icon"    : _icons.CONFIRM,
            "class"   : _btnClasses.CONFIRM,
            "callback": confirmCallback
        }], {
            // prompts need a few extra options
            "header"  : header,
            // explicitly tell dialog NOT to show the dialog...
            "show"    : false,
            "onEscape": cancelCallback
        });

        // ... the reason the prompt needs to be hidden is because we need
        // to bind our own "shown" handler, after creating the modal but
        // before any show(n) events are triggered
        // @see https://github.com/makeusabrew/bootbox/issues/69

        div.on("shown", function() {
        });

        div.modal("show");

        return div;
    }; // end of admin help

    // added in form dual inputs in a prompt for adding new classes + class numbers:
    that.duoprompt = function(/*str, labelCancel, labelOk, cb, defaultVal*/) {
            var str         = "",
                labelCancel = _translate('CANCEL'),
                labelOk     = _translate('CONFIRM'),
                cb          = null,
                defaultVal  = "";

            switch (arguments.length) {
                case 1:
                    str = arguments[0];
                    break;
                case 2:
                    str = arguments[0];
                    if (typeof arguments[1] == 'function') {
                        cb = arguments[1];
                    } else {
                        labelCancel = arguments[1];
                    }
                    break;
                case 3:
                    str         = arguments[0];
                    labelCancel = arguments[1];
                    if (typeof arguments[2] == 'function') {
                        cb = arguments[2];
                    } else {
                        labelOk = arguments[2];
                    }
                    break;
                case 4:
                    str         = arguments[0];
                    labelCancel = arguments[1];
                    labelOk     = arguments[2];
                    cb          = arguments[3];
                    break;
                case 5:
                    str         = arguments[0];
                    labelCancel = arguments[1];
                    labelOk     = arguments[2];
                    cb          = arguments[3];
                    defaultVal  = arguments[4];
                    break;
                default:
                    throw new Error("Incorrect number of arguments: expected 1-5");
            }

            var header = str;

            // let's keep a reference to the form object for later
            var form = $("<form></form>");
            form.append('<label>Class Name: </label>');
            form.append('<input class="input-block-level"' +
                    'autocomplete=off id="classname" type=text value="' + 
                    defaultVal + '" />'
            );
            form.append('<label>Class Number (MIT): </label>');
            form.append('<input class="input-block-level"' +
                    'autocomplete=off id="classnumber" type=text value="' + 
                    defaultVal + '" />'
            );


            var cancelCallback = function() {
                if (typeof cb === 'function') {
                    // yep, native prompts dismiss with null, whereas native
                    // confirms dismiss with false...
                    return cb(null);
                }
            };

            var confirmCallback = function() {
                if (typeof cb === 'function') {
                    var classname = $('#classname').val();
                    var classnumber = $('#classnumber').val();
                    return cb({'classname': classname, 'classnumber': classnumber});
                }
            };

            var div = that.dialog(form, [{
                // first button (cancel)
                "label"   : labelCancel,
                "icon"    : _icons.CANCEL,
                "class"   : _btnClasses.CANCEL,
                "callback":  cancelCallback
            }, {
                // second button (confirm)
                "label"   : labelOk,
                "icon"    : _icons.CONFIRM,
                "class"   : _btnClasses.CONFIRM,
                "callback": confirmCallback
            }], {
                // prompts need a few extra options
                "header"  : header,
                // explicitly tell dialog NOT to show the dialog...
                "show"    : false,
                "onEscape": cancelCallback
            });

            // ... the reason the prompt needs to be hidden is because we need
            // to bind our own "shown" handler, after creating the modal but
            // before any show(n) events are triggered
            // @see https://github.com/makeusabrew/bootbox/issues/69

            div.on("shown", function() {
                form.find("input[id=classname]").focus();

                // ensure that submitting the form (e.g. with the enter key)
                // replicates the behaviour of a normal prompt()
                form.on("submit", function(e) {
                    e.preventDefault();
                    div.find(".btn-primary").click();
                });
            });

            div.modal("show");

            return div;
        };
    // end of custom dual prompt

    // added in video inputs in a prompt for adding new activities:
    // Included new classname input variable
    that.videoprompt = function(/*str, classname, topic, labelCancel, labelOk, cb, defaultVal*/) {
            var str         = "",
                classname = "",
                topic = '',
                labelCancel = _translate('CANCEL'),
                labelOk     = _translate('CONFIRM'),
                cb          = null,
                defaultVal  = "";

            switch (arguments.length) {
                case 1:
                    str = arguments[0];
                    break;
                case 2:
                    str = arguments[0];
                    if (typeof arguments[1] == 'function') {
                        cb = arguments[1];
                    } else {
                        classname = arguments[1];
                    }
                    break;
                case 3:
                    str         = arguments[0];
                    classname 	= arguments[1];
                    if (typeof arguments[2] == 'function') {
                        cb = arguments[2];
                    } else {
                        topic = arguments[2];
                    }
                    break;
                case 4:
                    str			= arguments[0];
                    classname 	= arguments[1];
                    topic       = arguments[2];
                    if (typeof arguments[3] == 'function') {
                        cb 		= arguments[3];
                    } else {
                        labelCancel = arguments[3];
                    }
                    break;
                case 5:
                    str         = arguments[0];
                    classname 	= arguments[1];
                    topic       = arguments[2];
                    labelCancel = arguments[3];
                    if (typeof arguments[4] == 'function') {
                        cb 		= arguments[4];
                    } else {
                        labelOk = arguments[4];
                    }
                    break;
                case 6:
                    str         = arguments[0];
                    classname	= arguments[1];
                    topic       = arguments[2];
                    labelCancel = arguments[3];
                    labelOk     = arguments[4];
                    if (typeof arguments[5] == 'function') {
                        cb 		= arguments[5];
                    } else {
                        defaultVal = arguments[5];
                    }
                    break;
                case 7:
                    str         = arguments[0];
                    classname	= arguments[1];
                    topic       = arguments[2];
                    labelCancel = arguments[3];
                    labelOk     = arguments[4];
                    cb          = arguments[5];
                    defaultVal  = arguments[6];
                    break;
                default:
                    throw new Error("Incorrect number of arguments: expected 1-7");
            }

            var header = str;

            var container = $('<div></div>');
            var status_box = $('<div id="status_box" class="status_box"></div>');
            var video_form = $('<form id="video_object" name="video_object"' +
                    'action="" method="POST" enctype="multipart/form-data"></form>');
            video_form.append('<input type="hidden" name="classname" ' +
                    'id="modal_classname" value="' + classname + '" />');

            video_form.append('<label>Video File (MOV format): </label>');
            video_form.append('<input class="input-block-level"' +  
                    'autocomplete=off id="video_file" name="video_file" ' +  
                    'type=file required="required" accept="video/mov" onchange="' +
                            '$(&quot;#vid_url&quot;).attr(&quot;readonly&quot;,&quot;readonly&quot;);' +
                            'var filename = $(this).val();' + 
                            'VCB.s3_upload(filename);" />');

            // include a progress bar for the upload (video files are big!)
            // From: http://jquery.malsup.com/form/progress.html
            var progress_div = $('<div></div>').addClass('progress');
            var progress_bar = $('<div></div>').addClass('bar');
            var progress_text = $('<div></div>').addClass('percent');

            progress_div.append(progress_bar);
            progress_div.append(progress_text);

            video_form.append('<label>Video upload progress: </label>');
            video_form.append(progress_div);

            // Include a transcript upload form
            var transcript_form = $('<form id="transcript_form" name="transcript_form"' +
                    'action="" method="POST" enctype="multipart/form-data"></form>');
            transcript_form.append('<input type="hidden" name="classname" ' +
                    'id="modal_classname" value="' + classname + '" />');

            transcript_form.append('<label>Transcript File (optional; *.vtt): </label>');
            transcript_form.append('<input class="input-block-level"' +
                    'autocomplete=off id="transcript_file" name="transcript_file" ' +
                    'type=file required="required" onchange="' +
                            'var filename = $(this).val();' +
                            'VCB.s3_upload(filename, true);" />');

            var form = $('<form id="video_metadata" name="video_metadata"' +
                    'action="" method="POST" enctype="multipart/form-data"></form>');

            form.append('<label>Video URL (if not uploading). Preferably to an .m3u8 file: </label>');
            form.append('<input type="text" id="vid_url" class="url_text"  value=""></input>');
            form.append('<input type="hidden" id="transcript_url" value=""></input>');
            // need a form value for class session
            var session_div = $('<div></div>').addClass('ui-widget');
            var session_field = $('<label></label>');
            session_field.text('Class Session: ');
            var session_input = $('<input id="class_session"' +
                    'name="class_session" required="required"></input>');

            session_div.append(session_field);
            session_div.append(session_input);
            form.append(session_div);

            var sessions = [];

            // do an ajax call to get the current class sessions
            $.ajax({
                type: "GET",
                url: "get_class_sessions/",
                data: {
                    'classname': VCB.admin_classname,
                    'semester': VCB.admin_semester
                },
                success: function(session_names) {
                    // make the select options here
                    sessions = session_names.sort();
                },
                error: function(xhr, status, error) {
                    alert(error);
                }
            });

            form.append('<input type="hidden" name="classname" value="' +
                    classname + '"></input>'
            );
            form.append('<label>Recorded Date: </label>');
            form.append('<input id="recorded_date" autocomplete=off' +
                    'name="recorded_date" type=text required="required" />');
            form.append('<label>To-publish Date: </label>');
            form.append('<input id="pubdate" autocomplete=off name="pubdate"' +
                    'type=text required="required" />');
            VCB.append_auto_tag(form, topic);

            container.append(status_box);
            container.append(video_form);
            container.append(transcript_form);
            container.append(form);

            var cancelCallback = function() {
                if (typeof cb === 'function') {
                    // yep, native prompts dismiss with null, whereas native
                    // confirms dismiss with false...
                    $('.admin-action').removeClass('active-btn');
                    return cb(null);
                }
            };

            var confirmCallback = function() {
                // don't let the user continue unless video is done uploading
                var video_url = $('#vid_url').val();
                var transcript_url = $('#transcript_url').val();
                var classSession = $('#class_session').val();
                var recordedDate = $('#recorded_date').val();
                var pubDate = $('#pubdate').val();
                var subjects = $('input[name="subject\\[\\]"]').val();
                if (video_url == '') {
                    VCB.update_status('Please wait for the video to finish uploading or ' +
                                  'include a video url, before pressing OK');
                    return false;
                } else if (classSession == '' ||
                           recordedDate == '' ||
                           pubDate == '' ||
                           subjects == '') {
                    VCB.update_status('Please fill in all fields, ' +
                            'including at least one Timetag');
                    return false;
                } else {
                    if (typeof cb === 'function') {
                        video_url = video_url.replace('http://', 'https://');
                        //http://stackoverflow.com/questions/2627813/how-to-get-an-array-with-jquery-multiple-input-with-the-same-name
                        var subjects = $('input[name="subject\\[\\]"]').map(function() {
                            return $(this).val();
                        }).get();
                        var timetags = $('input[name="timetag\\[\\]"]').map(function() {
                            return $(this).val();
                        }).get();
                        var class_session = $('#class_session').val();
                        var recorddate = $('#recorded_date').val();
                        var pubdate = $('#pubdate').val();

                        var results = {
                                'video_url': video_url,
                                'subjects': subjects,
                                'class_session': class_session,
                                'recorddate': recorddate,
                                'timetags': timetags,
                                'transcript_url': transcript_url,
                                'pubdate': pubdate
                        };
                        return cb(results);
                    }
                }
            };

            var div = that.dialog(container, [{
                // first button (cancel)
                "label"   : labelCancel,
                "icon"    : _icons.CANCEL,
                "class"   : _btnClasses.CANCEL,
                "callback":  cancelCallback
            }, {
                // second button (confirm)
                "label"   : labelOk,
                "icon"    : _icons.CONFIRM,
                "class"   : _btnClasses.CONFIRM,
                "callback": confirmCallback
            }], {
                // prompts need a few extra options
                "header"  : header,
                // explicitly tell dialog NOT to show the dialog...
                "show"    : false,
                "onEscape": cancelCallback
            });

            // ... the reason the prompt needs to be hidden is because we need
            // to bind our own "shown" handler, after creating the modal but
            // before any show(n) events are triggered
            // @see https://github.com/makeusabrew/bootbox/issues/69

            div.on("shown", function() {
                form.find("input[id=class_session]").focus();
                $('#pubdate').datepicker({dateFormat: 'yy-mm-dd'});
                $('#recorded_date').datepicker({dateFormat: 'yy-mm-dd'});
                $('#class_session').autocomplete({
                    source: sessions
                });

                $(document).on('click', '#enter_tags', function() {
                    VCB.remove_auto_tags();
                    VCB.append_timetag_fields(form);
                    VCB.init_timetag_entry();
                });

//	             ensure that submitting the form (e.g. with the enter key)
//	             replicates the behaviour of a normal prompt()
                form.on("submit", function(e) {
                    e.preventDefault();
                    div.find(".btn-primary").click();
                });
            });

            div.modal("show");

            return div;
        };
    // end of custom video prompt

    // Edit an existing url:
    that.editurl = function(/*str, new_url, labelCancel, labelOk, cb, defaultVal*/) {
            var str         = "",
                new_url     = "",
                labelCancel = _translate('CANCEL'),
                labelOk     = _translate('CONFIRM'),
                cb          = null,
                defaultVal  = "";

            switch (arguments.length) {
                case 1:
                    str = arguments[0];
                    break;
                case 2:
                    str = arguments[0];
                    if (typeof arguments[1] == 'function') {
                        cb = arguments[1];
                    } else {
                        new_url = arguments[1];
                    }
                    break;
                case 3:
                    str         = arguments[0];
                    new_url 	= arguments[1];
                    if (typeof arguments[2] == 'function') {
                        cb = arguments[2];
                    } else {
                        labelCancel = arguments[2];
                    }
                    break;
                case 4:
                    str			= arguments[0];
                    new_url 	= arguments[1];
                    labelCancel = arguments[2];
                    if (typeof arguments[3] == 'function') {
                        cb 		= arguments[3];
                    } else {
                        labelOk = arguments[3];
                    }
                    break;
                case 5:
                    str         = arguments[0];
                    new_url 	= arguments[1];
                    labelCancel = arguments[2];
                    labelOk     = arguments[3];
                    cb          = arguments[4];
                    break;
                case 6:
                    str         = arguments[0];
                    new_url   	= arguments[1];
                    labelCancel = arguments[2];
                    labelOk     = arguments[3];
                    cb          = arguments[4];
                    defaultVal  = arguments[5];
                    break;
                default:
                    throw new Error("Incorrect number of arguments: expected 1-6");
            }

            var header = str;

            var container = $('<div></div>');
            var status_box = $('<div id="modal_status_box"></div>');

            var form = $('<form id="url_form" name="url_form"' +
                    'action="" method="POST" enctype="multipart/form-data"></form>');

            form.append('<label>Old URL: </label>');
            form.append('<input type="text" id="old_url" class="url_text" value="' +
                            new_url + '" readonly></input>');
            form.append('<label>New URL, preferably to an .m3u8 file: </label>');
            form.append('<input type="text" id="new_url" class="url_text" value=""></input>');

            container.append(status_box);
            container.append(form);

            var cancelCallback = function() {
                if (typeof cb === 'function') {
                    // yep, native prompts dismiss with null, whereas native
                    // confirms dismiss with false...
                    return cb(null);
                }
            };

            var confirmCallback = function() {
                var video_url = $('#new_url').val();
                if (video_url == '') {
                    $('#status_box')
                            .text('Please enter a new url or click Cancel')
                            .addClass('red');
                    return false;
                } else {
                    if (typeof cb === 'function') {
                        video_url = video_url.replace('http://', 'https://');
                        return cb(video_url);
                    }
                }
            };

            var div = that.dialog(container, [{
                // first button (cancel)
                "label"   : labelCancel,
                "icon"    : _icons.CANCEL,
                "class"   : _btnClasses.CANCEL,
                "callback":  cancelCallback
            }, {
                // second button (confirm)
                "label"   : labelOk,
                "icon"    : _icons.CONFIRM,
                "class"   : _btnClasses.CONFIRM,
                "callback": confirmCallback
            }], {
                // prompts need a few extra options
                "header"  : header,
                // explicitly tell dialog NOT to show the dialog...
                "show"    : false,
                "onEscape": cancelCallback
            });

            // ... the reason the prompt needs to be hidden is because we need
            // to bind our own "shown" handler, after creating the modal but
            // before any show(n) events are triggered
            // @see https://github.com/makeusabrew/bootbox/issues/69

            div.on("shown", function() {
                form.find("input[id=new_url]").focus();
            });

            div.modal("show");

            return div;
        };
    // end of custom editurl

    // added in form select class inputs in a prompt:
    that.selectclass = function(/*str, labelCancel, labelOk, cb, defaultVal*/) {
            var str         = "",
                labelCancel = _translate('CANCEL'),
                labelOk     = _translate('CONFIRM'),
                cb          = null,
                defaultVal  = "";

            switch (arguments.length) {
                case 1:
                    str = arguments[0];
                    break;
                case 2:
                    str = arguments[0];
                    if (typeof arguments[1] == 'function') {
                        cb = arguments[1];
                    } else {
                        labelCancel = arguments[1];
                    }
                    break;
                case 3:
                    str         = arguments[0];
                    labelCancel = arguments[1];
                    if (typeof arguments[2] == 'function') {
                        cb = arguments[2];
                    } else {
                        labelOk = arguments[2];
                    }
                    break;
                case 4:
                    str         = arguments[0];
                    labelCancel = arguments[1];
                    labelOk     = arguments[2];
                    cb          = arguments[3];
                    break;
                case 5:
                    str         = arguments[0];
                    labelCancel = arguments[1];
                    labelOk     = arguments[2];
                    cb          = arguments[3];
                    defaultVal  = arguments[4];
                    break;
                default:
                    throw new Error("Incorrect number of arguments: expected 1-5");
            }

            var header = str;

            // let's keep a reference to the form object for later
            var form = $('<form id="class_form"></form>');

            var status_box = $('<div id="status_box"></div>');
            form.append(status_box);

            var class_container = $('<div id="class_container"></div>')
                    .addClass('well well-small span6')
                    .css('min-height', '200px');
            var class_div = $('<div id="class_div"></div>')
                    .addClass('row row-fluid span6');
            var add_class_btn = $('<div id="add_class">Add Class</div>')
                    .addClass('btn btn-primary btn-large span3');
            var semester_dropdown = $('<div id="add_semester"></div>')
                    .addClass('dropdown btn btn-warning btn-large span4');
            var semester_trigger = $('<span id="semester_trigger"' +
                    'data-toggle="dropdown">Copy Class</span>')
                    .addClass('dropdown-toggle');
            var semester_list = $('<ul role="menu" aria-labelledby="semester"></ul>')
                    .addClass('dropdown-menu');
            var class_dropdown = $('<div id="class_dropdown"></div>')
                    .addClass('dropdown btn btn-large btn-success span4');
            var dropdown_trigger = $('<span id="dropdown_trigger"' +
                    'data-toggle="dropdown">Edit Class</span>')
                    .addClass('dropdown-toggle');
            var dropdown_list = $('<ul role="menu" aria-labelledby="classes"></ul>')
                    .addClass('dropdown-menu');

            $.ajax({
                type: "GET",
                url: "get_classes/",
                success: function(class_list) {
                    var classes_no_semesters = {};
                    // add each class to the dropdown_list as an <li> item
                    $.each(class_list, function(index, single_class) {
                        var id = single_class['pk'];
                        var name = single_class['fields']['class_name'];
                        var number = single_class['fields']['class_number'];
                        var obj_bank_id = single_class['fields']['obj_bank_id'];
                        var semester = single_class['fields']['semester'];
                        var access_code = single_class['fields']['access_code'];

                        var list_txt = '<li data-id="' + id + '" data-number="' +
                                number + '" data-obj-bank="' + obj_bank_id +
                                '" data-name="' + name + '" data-code="' + access_code +
                                '" data-semester ="' + semester + '"><a tabindex="-1"' +
                                ' href="#">' + name + ', ' + semester + '</a></li>';

                        var list_item = $(list_txt)
                                .addClass('text-left select-class');

                        dropdown_list.append(list_item);

                        if (!classes_no_semesters.hasOwnProperty(name)) {
                            var new_class = {
                                'id': id,
                                'number': number,
                                'obj_bank_id': obj_bank_id,
                                'access_code': access_code,
                                'semesters': []
                            };
                            new_class['semesters'].push(semester);
                            classes_no_semesters[name] = new_class;
                        } else {
                            classes_no_semesters[name]['semesters'].push(semester);
                        }

                    });

                    $.each(classes_no_semesters, function(name, class_data) {
                        var id = class_data['id'];
                        var number = class_data['number'];
                        var obj_bank_id = class_data['obj_bank_id'];
                        var semesters = class_data['semesters'];
                        var access_code = class_data['access_code'];

                        var list_txt = '<li data-id="' + id + '" data-number="' +
                                number + '" data-obj-bank="' + obj_bank_id +
                                '" data-name="' + name + '" data-code="' + access_code +
                                '" data-semesters ="' + semesters + '"><a tabindex="-1"' +
                                ' href="#">' + name + '</a></li>';

                        var list_item = $(list_txt)
                                .addClass('text-left select-semester');

                        semester_list.append(list_item);
                    });
                },
                error: function(xhr, status, error) {
                    alert(error);
                }
            });

            class_dropdown.append(dropdown_trigger);
            class_dropdown.append(dropdown_list);

            semester_dropdown.append(semester_trigger);
            semester_dropdown.append(semester_list);

            if (user_is_superuser == 'True') {
                class_div.append(add_class_btn);
                class_div.append(semester_dropdown);
            }

            class_div.append(class_dropdown);
            class_container.append(class_div);
            form.append(class_container);

            var cancelCallback = function() {
                if (typeof cb === 'function') {
                    // yep, native prompts dismiss with null, whereas native
                    // confirms dismiss with false...
                    return cb(null);
                }
            };

            var confirmCallback = function() {
                var classname = $('#class_name').val();
                var classnumber = $('#class_number').val();
                var obj_bank_id = $('#obj_bank_id').data('obj-bank');
                var semester = $('#semester').val();
                var new_class = $('#new_class').val();
                var code = $('#access_code').val();
                var new_semester = $('#new_semester').val();

                function initialize_class(classname, bank_id, message, semester) {
                    $('#admin_canvas_heading')
                            .html('<i class="fa fa-pencil"></i>' +
                                    ' ' + classname + ', ' + semester +
                                    '. Access code: ' + code);
                    VCB.update_status(message);

                    lscache.set('obj_bank_id', obj_bank_id, 1440);
                    VCB.initialize_canvas(classname, semester, obj_bank_id);
                }

                if ($('#new_container').length) {
                    VCB.block_body('Processing. This could take ~10 minutes, ' +
                            'depending on the size of the class.');

                    if (new_class == 'true'){
                        var copy = $('#copy').val();
                        if (copy == 'true') {
                            var semester_array = $('#semester_array').val();
                            if ($.type(semester_array) === 'string') {
                                semester_array = [semester_array];
                            }
                            if ((classname == "" || classnumber == "" || semester == "") || (new_semester == "")) {
                                VCB.update_status('You must include a class name, ' +
                                        'a class number, an old semester, and a new semester.');
                                return false;
                            }
                            if ($.inArray(new_semester, semester_array) > -1) {
                                VCB.update_status('A class already exists for' +
                                        'your new semester.');
                                return false;
                            }
                        } else {
                            if ((classname == "" || classnumber == "" || semester == "")) {
                                VCB.update_status('You must include a class name, ' +
                                        'a class number, and a semester.');
                                return false;
                            }
                        }

                        if (typeof cb === 'function') {
                            var message;

                            $.ajax({
                                type: "GET",
                                url: "create_class/",
                                async: true,
                                data: {
                                    'class_name': classname,
                                    'class_number': classnumber,
                                    'old_semester': semester,
                                    'new_semester': new_semester
                                },
                                success: function(result) {
                                    created = result['created']
                                    message = result['message']
                                    obj_bank = result['obj_bank_id']
                                    var new_code = result['code'];

                                    VCB.unblock_body();

                                    if (obj_bank != '') {
                                        if (new_semester === '') {
                                            actual_sem = semester;
                                        } else {
                                            actual_sem = new_semester
                                        }
                                        initialize_class(classname, obj_bank, message, actual_sem);

                                        return cb({
                                                'classname': classname,
                                                'classnumber': classnumber,
                                                'code': new_code,
                                                'obj_bank_id': obj_bank,
                                                'semester': actual_sem
                                        });
                                    } else {
                                        VCB.update_status(message);
                                        VCB.unblock_body();
                                        return false;
                                    }
                                },
                                error: function(xhr, status, error) {
                                    VCB.unblock_body();
                                    alert(error);
                                }
                            });
                        }
                    } else {
                        message = 'Congratulations, the class was' +
                                ' successfully loaded. Your access' +
                                ' code is: ' + code
                        VCB.unblock_body();
                        initialize_class(classname, obj_bank_id, message, semester);

                        return cb({
                                'classname': classname,
                                'classnumber': classnumber,
                                'code': code,
                                'obj_bank_id': obj_bank_id,
                                'semester': semester
                        });
                    }
                } else {
                    VCB.update_status('You must select or create a class, or cancel.');
                    return false;
                }
            };

            $(document).on('click', '#add_class', function() {
                // make two new input items

                if ($('#new_container').length) {
                    $('#new_container').remove();
                }

                var new_container = $('<div id="new_container"></div>')
                        .addClass('new_classes');
                var class_name_label = $('<label>Class Name: </label>');
                var class_name = $('<input id="class_name" type="text"' +
                        'required="required maxlength="150""></input>')
                        .addClass('input-block-level');
                var class_number_label = $('<label>Class Number (MIT): </label>');
                var class_number = $('<input id="class_number" type="text"' +
                        'required="required" maxlength="6"></input>')
                        .addClass('input-block-level');
                var semester_label = $('<label>Semester: </label>');
                var semester = $('<input id="semester" type="text"' +
                        'required="required" maxlength="100"></input>')
                        .addClass('input-block-level');
                var obj_bank_id = $('<input id="obj_bank_id" type="hidden"' +
                        'value=""></input>')
                        .data('obj-bank', '');
                var new_class = $('<input id="new_class" type="hidden"' +
                        'value="true"></input>');
                var access_code = $('<input id="access_code" type="hidden"' +
                        'value=""></input>');
                var new_semester = $('<input id="new_semester" type="hidden"' +
                        'value=""></input>');

                new_container.append(class_name_label);
                new_container.append(class_name);
                new_container.append(class_number_label);
                new_container.append(class_number);
                new_container.append(semester_label);
                new_container.append(semester);
                new_container.append(obj_bank_id);
                new_container.append(new_class);
                new_container.append(access_code);
                new_container.append(new_semester);
                class_container.append(new_container);
            });

            $(document).on('click', 'li.select-class', function() {
                if ($('#new_container').length) {
                    $('#new_container').remove();
                }

                var new_container = $('<div id="new_container"></div>')
                        .addClass('new_classes');
                var _this = $(this);
                var class_name_label = $('<label>Class Name: </label>');
                var class_name = $('<input id="class_name" type="text" value="' +
                        _this.data('name') + '" readonly></input>')
                        .addClass('input-block-level');
                var class_number = $('<input id="class_number" type="hidden"' +
                        'value=""></input>');
                var obj_bank_label = $('<label>MC3 Objective Bank ID: </label>');
                var obj_bank_id = $('<input id="obj_bank_id" type="textarea" readonly></input>')
                        .addClass('input-block-level')
                        .val(_this.data('obj-bank'))
                        .data('obj-bank', _this.data('obj-bank'));
                var semester_label = $('<label>Semester: </label>');
                var semester = $('<input id="semester" type="text"' +
                        'required="required" maxlength="100" readonly></input>')
                        .addClass('input-block-level')
                        .val(_this.data('semester'));
                var new_class = $('<input id="new_class" type="hidden"' +
                        'value="false"></input>');
                var access_code = $('<input id="access_code" type="hidden"' +
                        'value="' + _this.data('code') + '"></input>');
                var new_semester = $('<input id="new_semester" type="hidden"' +
                        'value=""></input>');
                var copy = $('<input id="copy" type="hidden"' +
                        'value="false"></input>');

                new_container.append(class_name_label);
                new_container.append(class_name);
                new_container.append(class_number);
                new_container.append(obj_bank_label);
                new_container.append(obj_bank_id);
                new_container.append(semester_label);
                new_container.append(semester);
                new_container.append(new_class);
                new_container.append(access_code);
                new_container.append(new_semester);
                new_container.append(copy);
                class_container.append(new_container);
            });

            $(document).on('click', 'li.select-semester', function() {
                if ($('#new_container').length) {
                    $('#new_container').remove();
                }

                var new_container = $('<div id="new_container"></div>')
                        .addClass('new_classes');
                var _this = $(this);
                var class_name_label = $('<label>Class Name: </label>');
                var class_name = $('<input id="class_name" type="text" value="' +
                        _this.data('name') + '" readonly></input>')
                        .addClass('input-block-level');
                var class_number = $('<input id="class_number" type="hidden"' +
                        'value="' + _this.data('number') + '"></input>');
                var obj_bank_label = $('<label>MC3 Objective Bank ID: </label>');
                var obj_bank_id = $('<input id="obj_bank_id" type="textarea" readonly></input>')
                        .addClass('input-block-level')
                        .val(_this.data('obj-bank'))
                        .data('obj-bank', _this.data('obj-bank'));
                var semester_label = $('<label>Source Semester: </label>');
                var semester_options = $('<select id="semester"' +
                        'required="required"></select>')
                        .addClass('input-block-level');
                var semester_array = _this.data('semesters').split(',');

                if ($.type(semester_array) === 'array') {
                    $.each(semester_array, function(index, semester) {
                        semester_options.append('<option>' + semester + '</option>');
                    });
                } else if ($.type(semester_array) === 'string') {
                    semester_options.append('<option>' + semester_array + '</option>');
                    semester_array = [semester_array];
                }
                var new_class = $('<input id="new_class" type="hidden"' +
                        'value="true"></input>');
                var access_code = $('<input id="access_code" type="hidden"' +
                        'value="' + _this.data('code') + '"></input>');
                var new_semester_label = $('<label>New Semester: </label>');
                var new_semester = $('<input id="new_semester" type="text"' +
                        'value="" required="required" maxlength=100></input>');
                var copy = $('<input id="copy" type="hidden"' +
                        'value="true"></input>');
                var semester_dom = $('<input id="semester_array" type="hidden"' +
                        'value="' + semester_array + '"></input>');

                new_container.append(class_name_label);
                new_container.append(class_name);
                new_container.append(class_number);
                new_container.append(obj_bank_label);
                new_container.append(obj_bank_id);
                new_container.append(semester_label);
                new_container.append(semester_options);
                new_container.append(new_class);
                new_container.append(access_code);
                new_container.append(new_semester_label);
                new_container.append(new_semester);
                new_container.append(copy);
                new_container.append(semester_dom);
                class_container.append(new_container);
            });

            var div = that.dialog(form, [{
                // first button (cancel)
                "label"   : labelCancel,
                "icon"    : _icons.CANCEL,
                "class"   : _btnClasses.CANCEL,
                "callback":  cancelCallback
            }, {
                // second button (confirm)
                "label"   : labelOk,
                "icon"    : _icons.CONFIRM,
                "class"   : _btnClasses.CONFIRM,
                "callback": confirmCallback
            }], {
                // prompts need a few extra options
                "header"  : header,
                // explicitly tell dialog NOT to show the dialog...
                "show"    : false,
                "onEscape": cancelCallback
            });

            // ... the reason the prompt needs to be hidden is because we need
            // to bind our own "shown" handler, after creating the modal but
            // before any show(n) events are triggered
            // @see https://github.com/makeusabrew/bootbox/issues/69

            div.on("shown", function() {
                form.find("input[id=classname]").focus();

                // ensure that submitting the form (e.g. with the enter key)
                // replicates the behaviour of a normal prompt()
                form.on("submit", function(e) {
                    e.preventDefault();
                    div.find(".btn-primary").click();
                });
            });

            div.modal("show");

            return div;
        };
    // end of custom select class prompt

    that.share = function(/*str, labelCancel, labelOk, cb, defaultVal*/) {
        var str         = "",
            labelCancel = _translate('CANCEL'),
            labelOk     = _translate('CONFIRM'),
            cb          = null,
            defaultVal  = "";

        switch (arguments.length) {
            case 1:
                str = arguments[0];
                break;
            case 2:
                str = arguments[0];
                if (typeof arguments[1] == 'function') {
                    cb = arguments[1];
                } else {
                    labelCancel = arguments[1];
                }
                break;
            case 3:
                str         = arguments[0];
                labelCancel = arguments[1];
                if (typeof arguments[2] == 'function') {
                    cb = arguments[2];
                } else {
                    labelOk = arguments[2];
                }
                break;
            case 4:
                str         = arguments[0];
                labelCancel = arguments[1];
                labelOk     = arguments[2];
                cb          = arguments[3];
                break;
            case 5:
                str         = arguments[0];
                labelCancel = arguments[1];
                labelOk     = arguments[2];
                cb          = arguments[3];
                defaultVal  = arguments[4];
                break;
            default:
                throw new Error("Incorrect number of arguments: expected 1-5");
        }

        var header = str;

        var wrapper = $("<div></div>");
        wrapper.append("<input class='input-block-level' autocomplete=off " +
                "readonly type=text value='" +
                VCB.get_share_link() + "' />");

        var cancelCallback = function() {
            if (typeof cb === 'function') {
                // yep, native prompts dismiss with null, whereas native
                // confirms dismiss with false...
                return cb(null);
            }
        };

        var confirmCallback = function() {
            if (typeof cb === 'function') {
                return cb(true);
            }
        };

        var div = that.dialog(wrapper, [{
            // first button (cancel)
            "label"   : labelCancel,
            "icon"    : _icons.CANCEL,
            "class"   : _btnClasses.CANCEL,
            "callback":  cancelCallback
        }, {
            // second button (confirm)
            "label"   : labelOk,
            "icon"    : _icons.CONFIRM,
            "class"   : _btnClasses.CONFIRM,
            "callback": confirmCallback
        }], {
            // prompts need a few extra options
            "header"  : header,
            // explicitly tell dialog NOT to show the dialog...
            "show"    : false,
            "onEscape": cancelCallback
        });

        // ... the reason the prompt needs to be hidden is because we need
        // to bind our own "shown" handler, after creating the modal but
        // before any show(n) events are triggered
        // @see https://github.com/makeusabrew/bootbox/issues/69

        div.on("shown.bs.modal", function() {

        });

        div.modal("show");

        return div;
    }; // End of custom share modal

    // custom XML file upload prompt
    that.xmlprompt = function(/*str, labelCancel, labelOk, cb, defaultVal*/) {
            var str         = "",
                labelCancel = _translate('CANCEL'),
                labelOk     = _translate('CONFIRM'),
                cb          = null,
                defaultVal  = "";

            switch (arguments.length) {
                case 1:
                    str = arguments[0];
                    break;
                case 2:
                    str         = arguments[0];
                    if (typeof arguments[1] == 'function') {
                        cb = arguments[1];
                    } else {
                        labelCancel = arguments[1];
                    }
                    break;
                case 3:
                    str			= arguments[0];
                    labelCancel = arguments[1];
                    if (typeof arguments[2] == 'function') {
                        cb 		= arguments[2];
                    } else {
                        labelOk = arguments[2];
                    }
                    break;
                case 4:
                    str         = arguments[0];
                    labelCancel = arguments[1];
                    labelOk     = arguments[2];
                    cb          = arguments[3];
                    break;
                case 5:
                    str         = arguments[0];
                    labelCancel = arguments[1];
                    labelOk     = arguments[2];
                    cb          = arguments[3];
                    defaultVal  = arguments[4];
                    break;
                default:
                    throw new Error("Incorrect number of arguments: expected 1-5");
            }

            var header = str;

            var container = $('<div></div>');
            var status_box = $('<div id="modal_status_box"></div>');

            var form = $('<form id="xml_form" name="xml_form"' +
                    'action="" method="POST" enctype="multipart/form-data"></form>');

            form.append('<label>XML File: </label>');
            form.append('<input class="input-block-level"' +
                    'autocomplete=off id="xml_file" name="xml_file" ' +
                    'type=file required="required" accept="text/xml*,application/xml*" />');

            form.append('<input class="input-block-level"' +
                    'id="process" name="process" type="button" value="Process XML"></input>');

            var results = $('<div id="modal_results"></div>');
            var table = $('<table id="results_table"></table>')
                          .addClass('table table-striped');
            var table_headers = $('<thead></thead>');
            var head_row = $('<tr></tr>');
            var offset_heading = $('<th></th>');
            offset_heading.text('Offset');
            var subject_heading = $('<th></th>');
            subject_heading.text('Video Subject');

            head_row.append(offset_heading);
            head_row.append(subject_heading);

            table_headers.append(head_row);
            var table_body = $('<tbody id="table_body"></tbody>');

            table.append(table_headers);
            table.append(table_body);

            results.append(table);

            container.append(status_box);
            container.append(form);
            container.append(results);

            var cancelCallback = function() {
                if (typeof cb === 'function') {
                    // yep, native prompts dismiss with null, whereas native
                    // confirms dismiss with false...
                    return cb(null);
                }
            };

            var confirmCallback = function() {
                if (typeof cb === 'function') {
                    var results = {
                            'message':'successfully processed the XML file!'
                    };
                    return cb(results);
                }
            };

            var div = that.dialog(container, [{
                // first button (cancel)
                "label"   : labelCancel,
                "icon"    : _icons.CANCEL,
                "class"   : _btnClasses.CANCEL,
                "callback":  cancelCallback
            }, {
                // second button (confirm)
                "label"   : labelOk,
                "icon"    : _icons.CONFIRM,
                "class"   : _btnClasses.CONFIRM,
                "callback": confirmCallback
            }], {
                // prompts need a few extra options
                "header"  : header,
                // explicitly tell dialog NOT to show the dialog...
                "show"    : false,
                "onEscape": cancelCallback
            });

            // ... the reason the prompt needs to be hidden is because we need
            // to bind our own "shown" handler, after creating the modal but
            // before any show(n) events are triggered
            // @see https://github.com/makeusabrew/bootbox/issues/69

            div.on("shown", function() {
                form.find("input[id=xml_file]").focus();

                $('#process').on('click', function() {
                    $('#table_body').remove();
                    var xml_file = document.getElementById('xml_file').files[0];
                    var reader = new FileReader();
                    reader.readAsText(xml_file);

                    reader.onload = function(event) {
                        var xml_contents = $(event.target.result);

                        var new_body = $('<tbody id="table_body"></tbody>')
                        table.append(new_body);

                        xml_contents.find('ProxyFrameRate').each(function() {
                            var frame_rate = $(this).text();
                            var start_offset = 0;
                            xml_contents.find('Memo').each(function() {
                                var offset = $(this).find('offset').text();
                                var subject = $(this).find('text').text();

                                if (subject == 'Start' || subject == 'OK') {
                                    start_offset = offset;
                                } else {
                                    // Minus an additional 4 seconds to account for
                                    // TA reaction time when using the recorder app
                                    offset = ((offset - start_offset) / frame_rate) - 4;

                                    var new_row = $('<tr></tr>');
                                    var offset_col = $('<td></td>');
                                    offset_col.text(VCB.convert_time(offset));
                                    var subject_col = $('<td></td>');
                                    subject_col.text(subject);

                                    new_row.append(offset_col);
                                    new_row.append(subject_col);

                                    new_body.append(new_row);
                                }
                            });
                        });
                    };
                });

//	             ensure that submitting the form (e.g. with the enter key)
//	             replicates the behaviour of a normal prompt()
//	            form.on("submit", function(e) {
//	                e.preventDefault();
//	                div.find(".btn-primary").click();
//	            });
            });

            div.modal("show");

            return div;
        };
    // end of custom XML upload prompt

    // custom prompt for managing class metadata like contacts and allow downloading
    that.management = function(/*str, labelCancel, labelOk, cb, defaultVal*/) {
        var str         = "",
            labelCancel = _translate('CANCEL'),
            labelOk     = _translate('CONFIRM'),
            cb          = null,
            defaultVal  = "";

        switch (arguments.length) {
            case 1:
                str = arguments[0];
                break;
            case 2:
                str = arguments[0];
                if (typeof arguments[1] == 'function') {
                    cb = arguments[1];
                } else {
                    labelCancel = arguments[1];
                }
                break;
            case 3:
                str         = arguments[0];
                labelCancel = arguments[1];
                if (typeof arguments[2] == 'function') {
                    cb = arguments[2];
                } else {
                    labelOk = arguments[2];
                }
                break;
            case 4:
                str         = arguments[0];
                labelCancel = arguments[1];
                labelOk     = arguments[2];
                cb          = arguments[3];
                break;
            case 5:
                str         = arguments[0];
                labelCancel = arguments[1];
                labelOk     = arguments[2];
                cb          = arguments[3];
                defaultVal  = arguments[4];
                break;
            default:
                throw new Error("Incorrect number of arguments: expected 1-5");
        }

        var header = str;

        var wrapper = $('<div></div>');
        var modal_status = $('<div></div>')
                .attr('addClass', 'status_box');
        wrapper.append(modal_status);
        VCB.append_management_checkbox(wrapper, 'download');
        VCB.append_management_checkbox(wrapper, 'sharing');
        VCB.append_management_checkbox(wrapper, 'transcripts');
        var table_wrapper = $('<div></div>')
                .addClass('control-group');
        wrapper.append(table_wrapper);

        var cancelCallback = function() {
            if (typeof cb === 'function') {
                if (DT.table_length('contacts_table') === 0 &&
                        VCB.metadata_contacts.length === 0) {
                    VCB.update_status('Please enter at least one contact.');
                    return false;
                } else {
                    // yep, native prompts dismiss with null, whereas native
                    // confirms dismiss with false...
                    return cb(null);
                }
            }
        };

        var confirmCallback = function() {
            if (typeof cb === 'function') {
                if (DT.table_length('contacts_table') === 0) {
                    VCB.update_status('Please enter at least one contact.');
                    return false;
                } else {
                    if (wrapper.find("input[name=download]").prop('checked')) {
                        VCB.metadata_download = true;
                    } else {
                        VCB.metadata_download = false;
                    }
                    if (wrapper.find("input[name=sharing]").prop('checked')) {
                        VCB.metadata_sharing = true;
                    } else {
                        VCB.metadata_sharing = false;
                    }
                    if (wrapper.find("input[name=transcripts]").prop('checked')) {
                        VCB.metadata_transcripts = true;
                    } else {
                        VCB.metadata_transcripts = false;
                    }
                    DT.get_table_data('contacts_table', function (contacts) {
                        VCB.metadata_contacts = contacts;
                        div.modal('hide');
                        return cb(true);
                    });
                }
            }
        };

        var div = that.dialog(wrapper, [{
            // first button (cancel)
            "label"   : labelCancel,
            "icon"    : _icons.CANCEL,
            "class"   : _btnClasses.CANCEL,
            "callback":  cancelCallback
        }, {
            // second button (confirm)
            "label"   : labelOk,
            "icon"    : _icons.CONFIRM,
            "class"   : _btnClasses.CONFIRM,
            "callback": confirmCallback
        }], {
            // prompts need a few extra options
            "header"  : header,
            // explicitly tell dialog NOT to show the dialog...
            "show"    : false,
            "onEscape": cancelCallback
        });

        // ... the reason the prompt needs to be hidden is because we need
        // to bind our own "shown" handler, after creating the modal but
        // before any show(n) events are triggered
        // @see https://github.com/makeusabrew/bootbox/issues/69

        div.on("shown", function() {
            wrapper.find("input[name=download]").focus();
            VCB.append_management_contacts(table_wrapper);
        });

        div.modal("show");

        return div;
    };


    that.dialog = function(str, handlers, options) {
        var buttons    = "",
            callbacks  = [];

        if (!options) {
            options = {};
        }

        // check for single object and convert to array if necessary
        if (typeof handlers === 'undefined') {
            handlers = [];
        } else if (typeof handlers.length == 'undefined') {
            handlers = [handlers];
        }

        var i = handlers.length;
        while (i--) {
            var label    = null,
                href     = null,
                _class   = null,
                icon     = '',
                callback = null;

            if (typeof handlers[i]['label']    == 'undefined' &&
                typeof handlers[i]['class']    == 'undefined' &&
                typeof handlers[i]['callback'] == 'undefined') {
                // if we've got nothing we expect, check for condensed format

                var propCount = 0,      // condensed will only match if this == 1
                    property  = null;   // save the last property we found

                // be nicer to count the properties without this, but don't think it's possible...
                for (var j in handlers[i]) {
                    property = j;
                    if (++propCount > 1) {
                        // forget it, too many properties
                        break;
                    }
                }

                if (propCount == 1 && typeof handlers[i][j] == 'function') {
                    // matches condensed format of label -> function
                    handlers[i]['label']    = property;
                    handlers[i]['callback'] = handlers[i][j];
                }
            }

            if (typeof handlers[i]['callback']== 'function') {
                callback = handlers[i]['callback'];
            }

            if (handlers[i]['class']) {
                _class = handlers[i]['class'];
            } else if (i == handlers.length -1 && handlers.length <= 2) {
                // always add a primary to the main option in a two-button dialog
                _class = 'btn-primary';
            }

            if (handlers[i]['link'] !== true) {
                _class = 'btn ' + _class;
            }

            if (handlers[i]['label']) {
                label = handlers[i]['label'];
            } else {
                label = "Option "+(i+1);
            }

            if (handlers[i]['icon']) {
                icon = "<i class='"+handlers[i]['icon']+"'></i> ";
            }

            if (handlers[i]['href']) {
                href = handlers[i]['href'];
            }
            else {
                href = _defaultHref;
            }

            buttons = "<a data-handler='"+i+"' class='"+_class+"' href='" + href + "'>"+icon+""+label+"</a>" + buttons;

            callbacks[i] = callback;
        }

        // @see https://github.com/makeusabrew/bootbox/issues/46#issuecomment-8235302
        // and https://github.com/twitter/bootstrap/issues/4474
        // for an explanation of the inline overflow: hidden
        // @see https://github.com/twitter/bootstrap/issues/4854
        // for an explanation of tabIndex=-1

        var parts = ["<div class='bootbox modal' tabindex='-1' style='overflow:hidden;'>"];

        if (options['header']) {
            var closeButton = '';
            if (typeof options['headerCloseButton'] == 'undefined' || options['headerCloseButton']) {
                closeButton = "<a href='"+_defaultHref+"' class='close'>&times;</a>";
            }

            parts.push("<div class='modal-header'>"+closeButton+"<h3>"+options['header']+"</h3></div>");
        }

        // push an empty body into which we'll inject the proper content later
        parts.push("<div class='modal-body'></div>");

        if (buttons) {
            parts.push("<div class='modal-footer'>"+buttons+"</div>");
        }

        parts.push("</div>");

        var div = $(parts.join("\n"));

        // check whether we should fade in/out
        var shouldFade = (typeof options.animate === 'undefined') ? _animate : options.animate;

        if (shouldFade) {
            div.addClass("fade");
        }

        var optionalClasses = (typeof options.classes === 'undefined') ? _classes : options.classes;
        if (optionalClasses) {
            div.addClass(optionalClasses);
        }

        // now we've built up the div properly we can inject the content whether it was a string or a jQuery object
        div.find(".modal-body").html(str);

        function onCancel(source) {
            // for now source is unused, but it will be in future
            var hideModal = null;
            if (typeof options.onEscape === 'function') {
                // @see https://github.com/makeusabrew/bootbox/issues/91
                hideModal = options.onEscape();
            }

            if (hideModal !== false) {
                div.modal('hide');
            }
        }

        // hook into the modal's keyup trigger to check for the escape key
        div.on('keyup.dismiss.modal', function(e) {
            // any truthy value passed to onEscape will dismiss the dialog
            // as long as the onEscape function (if defined) doesn't prevent it
            if (e.which === 27 && options.onEscape) {
                onCancel('escape');
            }
        });

        // handle close buttons too
        div.on('click', 'a.close', function(e) {
            e.preventDefault();
            onCancel('close');
        });

        // well, *if* we have a primary - give the first dom element focus
        div.on('shown', function() {
            div.find("a.btn-primary:first").focus();

        });

        $(document).on('click', '.modal-backdrop', function() {
            div.modal('hide');
        });

        div.on('hidden', function(e) {
            // @see https://github.com/makeusabrew/bootbox/issues/115
            // allow for the fact hidden events can propagate up from
            // child elements like tooltips
            if (e.target === this) {
                div.remove();
            }
        });

        // wire up button handlers
        div.on('click', '.modal-footer a', function(e) {

            var handler   = $(this).data("handler"),
                cb        = callbacks[handler],
                hideModal = null;

            // sort of @see https://github.com/makeusabrew/bootbox/pull/68 - heavily adapted
            // if we've got a custom href attribute, all bets are off
            if (typeof handler                   !== 'undefined' &&
                typeof handlers[handler]['href'] !== 'undefined') {

                return;
            }

            e.preventDefault();

            if (typeof cb === 'function') {
                hideModal = cb(e);
            }

            // the only way hideModal *will* be false is if a callback exists and
            // returns it as a value. in those situations, don't hide the dialog
            // @see https://github.com/makeusabrew/bootbox/pull/25
            if (hideModal !== false) {
                div.modal("hide");
            }
        });

        // stick the modal right at the bottom of the main body out of the way
        $("body").append(div);

        div.modal({
            // unless explicitly overridden take whatever our default backdrop value is
            backdrop : (typeof options.backdrop  === 'undefined') ? _backdrop : options.backdrop,
            // ignore bootstrap's keyboard options; we'll handle this ourselves (more fine-grained control)
            keyboard : false,
            // @ see https://github.com/makeusabrew/bootbox/issues/69
            // we *never* want the modal to be shown before we can bind stuff to it
            // this method can also take a 'show' option, but we'll only use that
            // later if we need to
            show     : false
        });

        // @see https://github.com/makeusabrew/bootbox/issues/64
        // @see https://github.com/makeusabrew/bootbox/issues/60
        // ...caused by...
        // @see https://github.com/twitter/bootstrap/issues/4781
        div.on("show", function(e) {
            $(document).off("focusin.modal");
        });

        if (typeof options.show === 'undefined' || options.show === true) {
            div.modal("show");
        }


        return div;
    };

    /**
     * #modal is deprecated in v3; it can still be used but no guarantees are
     * made - have never been truly convinced of its merit but perhaps just
     * needs a tidyup and some TLC
     */
    that.modal = function(/*str, label, options*/) {
        var str;
        var label;
        var options;

        var defaultOptions = {
            "onEscape": null,
            "keyboard": true,
            "backdrop": _backdrop
        };

        switch (arguments.length) {
            case 1:
                str = arguments[0];
                break;
            case 2:
                str = arguments[0];
                if (typeof arguments[1] == 'object') {
                    options = arguments[1];
                } else {
                    label = arguments[1];
                }
                break;
            case 3:
                str     = arguments[0];
                label   = arguments[1];
                options = arguments[2];
                break;
            default:
                throw new Error("Incorrect number of arguments: expected 1-3");
        }

        defaultOptions['header'] = label;

        if (typeof options == 'object') {
            options = $.extend(defaultOptions, options);
        } else {
            options = defaultOptions;
        }

        return that.dialog(str, [], options);
    };


    that.hideAll = function() {
        $(".bootbox").modal("hide");
    };

    that.animate = function(animate) {
        _animate = animate;
    };

    that.backdrop = function(backdrop) {
        _backdrop = backdrop;
    };

    that.classes = function(classes) {
        _classes = classes;
    };

    /**
     * private API
     */

    /**
     * standard locales. Please add more according to ISO 639-1 standard. Multiple language variants are
     * unlikely to be required. If this gets too large it can be split out into separate JS files.
     */
    var _locales = {
        'br' : {
            OK      : 'OK',
            CANCEL  : 'Cancelar',
            CONFIRM : 'Sim'
        },
        'da' : {
            OK      : 'OK',
            CANCEL  : 'Annuller',
            CONFIRM : 'Accepter'
        },
        'de' : {
            OK      : 'OK',
            CANCEL  : 'Abbrechen',
            CONFIRM : 'Akzeptieren'
        },
        'en' : {
            OK      : 'OK',
            CANCEL  : 'Cancel',
            CONFIRM : 'OK'
        },
        'es' : {
            OK      : 'OK',
            CANCEL  : 'Cancelar',
            CONFIRM : 'Aceptar'
        },
        'fr' : {
            OK      : 'OK',
            CANCEL  : 'Annuler',
            CONFIRM : 'D\'accord'
        },
        'it' : {
            OK      : 'OK',
            CANCEL  : 'Annulla',
            CONFIRM : 'Conferma'
        },
        'nl' : {
            OK      : 'OK',
            CANCEL  : 'Annuleren',
            CONFIRM : 'Accepteren'
        },
        'pl' : {
            OK      : 'OK',
            CANCEL  : 'Anuluj',
            CONFIRM : 'Potwierdź'
        },
        'ru' : {
            OK      : 'OK',
            CANCEL  : 'Отмена',
            CONFIRM : 'Применить'
        },
        'zh_CN' : {
            OK      : 'OK',
            CANCEL  : '取消',
            CONFIRM : '确认'
        },
        'zh_TW' : {
            OK      : 'OK',
            CANCEL  : '取消',
            CONFIRM : '確認'
        }
    };

    function _translate(str, locale) {
        // we assume if no target locale is probided then we should take it from current setting
        if (typeof locale === 'undefined') {
            locale = _locale;
        }
        if (typeof _locales[locale][str] === 'string') {
            return _locales[locale][str];
        }

        // if we couldn't find a lookup then try and fallback to a default translation

        if (locale != _defaultLocale) {
            return _translate(str, _defaultLocale);
        }

        // if we can't do anything then bail out with whatever string was passed in - last resort
        return str;
    }

    return that;

}(document, window.jQuery));

// @see https://github.com/makeusabrew/bootbox/issues/71
window.bootbox = bootbox;
