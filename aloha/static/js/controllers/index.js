var VCB = (function (window, document, $, vcb, undefined) {
    'use strict';
    // =================
    // from http://jqueryui.com/autocomplete/#remote
    vcb.init_search_autocomplete = function () {
        $('#vid_search').autocomplete( {
            source: function(request, response) {
                var sel = $('#class_selector').val();
                $.ajax({
                    url: "search_videos/",
                    data: {
                        id: sel,
                        term: request.term
                    },
                    success: function(data) {
                         response($.map(data, function(item) {
                            return {
                                label: item.label,
                                id: item.id
                            }
                        }));
                    }
                });
            },
            minLength: 2,
            position: {
                my: "left top",
                at: "left bottom"
            },
            select: function(event, ui) {
               var spin_target = document.getElementById('main_status_box');
               var spinner = new Spinner().spin(spin_target);
                ui.item ? VCB.playvid(ui.item.id, spinner) : pass;
            }
        });
    };

    vcb.validate_tos_and_class_codes = function () {
        // To make sure at least one class is selected
        // From http://stackoverflow.com/questions/15136943/jquery-validate-out-of-two-blank-fields-at-least-one-field-must-be-filled-or-b
        jQuery.validator.addMethod("require_from_group", function (value, element, options) {
            var numberRequired = options[0];
            var selector = options[1];
            var fields = $(selector, element.form);
            var filled_fields = fields.filter(function () {
                // it's more clear to compare with empty string
                return $(this).val() != "";
            });
            var empty_fields = fields.not(filled_fields);
            // we will mark only first empty field as invalid
            if (filled_fields.length < numberRequired && empty_fields[0] == element) {
                return false;
            }
            return true;
            // {0} below is the 0th item in the options field
        }, jQuery.format("Please put in the code for at least {0} class."));

        // ================
        //  From http://www.infotuts.com/create-registration-form-easily-with-twitter-bootstrap-in-minutes/
        var input_names = '';
        $('.class_code').each(function() {
            input_names += $(this).attr('name') + ' ';
        });
        input_names = input_names.trim()

        $("#signup").validate({
            groups:{
                classes: input_names,
            },
            rules:{
                tos: {
                    required:true
                },
                email:{
                    required:true,
                    email: true
                },
                passwd:{
                    required:true,
                    minlength: 8
                },
                conpasswd:{
                    required:true,
                    equalTo: "#passwd"
                }
            },
            errorClass: "help-inline"
        });

        $("#class_signup").validate({
            groups:{
                classes: input_names,
            },
            rules:{
                tos: {
                    required:true
                },
            },
            errorClass: "help-inline"
        });

        $('.class_code').each(function() {
            $("[name='" + $(this).attr('name') + "']")
                    .rules("add", {require_from_group:[1, '.class_code']});
        });
    };
    return vcb;
})(this, document, jQuery, VCB || {});