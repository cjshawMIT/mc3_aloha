var DT = (function (window, document, $, dt, undefined) {
    dt.add_row_to_table = function (id, data) {
        var handle = dt.get_table_handle(id);
        var counter = VCB.length(data);
        if (counter > 0) {
            var newrow = [];
            $.each(data, function (key, value) {
                newrow.push(value);
                if (--counter === 0) {
                    handle.fnAddData(newrow);
                }
            });
        }
    };

    dt.construct_table = function (table, data, wrapper, template) {
        var table_head = $('<thead></thead>');
        var head_row = $('<tr></tr>');
        $.each(template, function(header, field) {
            var new_header = $('<th></th>')
                               .addClass('text-center')
                               .text(header);
            if ($.type(field) === 'object') {
                new_header.addClass('no_sort');
            }

            head_row.append(new_header);
        });
        var table_body = $('<tbody></tbody>');
        table_head.append(head_row);
        table.append(table_head);
        table.append(table_body);

        var data_counter = data.length;
        if (data_counter > 0) {
            $.each(data, function(index, obj) {
                var new_row = $('<tr></tr>');
                var field_counter = Object.keys(template).length;
                $.each(template, function(header, field) {
                    if ($.type(field) === 'object') {
                        var new_col = field.clone();
                    } else {
                        var new_col = $('<td></td>');
                        if (field === 'name') {
                            var col_span = $('<span></span>')
                                    .addClass('pointer')
                                    .data('id', obj['id'])
                                    .text(obj[field]);
                            new_col.addClass('name_col')
                                   .append(col_span);
                        } else {
                            var col_span = $('<span></span>')
                                             .text(obj[field]);
                            new_col.append(col_span);
                        }
                    }
                    new_row.append(new_col);
                    if (--field_counter === 0) {
                        table_body.append(new_row);
                    }
                });
                if (--data_counter === 0) {
                    wrapper.empty()
                           .append(table);
                    dt.init_table(table.attr('id'));
                }
            });
        } else {
            wrapper.empty()
                .append(table);
            dt.init_table(table.attr('id'));
        }
    };

    dt.delete_row = function (id, row) {
        var handle = dt.get_table_handle(id);
        handle.fnDeleteRow(row);
    };

    dt.get_element_row = function (ele, handle) {
        // http://stackoverflow.com/questions/7503306/jquery-datatables-how-to-get-row-index-or-nnode-by-row-id-of-tr
        return handle.fnGetPosition(ele.parent()
                .parent()[0]);
    };

    dt.get_resource_text = function (box_ele) {
        var rtext = box_ele.parent()
                .parent()
                .children('.name_col')
                .children('span')
                .data('resource_text');
        return rtext;
    };

    dt.get_table_data = function (id, _callback) {
        var handle = dt.get_table_handle(id);
        var raw_data = handle.fnGetData();
        var counter = raw_data.length;
        var clean_data = [];
        if (counter > 0) {
            $.each(raw_data, function (index, entry) {
                if ($(entry[1]).length === 0) {
                    // don't convert to HTML objects
                    var tmp = {
                        'fname': entry[1],
                        'lname': entry[2],
                        'email': entry[3],
                        'role': entry[4]
                    };
                } else {
                    var tmp = {
                        'fname': $(entry[1]).text(),
                        'lname': $(entry[2]).text(),
                        'email': $(entry[3]).text(),
                        'role': $(entry[4]).text()
                    };
                }
                clean_data.push(tmp);
                if (--counter === 0) {
                    _callback(clean_data);
                }
            });
        } else {
            _callback(clean_data);
        }
    };

    dt.get_table_handle = function (id) {
        return $('#' + id).dataTable();
    };

    dt.get_table_row_bank = function (ele) {
        'use strict';
        return $(ele).parent()
                .parent()
                .children('.name_col')
                .children('span')
                .data('bank');
    };

    dt.get_table_row_id = function (ele) {
        'use strict';
        return $(ele).parent()
                .parent()
                .children('.name_col')
                .children('span')
                .data('id');
    };

    dt.get_table_row_ids = function (ele, callback) {
        'use strict';
        if ($.type(ele) === 'object') {
            var return_val = [];
            var counter = ele.length;
            $.each(ele, function(index, el) {
                return_val.push(get_table_row_id($(el)));
                if (--counter === 0) {
                    callback(return_val);
                }
            });
        } else {
            callback(get_table_row_id(ele));
        }
    };

    dt.init_table = function (id) {
        'use strict';

        var handle = '';

        var dont_sort = [];
        $('#' + id + ' thead th').each(function() {
            if ($(this).hasClass('no_sort')) {
                dont_sort.push({'bSortable':false});
            } else {
                dont_sort.push(null);
            }
        });

        handle = $('#' + id).dataTable({
            'sPaginationType': 'full_numbers',
            'bJQueryUI': true,
            'aoColumns': dont_sort
        });
        return handle;
    };

    dt.table_length = function (id) {
        var handle = $('#' + id).dataTable();
        return handle.fnSettings().fnRecordsTotal();
    };

    return dt;
})(this, document, jQuery, DT || {});