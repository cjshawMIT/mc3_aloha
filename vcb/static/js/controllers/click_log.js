var VCB = (function (window, document, $, vcb, undefined) {
    vcb.append_staff_checkbox = function (parent) {
        var box = $('<span></span>')
                 .append('Include Staff: ')
                 .append('<input type="checkbox" name="include_staff"/>')
                 .attr('id', 'include_staff');
        parent.append(box);
    };

    vcb.click_log_callback = function (response) {
        success = response['success'];
        if (success) {
            var log_data = response['data'];
            var log_table = $('<table></table>')
                              .attr('id', 'log_table');
            var wrapper = $('#log_div');
            var template = {
                'Username': 'username',
                'Objective': 'obj',
                'Tag Clicked': 'tag',
                'Timestamp': 'timetag'
            };

            DT.construct_table(log_table, log_data, wrapper, template);
        } else {
            alert('Error in retrieving class log data.');
        }
    };

    vcb.generate_clicklog = function (id, download, include_staff) {
        $('#log_div').empty();
        $.ajax({
            url: 'clickLog/',
            type: 'GET',
            data: {
                'id': id,
                'download': download,
                'include_staff': include_staff
            }
        }).fail( function(xhr, status, error) {
            VCB.update_status('Server Error: ' + status);
        }).done( function(response) {
            VCB.click_log_callback(response);
        }).always( function(xhr, status) {

        });
    };

    vcb.initialize_nav_class_selector = function (id) {
        $('#' + id).select2({
            placeholder: 'Select Class',
            id: function(select_class) {return select_class.local_id;},
            ajax: {
                url: 'user_classes/',
                dataType: 'json',
                data: function (term, page) {
                    search_term = term.toLowerCase();
                    return {
                        q: term,
                        page: page
                    };
                },
                results: function(data) {
                    var counter = data.length;
                    if (counter > 0) {
                        var filtered_classes = [];
                        $.each(data, function(index, select_class) {
                            var class_name = select_class.metadata.class_name + ', ' +
                                    select_class.metadata.semester;
                            class_name = class_name.toLowerCase();

                            if (class_name.indexOf(search_term) >= 0) {
                                filtered_classes.push(select_class);
                            }
                        });
                        return {results: filtered_classes};
                    } else {
                        var tmp = [{
                            'local_id': null,
                            'metadata': {
                                'class_number': null,
                                'class_name': 'None',
                                'semester': ' Found'
                            }
                        }];
                        return {results: tmp};
                    }
                }
            },
            formatResult: function(select_class) {
                return '<span class="mit_classnum" style="display: none;">' +
                        select_class.metadata.class_number + ' - </span> ' +
                        select_class.metadata.class_name + ', ' +
                        select_class.metadata.semester;
            },
            formatSelection: function(select_class) {
                return select_class.metadata.class_name + ', ' +
                        select_class.metadata.semester;
            },
            escapeMarkup: function(m) {
                return m;
            }
        });

        // From:
        // http://stackoverflow.com/questions/16966002/select2-plugin-works-fine-when-not-inside-a-jquery-modal-dialog/18386569#18386569
        $.ui.dialog.prototype._allowInteraction = function(e) {
            return !!$(e.target).closest('.ui-dialog, .ui-datepicker, .select2-drop').length;
        };
    };

    return vcb;
})(this, document, jQuery, VCB || {});