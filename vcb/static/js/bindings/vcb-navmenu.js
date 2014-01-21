// ==============
// This section takes care of the nav menu for opening up trees and other content
$(document).ready(function () {
    $('#control_type').on('change', function(e) {
        if (e.hasOwnProperty('val')) {
            var sel = e.val;
        } else {
            var sel = $(this).val();
        }
        var class_data = VCB.get_active_class();
        VCB.store_class_and_semester(class_data);
        if (sel === 'recent') {
            lscache.remove('treeType');

            VCB.viewRecent();
        } else {
            var treeType = sel;
            lscache.set('treeType', treeType, 1);
            VCB.view_tree();
        }
    });

    // This function allows staff users to upload an XML file and parse the timestamps
    // for use with TechTV
    $(document).on('click', 'a.nav-amps', function() {
        // Open a modal that prompts for file upload
        bootbox.xmlprompt('Upload XML file', function(results) {
            console.log(results);
        });
    });

    // To allow Admin users to download click logs
    $(document).on('click','.nav-clicklog', function () {
        VCB.clear_status_boxes();
        VCB.block_nav();

        var click_div = $('<div></div>');
        var action_div = VCB.append_div(click_div, 'click_action_div');
        VCB.append_class_selector(action_div, 'click_class');
        VCB.append_download_button(action_div);
        VCB.append_staff_checkbox(action_div);
        VCB.append_div(click_div, 'log_div');
        VCB.create_modal(click_div, 'Click logs');
        VCB.initialize_nav_class_selector('click_class');

        $('#click_class').on('change', function(e) {
            var sel = e.val;
            var include_staff = $('#include_staff input').prop('checked');
            VCB.generate_clicklog(sel, false, include_staff);
        });

        $(document).on('click', '#include_staff', function () {
            try {
                var sel = $('#click_class').val();
                if (sel !== '') {
                    var include_staff = $('#include_staff input').prop('checked');
                    VCB.generate_clicklog(sel, false, include_staff);
                }
            } catch (err) {
                // do nothing if no class selected
            }
        });

        $(document).on('click', '#download_log', function() {
            var sel = $('#click_class').val();
            var include_staff = $('#include_staff input').prop('checked');
            window.open('clickLog/?id=' + sel +
                    '&download=true&include_staff=' + include_staff);
        });
    });
    // ==========

    $(document).on('click', '.nav-s3dash', function () {
        VCB.clear_status_boxes();
        VCB.block_page('Calculating S3 Usage.');
        var s3dash_div = $('<div></div>');
        VCB.append_div(s3dash_div, 's3_results');
        VCB.create_modal(s3dash_div, 'S3 Usage');
        VCB.calculate_s3('s3_results', function (results) {
            console.log(results);
            NS.create_nested_sortable('s3_results', results, VCB.unblock_body);
        });
    });

    // This function builds and opens the Administrative <div> for creating or modifying a class
    // Two-pane div.
    //   Left pane should be adding new objects and activities, deleting, and moving. Save / Cancel.
    //   Right pane should show a graphical representation of the changes.
    $(document).on('click', 'a.nav-admin', function() {
        function create_admin_div() {
            VCB.clear_status_boxes();
            VCB.hide_main_status_box();
            var admin_div = $('<div id="admin_div"></div>')
                    .addClass('row')
                    .addClass('row-fluid');
            var admin_status_box = $('<div id="admin_status_box"></div>')
                    .addClass('box-content')
                    .addClass('status_box');

            admin_div.append(admin_status_box);

            var admin_canvas_div = $('<div id="admin_canvas"></div>')
                    .addClass('box span12')
                    .addClass('pad_left');
            var admin_canvas_header_well = $('<div></div>')
                    .addClass('box-header well');
            var admin_canvas_heading = $('<h2 id="admin_canvas_heading"></h2>')
                    .addClass('span9')
                    .html('<i class="fa fa-pencil"></i>' +
                    ' Class Administration Canvas');
            var admin_canvas_box = $('<div id="admin_canvas_box"></div>')
                    .addClass('box-content');
            var admin_canvas_spinner = $('<div id="admin_canvas_spinner"></div>')
                    .addClass('box-content');
            var admin_canvas_content = $('<div id="admin_canvas_content"></div>')
                                         .addClass('pad_left');

            var admin_help = $('<div></div>')
                    .addClass('pull-left pointer admin_help')
                    .attr('id', 'admin_help')
                    .append('<i class="fa fa-question"></i> Admin help');
            var metadata = $('<div></div>')
                    .addClass('pull-left class_management pointer')
                    .attr('id', 'class_management')
                    .append('<i class="fa fa-info-circle"></i> Class Management');
            var save_btn = $('<div id="save_map" title="Save the current canvas">Save</div>')
                    .addClass('btn btn-success btn-small pull-right');
            var cancel_btn = $('<div id="cancel_map" title="Close the Admin canvas">' +
                    'Close</div>')
                              .addClass('btn btn-inverse btn-small pull-right')
                              .on('click', function() {
                                    var canvas_clean = lscache.get('canvas_clean');
                                    var treeType = lscache.get('treeType');
                                    var className = lscache.get('className');
                                    var semester = lscache.get('semester');
                                    if (canvas_clean) {
                                        VCB.close_admin_div();
                                        if (treeType !== undefined &&
                                            treeType !== null &&
                                            className !== undefined &&
                                            className !== null &&
                                            semester !== undefined &&
                                            semester !== null) {
                                            lscache.set('treeType', treeType, 1);
                                            lscache.set('className', className, 1);
                                            lscache.set('semester', semester, 1);
                                            VCB.view_tree();
                                        } else if ( (treeType === undefined ||
                                                     treeType === null) &&
                                                    (className !== undefined &&
                                                     className !== null) &&
                                                    (semester !== undefined &&
                                                     semester !== null)) {
                                            lscache.set('className', className, 1);
                                            lscache.set('semester', semester, 1);
                                            VCB.viewRecent();
                                        }
                                    } else {
                                        bootbox.dialog('Really throw away all of your un-saved work?', [{
                                            'label': 'No!',
                                            'class': 'btn-success',
                                            'callback': function() {}
                                        },
                                        {
                                            'label': 'Yes',
                                            'class': 'btn-danger',
                                            'callback':	function() {
                                                VCB.close_admin_div();
                                                if (treeType !== undefined &&
                                                    treeType !== null &&
                                                    className !== undefined &&
                                                    className !== null &&
                                                    semester !== undefined &&
                                                    semester !== null) {
                                                    lscache.set('treeType', treeType, 1);
                                                    lscache.set('className', className, 1);
                                                    lscache.set('semester', semester, 1);
                                                } else if ( (treeType === undefined ||
                                                             treeType === null) &&
                                                            (className !== undefined &&
                                                             className !== null) &&
                                                            (semester !== undefined &&
                                                             semester !== null)) {
                                                    lscache.set('className', className, 1);
                                                    lscache.set('semester', semester, 1);
                                                }
                                            }
                                        }]);
                                    }
                              });

            admin_canvas_header_well.append(admin_canvas_heading);
            admin_canvas_header_well.append(cancel_btn);
            admin_canvas_header_well.append(save_btn);
            admin_canvas_header_well.append(metadata);
            admin_canvas_header_well.append(admin_help);
            admin_canvas_box.append(admin_canvas_spinner);
            admin_canvas_box.append(admin_canvas_content);
            admin_canvas_div.append(admin_canvas_header_well);
            admin_canvas_div.append(admin_canvas_box);

            admin_div.append(admin_canvas_div);

            bootbox.selectclass('Create new class or modify existing one: ', function(result) {
                if (result != null && result != '') {
                    admin_div.insertBefore('#help_modal').hide();
                    var classname = result['classname'];
                    var classnumber = result['classnumber'];
                    var obj_bank_id = result['obj_bank_id'];
                    var code = result['code'];
                    var semester = result['semester'];
                    d3.selectAll("svg").remove();
                    lscache.set('canvas_clean', 'true');

                    $('#admin_canvas_heading')
                            .html('<i class="fa fa-pencil"></i> ' +
                                    classname + ', ' + semester +
                                    '. Access code: ' + code);

                    $('#viewer_container').fadeOut(600, function() {$(this).hide();});
                    $('#vid_downloadsearch').fadeOut(600, function() {$(this).hide();});
                    $('#admin_div').fadeIn(600, function() {$(this).show();});
                    VCB.set_admin_class_data(classname, semester);
                    VCB.initialize_class_metadata(result);
                } else {
                    VCB.close_admin_div();
                }
            });
        }

        if ($('#admin_div').length) {
            var canvas_clean = lscache.get('canvas_clean');
            if (canvas_clean) {
                $('#admin_div').fadeOut(600, function() {$(this).remove();});
                create_admin_div();
            } else {
                bootbox.dialog('Really throw away all of your un-saved work and change classes?', [{
                    'label': 'No!',
                    'class': 'btn-success',
                    'callback': function() {
                    }
                },
                {
                    'label': 'Yes',
                    'class': 'btn-danger',
                    'callback':	function() {
                        create_admin_div();
                    }
                }]);
            }
        } else {
            create_admin_div();
        }
    });

    // If an event gets to the body when using the admin canvas
    $(document).on('click', 'html', function() {
      $("#action_div:visible").fadeOut();
    });

    $(document).on('click', '.class_management', function () {
        VCB.open_class_management_modal();
    });

    $(document).on('click', '.admin_help', function () {
        VCB.open_admin_help_modal();
    });
});
