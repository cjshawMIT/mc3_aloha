var VCB = (function (window, document, $, vcb, undefined) {
    vcb.admin_classname = '';
    vcb.admin_semester = '';
    vcb.allow_download = false;
    vcb.allow_sharing = false;
    vcb.allow_transcripts = false;
    vcb.metadata_download = false;
    vcb.metadata_sharing = false;
    vcb.metadata_transcripts = false;
    vcb.metadata_contacts = [];

    vcb.hide_main_status_box = function () {
        $('#main_status_box').hide();
    };

    vcb.hide_video_download = function () {
        $('#vid_download').hide();
    };

    vcb.hide_share_link = function () {
        $('#vid_share').hide();
    };

    vcb.initialize_class_selector = function () {
        var search_term = '';
        $('#class_selector').select2({
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
                            'allow_download': false,
                            'allow_sharing': false,
                            'allow_transcripts': false,
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
            },
            initSelection: function(element, callback) {
                var init_class = $(element[0]).data('init');
                vcb.create_playlist(init_class, vcb.playlist_callback, callback);
            }
        });
    };

    vcb.initialize_control_type_selector = function () {
        $('#control_type').select2();
    };

    vcb.open_selected_class_topic_tree = function () {
        if ($('#class_selector').val() !== '0') {
            $('#control_type').select2('val', 'topic');
            $('#control_type').trigger('change');
        }
    };

    vcb.reorder_recent_table = function (ele) {
        ele.parent()
                .prepend(ele.clone(deepWithDataAndEvents=true));
        ele.remove();
    };

    vcb.reset_init_data_on_class_selector = function (data) {
        var old_data = $('#class_selector').data('init');
        if (old_data.metadata.class_name === data.classname &&
                old_data.metadata.semester === data.semester) {
            old_data.allow_download = data.allow_download;
            old_data.allow_sharing = data.allow_sharing;
            old_data.allow_transcripts = data.allow_transcripts;
            $('#class_selector').data('init', old_data);
        }
    };

    vcb.show_main_status_box = function () {
        $('#main_status_box').show();
    };

    vcb.show_video_download = function () {
        $('#vid_download').show();
    };

    vcb.show_share_link = function () {
        $('#vid_share').show();
    };
    return vcb;
})(this, document, jQuery, VCB || {});