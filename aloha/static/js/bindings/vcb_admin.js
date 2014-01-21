$(document).ready(function () {
    // Toggle a collection to show resources / collections
    $(document).on('click', '.disclose', function() {
        var _closest_li = $(this).closest('li');
        if (NS.nested_sortable_is_open(_closest_li)) {
            NS.collapse_nested_sortable(_closest_li);
        } else {
            NS.expand_nested_sortable(_closest_li);
        }
    });

    // Remove an item from the tree
    $(document).on('click', '.remove', function() {
        var _this = $(this);
        bootbox.confirm('Remove this item and all its children from this course? ' +
                'This cannot be undone!', function(result) {
            if (result) {
                lscache.set('canvas_clean', false);
                _this.parent()
                     .parent()
                     .hide();
                _this.parent()
                     .parent()
                     .find('.menu_heading')
                     .addClass('deleted');
            }
        });
    });


    $.contextMenu({
        selector: '.context-menu-asset',
        trigger: 'right',
        build: function($trigger, e) {
            var items = {};

            items['url'] = {
                'name': 'Edit video URL'
            };
            items['transcript'] = {
                'name': 'Edit transcript URL'
            };

            return {
                callback: function(key, options) {
                    if (key != 'null') {
                        var m = "Picked menu option: " + key;
                        console.log(m);
                        var trigger = $(options['$trigger'][0]);
                        if (key === 'url') {
                            var old_url = trigger.data('url');
                            bootbox.editurl('Enter the new url', old_url, function(result) {
                                if (result != null && result != '') {
                                    lscache.set('canvas_clean', false);
                                    trigger.data('url', result);
                                } else {
                                    VCB.update_status('Not a valid url.');
                                }
                            });
                        } else if (key === 'transcript') {
                            var old_trans = trigger.data('transcript_url');
                            bootbox.editurl('Enter the new transcript url', old_trans, function (result) {
                                if (result != null && result != '') {
                                    lscache.set('canvas_clean', false);
                                    trigger.data('transcript_url', result);
                                } else {
                                    VCB.update_status('Not a valid url.');
                                }
                            });
                        }
                    } else {
                        VCB.update_status('Cannot open a non-existent menu object.');
                    }
                },
                items: items,
            };
        }
    });

    $.contextMenu({
        selector: '.context-menu-tree',
        trigger: 'right',
        build: function($trigger, e) {
            var items = {};

            items['objective'] = {
                'name': 'Insert topic'
            };

            if (!$trigger.hasClass('root')) {
                items['subobjective'] = {
                    'name': 'Attach sub-topic'
                };

                items['video'] = {
                    'name': 'Attach videos'
                };
            }

            return {
                callback: function(key, options) {
                    if (key != 'null') {
                        var m = "Picked menu option: " + key;
                        console.log(m);
                        var trigger = $(options['$trigger'][0]);
                        var item_class = trigger.data('item_class');

                        var name_list = [];
                        $('.objective, .root, .asset').children('.heading_text')
                                       .each(function() {
                            name_list.push($(this).text());
                        });

                        if (key === 'objective' ||
                            key === 'subobjective') {
                            var error_message = 'Please enter a unique name.';
                            if (key === 'objective') {
                                var ol = trigger.parent().parent();
                            } else {
                                var ol = trigger.siblings('ol');
                                if (ol.length === 0) {
                                    var new_ol = $('<ol></ol>');
                                    trigger.parent()
                                        .append(new_ol);
                                    ol = new_ol;
                                }
                            }

                            if (item_class === 'root') {
                                ol = trigger.siblings('ol');
                            }

                            bootbox.prompt('Enter the topic name: ', function(result) {
                                if (result != null && result != '' &&
                                        ($.inArray(result, name_list) < 0)) {
                                    if (trigger.parent().hasClass('mjs-nestedSortable-collapsed') &&
                                            key === 'subobjective') {
                                        trigger.children('span.disclose').click();
                                    }
                                    var child_element = $('<li></li>')
                                                          .addClass('mjs-nestedSortable-branch')
                                                          .addClass('mjs-nestedSortable-collapsed');
                                    var child_heading = $('<div></div>')
                                                          .addClass('menu_heading')
                                                          .addClass('objective')
                                                          .addClass('context-menu-tree')
                                                          .data('item_class', 'objective')
                                                          .data('source', 'user')
                                                          .data('id', 'tmp')
                                                          .data('bank', 'tmp');
                                    var toggle = $('<span></span>')
                                                   .addClass('disclose');
                                    toggle.append('<i class="fa fa-plus"></i>');

                                    var remove = $('<span></span>')
                                                    .addClass('pull-right remove');
                                    remove.append('<i class="fa fa-times"></i>');

                                    var heading_text = $('<p></p>')
                                                         .addClass('heading_text');
                                    heading_text.text(result);
                                    heading_text.attr('contenteditable','true');

                                    child_heading.append(toggle);
                                    child_heading.append(heading_text);
                                    child_heading.append(remove);
                                    child_element.append(child_heading);
                                    ol.append(child_element);

                                    var grandchild_list = $('<ol></ol>');
                                    child_element.append(grandchild_list);

                                    lscache.set('canvas_clean', 'false');
                                    VCB.clear_status_boxes();
                                } else {
                                    VCB.update_status(error_message);
                                }
                            });
                        } else if (key === 'video') {
                            var error_message = 'Please provide all video information.';
                            var class_data = VCB.get_admin_class();
                            var class_semester = class_data['class_name'] +
                                    ', ' + class_data['semester'];

                            bootbox.videoprompt('Enter the video data: ',
                                    class_semester,
                                    NS.get_topic_name(trigger),
                                    function(result) {
                                // Form POST data is sent to views/upload_video for saving on the server
                                if (result != null && result != '') {
                                    lscache.set('canvas_clean', 'false');
                                    VCB.clear_status_boxes();
                                    var ol = trigger.siblings('ol');
                                    if (ol.length === 0) {
                                        var new_ol = $('<ol></ol>');
                                        trigger.parent()
                                            .append(new_ol);
                                        ol = new_ol;
                                    }

                                    // from results, should get an object with two things:
                                    //  1) video url
                                    //  2) timetags array
                                    var video_url = result['video_url'];
                                    var subjects = result['subjects'];
                                    var class_session = result['class_session'];
                                    var recorddate = result['recorddate'];
                                    var timetags = result['timetags'];
                                    var transcript_url = result['transcript_url'];
                                    var pubdate = result['pubdate'];
                                    var sub_count = subjects.length;
                                    $.each(subjects, function (index, tag_desc) {
                                        if (tag_desc != '') {
                                            var asset_element = $('<li></li>');
                                            var asset_heading = $('<div></div>')
                                                    .addClass('asset')
                                                    .addClass('menu_heading')
                                                    .addClass('context-menu-asset')
                                                    .data('source', 'user')
                                                    .data('id', 'tmp')
                                                    .data('bank', 'tmp')
                                                    .data('item_class', 'asset')
                                                    .data('session', class_session)
                                                    .data('pubdate', pubdate)
                                                    .data('recorddate', recorddate)
                                                    .data('timetag', timetags[index])
                                                    .data('transcript_url', transcript_url)
                                                    .data('url', video_url);
                                            var toggle = $('<span></span>')
                                                           .addClass('disclose');
                                            toggle.append('<i class="fa fa-move"></i>');

                                            var remove = $('<span></span>')
                                                            .addClass('pull-right remove');
                                            remove.append('<i class="fa fa-times"></i>');

                                            var heading_text = $('<p></p>')
                                                                 .addClass('heading_text');
                                            heading_text.text(tag_desc);
                                            heading_text.attr('contenteditable','true');

                                            asset_heading.append(toggle);
                                            asset_heading.append(heading_text);
                                            asset_heading.append(remove);
                                            asset_element.append(asset_heading);
                                            ol.append(asset_element);
                                        }

                                        if (--sub_count === 0) {
                                            var span_toggle = trigger.find('span.disclose');
                                            var trig_parent = trigger.parent();
                                            if (trig_parent.hasClass('mjs-nestedSortable-collapsed')) {
                                                span_toggle.click();
                                            }
                                        }
                                    });
                                } else {
                                    VCB.update_status(error_message);
                                }
                            });
                        }
                    } else {
                        VCB.update_status('Cannot open a non-existent menu object.');
                    }
                },
                items: items,
            };
        }
    });

    $(document).on('focus', '[contenteditable]', function() {
    // Regex from : http://stackoverflow.com/questions/2513848/how-to-remove-nbsp-and-br-using-javascript-or-jquery
        var $this = $(this);

        $this.data('before', $this.html().trim().replace(/[<]br[^>]*[>]/gi,""));
        var objs_list = [];
        $('.objective, .root, .asset').children('.heading_text')
                       .each(function() {
            objs_list.push($(this).text()
                                  .toLowerCase()
                                  .trim()
                                  .replace(/[<]br[^>]*[>]/gi,""));
        });
        $this.data('prior_list', objs_list);
        return $this;
    }).on('blur', '[contenteditable]', function() {
        var _this = $(this);
        if (_this.data('before') !== _this.html().trim().replace(/[<]br[^>]*[>]/gi,"")) {
            var prior_list = _this.data('prior_list');
            if ($.inArray(_this.html()
                               .toLowerCase()
                               .trim()
                               .replace(/[<]br[^>]*[>]/gi,""), prior_list) >= 0) {
                VCB.update_status('Please enter a unique name.');
                _this.html(_this.data('before'));
            } else {
                lscache.set('canvas_clean', false);
                _this.data('before', _this.html()
                                          .trim()
                                          .replace(/[<]br[^>]*[>]/gi,""));
            }
        }
    });

    // User wants to save their current progress on the map
    $(document).on('click', '#save_map', function() {
        var canvas_clean = lscache.get('canvas_clean');
        if (!canvas_clean) {
            VCB.block_body('Processing. This could take ~10 minutes, ' +
                    'depending on the size of the class.');
            function parse_element(parent, callback) {
                var children = [];

                var children_elements = parent.siblings('ol')
                                              .children()
                                              .children('.menu_heading');

                var counter = children_elements.length;
                if (counter > 0) {
                    $.each(children_elements, function(index, child_element) {
                        var _this = $(child_element);
                        var is_active = !_this.hasClass('deleted');
                        if (_this.hasClass('objective')) {
                            var tmp = {
                                'bank': _this.data('bank'),
                                'id': _this.data('id'),
                                'is_active': is_active,
                                'item_class': _this.data('item_class'),
                                'name': _this.children('p').html(),
                                'sequence_order': index,
                                'source': _this.data('source')
                            };

                            parse_element(_this, function(_children) {
                                tmp['children'] = _children;

                                children.push(tmp);
                                if (--counter === 0) {
                                    callback(children);
                                }
                            });
                        } else if (_this.hasClass('asset')) {
                            var tmp = {
                                'bank': _this.data('bank'),
                                'id': _this.data('id'),
                                'is_active': is_active,
                                'item_class': _this.data('item_class'),
                                'name': _this.children('p').html(),
                                'pubdate': _this.data('pubdate'),
                                'recorddate': _this.data('recorddate'),
                                'sequence_order': index,
                                'session': _this.data('session'),
                                'source': _this.data('source'),
                                'timetag': _this.data('timetag'),
                                'transcript_url': _this.data('transcript_url'),
                                'url': _this.data('url')
                            };

                            children.push(tmp);
                            if (--counter === 0) {
                                callback(children);
                            }
                        }
                    });
                } else {
                    callback(children);
                }
            }

            var root = $('.root');
            var children_array = [];

            parse_element(root, function(children) {
                var classname = VCB.get_admin_class()['class_name'];
                var semester = VCB.get_admin_class()['semester'];
                $.ajax({
                    type: "POST",
                    url: "update_map/",
                    data: {
                        'children': JSON.stringify(children),
                        'classname': classname,
                        'semester': semester
                    },
                    success: function(result) {
                        var all_okay = result['all_okay'];
                        var message = result['message'];
                        if (all_okay) {
                            var admin_heading = $('#admin_canvas_heading').text();
                            var location_of_dash = admin_heading.indexOf('-');
                            var classname = admin_heading.substr(location_of_dash + 2);
                            var cached_tree_name = "topic_" + classname;

                            lscache.set('canvas_clean', true);
                            VCB.update_status(message + ' and saved ' + classname);
                            VCB.close_admin_div();
                        } else {
                            VCB.update_status(message);
                        }
                    },
                    error: function(xhr, status, error) {
                        alert(error);
                        VCB.update_status_box('Server error: ' + status);
                    },
                    complete: function() {
                        VCB.unblock_page();
                    }
                });
            });
        } else {
            VCB.update_status('No changes to save.');
        }
    });

    // bindings for managing contacts in the class management modal
    $(document).on('click', '.add_contact', function () {
        VCB.show_save_contacts_button();
        VCB.show_contacts_form();
    });

    $(document).on('click', '.save_contact', function () {
        var data = VCB.get_new_contact_details();
        if (data.email === '' ||
                data.fname === '' ||
                data.lname === '' ||
                data.role === '') {
            VCB.update_status('Please include all contact fields.');
        } else {
            VCB.clear_status_boxes();
            DT.add_row_to_table('contacts_table', data);
            VCB.reset_contacts_form();
        }
    });

    $(document).on('click', '.delete_contact', function () {
        var _this = $(this).parent()
                .parent()[0]; // get the row itself
        DT.delete_row('contacts_table', _this);
    });
});