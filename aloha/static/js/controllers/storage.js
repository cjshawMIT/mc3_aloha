var VCB = (function (window, document, $, vcb, undefined) {
    vcb.calculate_s3 = function (target_id, _callback) {
        var target = $('#' + target_id);
        var params = {
            'url': 'get_s3_size/'
        };

        vcb.send_ajax(params, _callback, null, vcb.unblock_body);
    };

    vcb.store_class_and_semester = function (data) {
        lscache.set('className', data['class_name'], 1);
        lscache.set('semester', data['semester'], 1);
    };

    return vcb;
})(this, document, jQuery, VCB || {});