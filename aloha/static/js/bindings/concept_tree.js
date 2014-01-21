$(document).ready(function () {
    // This is to handle click events on the D3.js SVG, with jQuery
    // From: http://stackoverflow.com/questions/9063383/how-to-invoke-click-event-programmaticaly-in-d3
    jQuery.fn.d3Click = function () {
      this.each(function (i, e) {
        var evt = document.createEvent("MouseEvents");
        evt.initMouseEvent("click", true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);

        e.dispatchEvent(evt);
      });
    };

    $(document).on('click', '.queue_vid', function() {
        var spin_target = document.getElementById('main_status_box');
        var spinner = new Spinner().spin(spin_target);
        var id = $(this).data('id');
        var views_col = $(this).children('td')
                               .first();
        var old_views = views_col.text();
        var new_views = parseInt(old_views) + 1;
        views_col.text(String(new_views));
        VCB.playvid(id, spinner);
        if (VCB.get_control_type() === 'recent') {
            var _this = $(this);
            VCB.reorder_recent_table(_this);
        }
    });
});