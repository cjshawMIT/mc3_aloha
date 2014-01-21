var VCB = (function (window, document, $, vcb, undefined) {
    'use strict';
    vcb.append_auto_tag = function (form, topic) {
        var wrapper = $('<div></div>')
                .attr('id', 'auto_tag_wrapper')
                .append('<input name="subject[]" type="hidden"' +
                'value="Start of ' + topic + '"></input>')
                .append('<input name="timetag[]" type="hidden"' +
                'value="00:00:01" step="1"></input>')
                .append('<input type="button" id="enter_tags" name="enter_tags"' +
                'value="Enter Tags (optional)" />');
        form.append(wrapper);
    };

    vcb.append_management_checkbox = function (parent, type) {
        var group = $('<div></div>')
                .addClass('control-group');
        var label = $('<label></label>')
                .addClass('control-label')
                .text('Allow ' + type + ': ');
        var input = $('<input />')
                .addClass('controls')
                .attr('type', 'checkbox')
                .attr('name', type);
        if ((type === 'download' && vcb.metadata_download) ||
                (type === 'sharing' && vcb.metadata_sharing) ||
                (type === 'transcripts' && vcb.metadata_transcripts)) {
            input.attr('checked', true);
        }
        group.append(label);
        group.append(input);
        parent.append(group);
    };

    vcb.append_management_contacts = function (parent) {
        var label = $('<label></label>')
                .addClass('control-label')
                .text('Course Contacts (please have at least one):')
                .insertBefore(parent);
        vcb.insert_add_contact(parent);

        var data = vcb.metadata_contacts;
        var table = $('<table></table>')
                .attr('id', 'contacts_table');
        var del = $('<td></td>')
                .html(vcb.delete_contact_html());
        var template = {
            'Delete': del,
            'First Name': 'fname',
            'Last Name': 'lname',
            'E-mail': 'email',
            'Role': 'role'
        };
        DT.construct_table(table, data, parent, template);
    };

    vcb.append_timetag_fields = function (form) {
        form.append('<label>Populate Timetags with XML File: </label>');
        form.append('<input class="input-block-level"' +
                'autocomplete=off id="xml_file" name="xml_file" ' +
                'type=file required="required" accept="text/xml*,application/xml*" />');

        form.append('<input class="input-block-level"' +
                'id="process" name="process" type="button" value="Process XML"></input>');

        var timetag_table = $('<table></table>')
                .attr('id', 'timetag_table');
        var timetag_head = $('<thead></thead>');
        var header_row = $('<tr></tr>');
        var delete_heading = $('<th></th>');
        var subject_heading = $('<th></th>');
        subject_heading.text('Video Timetag Description');
        var timestamp_heading = $('<th></th>');
        timestamp_heading.text('Video Timetag (hh:mm:ss)');
        header_row.append(delete_heading);
        header_row.append(subject_heading);
        header_row.append(timestamp_heading);
        timetag_head.append(header_row);

        var timetag_body = $('<tbody id="table_body"></tbody>');
        var body_row = $('<tr></tr>').addClass('timetag-row');
        var delete_icon = $('<td></td>')
                            .addClass('timetag_del');
        delete_icon.html('<i class="fa fa-times-circle"></i>');
        var subject_input = $('<td></td>');
        subject_input.html('<input name="subject[]" type="text"' +
                'autocomplete=off></input>');
        var timetag_input = $('<td></td>');
        timetag_input.html('<input name="timetag[]" type="time"' +
                'autocomplete=off value="00:00:01" step="1"></input>');
        body_row.append(delete_icon);
        body_row.append(subject_input);
        body_row.append(timetag_input);
        timetag_body.append(body_row);

        timetag_table.append(timetag_head);
        timetag_table.append(timetag_body);

        form.append(timetag_table);
        form.append('<input type="button" id="add-row" name="add-row"' +
                'value="Add Row" />');
    };

    vcb.close_admin_div = function () {
        $('#admin_div').fadeOut(1000, function() { $(this).remove(); });
        $('#viewer_container').fadeIn(600, function() { $(this).show(); });
        $('#vid_search').fadeIn(600, function() { $(this).show(); });
        vcb.show_main_status_box();
        vcb.clear_admin_class_data();
        vcb.unblock_nav();
        lscache.flush();
        vcb.initialize_class_selector();
        vcb.open_selected_class_topic_tree();
    };

    vcb.delete_contact_html = function () {
        return '<i class="fa fa-times pointer delete_contact"></i>';
    };

    vcb.get_new_contact_details = function () {
        var data = {
            'delete': vcb.delete_contact_html(),
            'fname': $('input[name=fname]').val(),
            'lname': $('input[name=lname]').val(),
            'email': $('input[name=email]').val(),
            'role': $('input[name=role]').val()
        };
        return data;
    };

    // ================
    // These functions are for the Admin / Create Class menu
    vcb.initialize_canvas = function (class_name, semester, obj_bank_id) {
        vcb.block_page('Loading the course.');
        var container = '#admin_canvas';
        var tree_target = '#admin_canvas_content';

        // get current class tree, if it exists
        // if the class tree doesn't exist, create it
        // draw the class tree

        // Always draw from scratch
        var storage_check_name = 'topic_' + class_name + semester;

        lscache.set('obj_bank_id', obj_bank_id, 1440);

        $.ajax({
            type: "GET",
            url: "drawtree/",
            data: {
                'tree-type': 'topics',
                'class-name': class_name,
                'semester': semester,
                'get_all': true
            },
            success: function(tree_data) {
                lscache.set(storage_check_name, tree_data, 1440);
                var tree = tree_data[0];
                var wrapper = $('<div></div>');
                var main_list = $('<ol></ol>')
                                  .attr('id', 'admin_list')
                                  .addClass('sortable');

                var root = $('<li></li>')
                             .addClass('mjs-nestedSortable-branch')
                             .addClass('mjs-nestedSortable-expanded');
                var root_heading = $('<div></div>')
                                    .addClass('menu_heading')
                                    .addClass(tree['item_class'])
                                    .addClass('context-menu-tree')
                                    .data('item_class', tree['item_class'])
                                    .data('source', tree['source']);
                var toggle = $('<span></span>')
                               .addClass('disclose');
                toggle.append('<i class="fa fa-minus"></i>');

                var heading_text = $('<p></p>')
                                     .addClass('heading_text');
                heading_text.text(tree['name']);

                root_heading.append(toggle);
                root_heading.append(heading_text);
                root.append(root_heading);
                main_list.append(root);
                var children = tree['children'];

                function add_children(children, parent_list) {
                    if (children.length > 0) {
                        var child_list = $('<ol></ol>');
                        parent_list.append(child_list);
                        $.each(children, function(index, child) {
                            var item_class = child['item_class'];
                            if (item_class === 'objective') {
                                var child_element = $('<li></li>')
                                                      .addClass('mjs-nestedSortable-branch')
                                                      .addClass('mjs-nestedSortable-collapsed');
                                var child_heading = $('<div></div>')
                                                      .addClass('menu_heading')
                                                      .addClass(child['item_class'])
                                                      .addClass('context-menu-tree')
                                                      .data('item_class', child['item_class'])
                                                      .data('source', child['source'])
                                                      .data('id', child['item_id'])
                                                      .data('bank', child['bank']);
                                var toggle = $('<span></span>')
                                               .addClass('disclose');
                                toggle.append('<i class="fa fa-plus"></i>');

                                var remove = $('<span></span>')
                                                .addClass('pull-right remove');
                                remove.append('<i class="fa fa-times"></i>');

                                var heading_text = $('<p></p>')
                                                     .addClass('heading_text');
                                heading_text.text(child['fullname']);
                                heading_text.attr('contenteditable','true');

                                var grandchildren = child['children'];
                                if (typeof grandchildren !== 'undefined') {
                                    if (grandchildren.length > 0) {

                                        child_heading.append(toggle);
                                        child_heading.append(heading_text);
                                        child_heading.append(remove);
                                        child_element.append(child_heading);
                                        child_list.append(child_element);

                                        add_children(grandchildren, child_element);
                                    } else {
                                        var grandchild_list = $('<ol></ol>');

                                        child_heading.append(toggle);
                                        child_heading.append(heading_text);
                                        child_heading.append(remove);
                                        child_element.append(child_heading);
                                        child_element.append(grandchild_list);

                                        child_list.append(child_element);
                                    }
                                }
                            } else if (item_class === 'asset') {
                                var child_element = $('<li></li>');
                                try {
                                    var child_url = child['urls'][0]['url'];
                                } catch (e) {
                                    var child_url = '';
                                }
                                var child_heading = $('<div></div>')
                                                      .addClass('asset')
                                                      .addClass('menu_heading')
                                                      .addClass('context-menu-asset')
                                                      .addClass(child['item_class'])
                                                      .data('source', child['source'])
                                                      .data('item_class', 'asset')
                                                      .data('recorddate', child['rec_date'])
                                                      .data('pubdate', '')
                                                      .data('url', child_url)
                                                      .data('timetag', child['timestamp'])
                                                      .data('session', '')
                                                      .data('id', child['item_id'])
                                                      .data('bank', child['bank']);
                                var toggle = $('<span></span>')
                                               .addClass('disclose');
                                toggle.append('<i class="fa fa-move"></i>');

                                var remove = $('<span></span>')
                                                .addClass('pull-right remove');
                                remove.append('<i class="fa fa-times"></i>');

                                var heading_text = $('<p></p>')
                                                     .addClass('heading_text');
                                heading_text.text(child['fullname']);
                                heading_text.attr('contenteditable','true');

                                child_heading.append(toggle);
                                child_heading.append(heading_text);
                                child_heading.append(remove);
                                child_element.append(child_heading);
                                child_list.append(child_element);
                            }
                        });
                    }
                }

                if (typeof(children) !== 'undefined') {
                    if (children.length > 0) {
                        add_children(children, root);
                    } else {
                        var child_list = $('<ol></ol>');
                        root.append(child_list);
                    }
                } else {
                    var child_list = $('<ol></ol>');
                    root.append(child_list);
                }

                wrapper.append(main_list);
                $(tree_target).append(wrapper);

                $('ol.sortable').nestedSortable({
                    forcePlaceholderSize: true,
                    handle: 'span.disclose',
                    helper: 'clone',
                    items: 'li',
                    opacity: .6,
                    placeholder: 'placeholder',
                    revert: 250,
                    tabSize: 25,
                    tolerance: 'pointer',
                    toleranceElement: '> div',
                    isTree: true,
                    expandOnHover: 700,
                    startCollapsed: true,
                    protectRoot: true,
                    stop: function(e, ui) {
                        lscache.set('canvas_clean', false);
                    }
                });
                lscache.set('canvas_clean', 'true', 1440);
            },
            error: function(xhr, status, error) {
                alert(error);
            },
            complete: function() {
                vcb.unblock_body();
            }
        });
    };

    vcb.insert_add_contact = function (parent) {
        var add_new = $('<div></div>')
                .addClass('btn')
                .addClass('btn-primary')
                .addClass('add_contact')
                .html('<i class="fa fa-plus"></i> Add new contact')
                .insertBefore(parent);
        var save = $('<div></div>')
                .addClass('btn')
                .addClass('btn-success')
                .addClass('save_contact')
                .addClass('pull-right')
                .html('<i class="fa fa-save"></i> Save contact')
                .insertBefore(parent)
                .hide();
        var new_row = $('<form></form>')
                .attr('id', 'contacts_form')
                .insertBefore(parent)
                .hide();
        vcb.insert_text_field(new_row, 'First Name', 'fname');
        vcb.insert_text_field(new_row, 'Last Name', 'lname');
        vcb.insert_text_field(new_row, 'E-mail', 'email');
        vcb.insert_text_field(new_row, 'Role', 'role');
    };

    vcb.insert_text_field = function (parent, label, name) {
        var field = $('<input />')
                .attr('type', 'text')
                .attr('name', name)
                .attr('placeholder', label);
        parent.append(field)
    };

    vcb.init_timetag_entry = function () {
        var row = $('.timetag-row').clone();
        var button = $('#add-row');
        button.on('click', function() {
            $('#table_body').append(row.clone());
        });

        $(document).on('click', '.fa-times-circle', function() {
            $(this).parent().parent().remove();
        });

        $('#process').on('click', function() {
            $('#table_body').remove();
            var xml_file = document.getElementById('xml_file').files[0];
            var reader = new FileReader();
            reader.readAsText(xml_file);

            reader.onload = function(event) {
                var xml_contents = $(event.target.result);
                var timetag_table = $('#timetag_table');
                var timetag_body = $('<tbody id="table_body"></tbody>');
                timetag_table.append(timetag_body);

                xml_contents.find('ProxyFrameRate').each(function() {
                    var frame_rate = $(this).text();
                    var start_offset = 0;
                    var row = 0;
                    xml_contents.find('Memo').each(function() {
                        var offset = $(this).find('offset').text();
                        var subject = $(this).find('text').text();

                        if (subject == 'Start' || subject == 'OK') {
                            start_offset = offset;
                            var body_row = $('<tr></tr>')
                                             .addClass('timetag-row');
                            var delete_icon = $('<td></td>')
                                                .addClass('timetag_del');
                            delete_icon.html('<i class="fa fa-times-circle"></i>');
                            var subject_input = $('<td></td>');
                            subject_input.html('<input name="subject[]" type="text"' +
                                    'id="sub_row' + row + '" autocomplete=off></input>');
                            var timetag_input = $('<td></td>');
                            timetag_input.html('<input name="timetag[]" type="time"' +
                                    'id="tag_row' + row + '" autocomplete=off ' +
                                    'value="00:00:01" step="1"></input>');
                            body_row.append(delete_icon);
                            body_row.append(subject_input);
                            body_row.append(timetag_input);
                            timetag_body.append(body_row);
                        } else {
                            // Minus an additional 4 seconds to account for
                            // TA reaction time when using the recorder app
                            offset = ((offset - start_offset) / frame_rate) - 4;

                            $('#sub_row' + row).val(subject);
                            $('#tag_row' + row).val(VCB.convert_time(offset));

                            row += 1;
                            var body_row = $('<tr></tr>');
                            var delete_icon = $('<td></td>')
                                                .addClass('timetag_del');
                            delete_icon.html('<i class="fa fa-times-circle"></i>');
                            var subject_input = $('<td></td>');
                            subject_input.html('<input name="subject[]" type="text"' +
                                    'id="sub_row' + row + '" autocomplete=off></input>');
                            var timetag_input = $('<td></td>');
                            timetag_input.html('<input name="timetag[]" type="time"' +
                                    'id="tag_row' + row + '" autocomplete=off ' +
                                    'value="00:00:01" step="1"></input>');
                            body_row.append(delete_icon);
                            body_row.append(subject_input);
                            body_row.append(timetag_input);
                            timetag_body.append(body_row);
                        }
                    });
                });
            };
        });
    };

    vcb.open_class_management_modal = function () {
        bootbox.management('Class Metadata', function (results) {
            if (results) {
                vcb.save_class_management_data();
            }
        });
    };

    vcb.open_admin_help_modal = function () {
        bootbox.admin_help('Admin Help', function (results) {

        });
    };

    vcb.remove_auto_tags = function () {
        $('#auto_tag_wrapper').remove();
    };

    vcb.reset_contacts_form = function () {
        $('#contacts_form')[0].reset();
    };

    vcb.s3_upload = function (filename, is_transcript) {
        is_transcript = typeof is_trascript !== undefined ? is_transcript : false;
        // http://philfreo.com/blog/how-to-allow-direct-file-uploads-from-javascript-to-amazon-s3-signed-by-python/
        filename = filename.split('\\').pop();
        var classname = $('#modal_classname').val();

        if (is_transcript) {
            var object_name = classname + '/transcripts/' + filename;
            object_name = object_name.split(' ')
                    .join('_')
                    .replace(',','')
                    .toLowerCase();
            var s3upload = new S3Upload({
                file_dom_selector: '#transcript_file', // an <input type="file"> element
                s3_sign_put_url: 'signS3put/',
                s3_object_name: object_name,
                onProgress: function(percent, message, publicUrl, file) { // Use this for live upload progress bars
                  console.log(percent + '% of transcript file uploaded.');
                },
                onFinishS3Put: function(public_url, file) { // Get the URL of the uploaded file
                    $('#transcript_url').val(public_url);
                    console.log('Transcript upload complete.');
                },
                onError: function(status, file) {
                  vcb.update_status('Transcript upload error: ' + status);
                }
            });
        } else {
            var object_name = classname + '/original/' + filename;
            object_name = object_name.split(' ')
                    .join('_')
                    .replace(',','')
                    .toLowerCase();
            var s3upload = new S3Upload({
                file_dom_selector: '#video_file', // an <input type="file"> element
                s3_sign_put_url: 'signS3put/',
                s3_object_name: object_name,
                onProgress: function(percent, message, publicUrl, file) { // Use this for live upload progress bars
                  var progress_width = $('.progress').width() * percent / 100;
                  $('.percent').text(' ' + percent + '%');
                  $('.bar').width(progress_width);
                },
                onFinishS3Put: function(public_url, file) { // Get the URL of the uploaded file
                    $('#vid_url').val(public_url);
                    vcb.update_status('Upload complete.');
                    // Transcode it
                    $.ajax({
                        type: "POST",
                        url: "create_transcoder_job/",
                        data: {
                            'input_file': object_name
                        },
                        success: function(result) {
                            if (result) {
                                console.log('Transcoding jobs submitted.');
                            } else {
                                console.log('Error submitting transcoder jobs.');
                            }
                        },
                        error: function(xhr, status, error) {
                            vcb.update_status('Server error. ' + error);
                        },
                        complete: function() {
                            vcb.unblock_body();
                        }
                    });
                },
                onError: function(status, file) {
                  vcb.update_status('Upload error: ' + status);
                }
            });
        }
    };

    vcb.save_class_management_data = function () {
        var data = {
            'allow_download': vcb.metadata_download,
            'allow_sharing': vcb.metadata_sharing,
            'allow_transcripts': vcb.metadata_transcripts,
            'classname': vcb.admin_classname,
            'contacts': JSON.stringify(vcb.metadata_contacts),
            'semester': vcb.admin_semester
        };
        var params = {
            'data': data,
            'url': 'save_class_management_data/'
        };

        function save_class_success(results) {
            if (results) {
                vcb.update_status('Saved your class management data.');
                vcb.reset_init_data_on_class_selector(data);
            } else {
                vcb.update_status('Error saving your class management data.');
            }
        }

        vcb.send_ajax(params, save_class_success, null, null);
    };

    vcb.show_contacts_form = function () {
        $('#contacts_form').show();
    };

    vcb.show_save_contacts_button = function () {
        $('.save_contact').show();
    };

    vcb.viewRecent = function () {
        var className = vcb.get_active_class()['class_name'];
        var semester = vcb.get_active_class()['semester'];
        var spin_target = document.getElementById('treespinner');
        var spinner = new Spinner().spin(spin_target);

        $.ajax({
            type: "GET",
            url: "recent/",
            data: {
                'class-name': className,
                'semester': semester
            },
            success: function(recently_viewed) {
                spinner.stop();
                vcb.clear_status_boxes();
                console.log(recently_viewed);

                var recent_data = JSON.parse(recently_viewed);
                $('#recent_table').remove();
                $('#tree').hide();
                d3.selectAll("svg").remove();

                $('#concept-box-header')
                        .html('<i id="concept-box-icon"' +
                        'class="fa fa-star"></i> Recently Viewed');
                var recent_table = $('<table id="recent_table"></table>')
                        .addClass('table table-striped table-bordered');
                var header_row = $('<thead></thead>');
                var views_header = $('<td></td>')
                        .addClass('col-lg-1')
                        .addClass('col-md-1')
                        .addClass('col-sm-2')
                        .addClass('col-xs-2')
                        .addClass('text-center')
                        .html('<strong>Views</strong>');
                var subject_header = $('<td></td>')
                        .addClass('col-lg-4')
                        .addClass('col-md-4')
                        .addClass('col-sm-6')
                        .addClass('col-xs-6')
                        .addClass('text-center')
                        .html('<strong>Video Subject</strong>');

                header_row.append(views_header).append(subject_header);
                recent_table.append(header_row);
                $.each(recent_data, function() {
                    var row = $('<tr></tr>').addClass('queue_vid');
                    var views = $(this)[0].views;
                    var id = $(this)[0].id;
                    var subject = $(this)[0].subject;
                    var views_col = $('<td></td>')
                            .addClass('col-lg-1')
                            .addClass('col-md-1')
                            .addClass('col-sm-2')
                            .addClass('col-xs-2')
                            .addClass('pointer')
                            .addClass('text-center')
                            .text(views);
                    var sub_col = $('<td></td>')
                            .addClass('col-lg-4')
                            .addClass('col-md-4')
                            .addClass('col-sm-6')
                            .addClass('col-xs-6')
                            .addClass('pointer')
                            .addClass('text-center')
                            .text(subject);

                    row.data('id', id);

                    row.append(views_col).append(sub_col);
                    recent_table.append(row);
                });

                recent_table.insertAfter('#treespinner');
            },
            error: function(xhr, status, error) {
                alert(error);
            }
        });
    };


    vcb.view_tree = function () {
        $('#tree').show();
        var spin_target = document.getElementById('treespinner');
        var spinner = new Spinner().spin(spin_target);

        var treeType = lscache.get('treeType');
        var className = lscache.get('className');
        var semester = lscache.get('semester');

        var container = '#treecontainer';
        var tree_target = '#tree';

        var storage_check_name = treeType + '_' + className + semester;
        var storage_check = lscache.get(storage_check_name);

        if (treeType == 'topics') {
            $('#concept-box-header')
                    .html("<i id='concept-box-icon' class='fa fa-list'></i> ");
        } else {
            $('#concept-box-header')
                    .html("<i id='concept-box-icon' class='fa fa-calendar'></i> ");
        }
        var header_txt = " " + className + ', ' + semester;
        $('#concept-box-header').append(header_txt);

        if (storage_check === null) {
            $.ajax({
                type: "GET",
                url: "drawtree/",
                data: {
                    'tree-type': treeType,
                    'class-name': className,
                    'semester': semester
                },
                success: function(tree_data) {
                    // save the data to local storage, for use next time
                    var storage_name = treeType + '_' + className + semester;
                    lscache.set(storage_name, tree_data, 2);
                    vcb.clear_status_boxes();
                    vcb.draw_new_tree(tree_data, spinner, container, tree_target);
                },
                error: function(xhr, status, error) {
                    alert(error);
                }
            });
        } else {
            var tree_data = storage_check;
            vcb.draw_new_tree(tree_data, spinner, container, tree_target);
        }
    };

    return vcb;
})(this, document, jQuery, VCB || {});
