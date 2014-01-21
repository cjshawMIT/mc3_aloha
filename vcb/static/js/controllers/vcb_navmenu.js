var VCB = (function (window, document, $, vcb, undefined) {
    vcb.append_class_selector = function (parent, sel_id) {
        var class_menu = $('<input />')
                   .attr('type', 'hidden')
                   .attr('id', sel_id);
        parent.append(class_menu);
    };

    vcb.append_div = function (parent, id) {
        var div = $('<div></div>')
                .addClass('row')
                .addClass('reset_left')
                .attr('id', id)
                .show();
        parent.append(div);
        return div;
    };

    vcb.append_download_button = function (parent) {
        var download = $('<span></span>')
                 .append('Download log: ')
                 .append('<i class="fa fa-download"></i>')
                 .attr('id', 'download_log');
        parent.append(download);
    };

    vcb.clear_admin_class_data = function () {
        vcb.admin_classname = '';
        vcb.admin_semester = '';
    };

    vcb.create_modal = function (wrapper, title) {
        var target = $('.navbar');

        wrapper.dialog({
            width: 800,
            height: 600,
            modal: true,
            closeText: 'close',
            title: title,
            collision: 'none',
            close: function(event, ui) {
                $(this).dialog('destroy').remove();
                VCB.unblock_nav();
            },
            buttons: [{
                text: 'Close',
                click: function() {
                    $(this).dialog('close');
                }
            }]
        }).dialog('widget')
          .position({
            my: 'top',
            at: 'bottom',
            of: target
        });
        VCB.bind_dialog_close_events();
    };

    vcb.get_active_class = function () {
        var data = $('#class_selector').select2('data');
        return {
            'class_name': data.metadata.class_name,
            'semester': data.metadata.semester
        };
    };

    vcb.get_admin_class = function() {
        return {
            'class_name': vcb.admin_classname,
            'semester': vcb.admin_semester
        }
    }

    vcb.get_control_type = function() {
        return $('#control_type').val();
    }

    vcb.initialize_class_metadata = function (data) {
        // Do Ajax call with the data
        // Should return the metadata:
        //    e-mail contacts, share, download
        // If the metadata is empty,
        //   open a modal that requests the info
        var params = {
            'data': data,
            'url': 'class_management/'
        };

        function populate_metadata (results) {
            var contacts = results['contacts'];

            if (results['allow_download']) {
                vcb.metadata_download = true;
            } else {
                vcb.metadata_download = false;
            }
            if (results['allow_sharing']) {
                vcb.metadata_sharing = true;
            } else {
                vcb.metadata_sharing = false;
            }
            if (results['allow_transcripts']) {
                vcb.metadata_transcripts = true;
            } else {
                vcb.metadata_transcripts = false;
            }

            if (contacts.length === 0) {
                vcb.metadata_contacts = [];
                vcb.open_class_management_modal();
            } else {
                vcb.metadata_contacts = contacts;
            }
        }

        vcb.send_ajax(params, populate_metadata, null, null);
    };

    vcb.set_admin_class_data = function (classname, semester) {
        vcb.admin_classname = classname;
        vcb.admin_semester = semester;
    };

    return vcb;
})(this, document, jQuery, VCB || {});