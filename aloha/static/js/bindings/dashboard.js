$(document).ready(function() {
    SMPlayer.disable_transcripts();
    VCB.initialize_class_selector();
    VCB.initialize_control_type_selector();
    VCB.open_selected_class_topic_tree();

    $('#class_selector').on('change', function(e) {
        var raw_data = $(this).select2('data');
        VCB.create_playlist(raw_data,
                VCB.playlist_callback,
                VCB.open_selected_class_topic_tree);
    });

    $(document).on('click', '#sharelink', function () {
        bootbox.share('Copy this link', function(results) {
        });
    });
});