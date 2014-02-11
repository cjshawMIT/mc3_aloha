define(
['aloha', 'aloha/plugin', 'jquery', 'ui/ui', 'ui/button', 'PubSub',
    'css!../../../mc3/oea/css/oea.css'],
function(Aloha, plugin, $, Ui, Button, PubSub) {
    "use strict";

	var GENTICS = window.GENTICS;

    var DIALOG =
    '<div class="oea-options">' +
    '    <a class="search-oea-link" href="javascript:;">Search for OEA</a> OR <a class="upload-url-link" href="javascript:;">specify a known URL</a>.' +
    '</div>' +
    '<div class="upload-url-form">' +
    '    <input type="text" class="oea-url oea-input" placeholder="Enter URL of OEA ...">' +
    '</div>' +
    '<div class="search-tabs">' +
    '    <ul>' +
    '        <li><a href="#search-oea-form">OEA</a></li>' +
    '        <li><a href="#search-mc3-form">MC3</a></li>' +
    '    </ul>' +
    '    <div class="search-oea-form search-tab" id="search-oea-form">' +
    '      <input id="oea_search" class="oea-search oea-input" type="text" placeholder="Search for assessments..." />' +
    '    </div>' +
    '    <div class="search-mc3-form search-tab" id="search-mc3-form">' +
    '    </div>' +
    '</div>' +
    '<div class="placeholder preview">' +
    '</div>';

    function prepareoea(plugin, img){
    }

    return plugin.create('oea', {
        // Settings:
        // uploadurl - where to upload to
        // uploadfield - field name to use in multipart/form upload
        // parseresponse - takes the xhr.response from server, return an
        //                 url to be used for the oea. Default expects
        //                 a json response with an url member.
        defaultSettings: {
            uploadfield: 'upload',
            parseresponse: function(xhr){ return JSON.parse(xhr.response).url; }
        },
        init: function(){
            this.settings = jQuery.extend(true, this.defaultSettings, this.settings);
            var plugin = this;
            Aloha.bind('aloha-editable-created', function(event, editable){
                editable.obj.find('img').each(function(){
                    prepareoea(plugin, $(this));
                });
            });
            PubSub.sub('aloha.selection.context-change', function(m){
                if ($(m.range.markupEffectiveAtStart).parent('img')
                        .length > 0) {
                    // We're inside an oea
                } else {
                    // We're outside an oea
                }
            });
            this._createDialog();
            this._createoeaButton = Ui.adopt("insertOEA", Button, {
                tooltip: "Insert OEA",
                icon: "aloha-button aloha-oea-insert",
                scope: 'Aloha.continuoustext',
                click: function(e){
                    var range = Aloha.Selection.getRangeObject(),
                        $placeholder = $('<span class="aloha-ephemera oea-placeholder"> </span>');
                    if (range.isCollapsed()) {
                        GENTICS.Utils.Dom.insertIntoDOM($placeholder, range, $(Aloha.activeEditable.obj));
                        $('.plugin.oea').data('placeholder', $placeholder)
                                .modal('show');
                        plugin._initOEASearch();
                        plugin._initMC3Search();
                    }
                }
            });
            this._hideModal = function () {
                var $modal = $('.plugin.oea');
                plugin._resetModalForms();
                $modal.modal('hide');
            };
            var $modal = $('.plugin.oea');
            $modal.on('hidden.bs.modal', function () {
                if ($('.oea-placeholder').length > 0) {
                    plugin._resetModalForms();
                    $('.oea-placeholder').remove();
                }
            });
        },
        _createDialog: function(){
            var plugin = this,
                $dialog = $('<div class="plugin oea modal">'),
                $body = $('<div class="modal-body"></div>');
            $dialog.append('<div class="modal-header">' +
                    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
                    '<h3>Open Embedded Assessments</h3></div>');
            $dialog.append($body);
            $dialog.append('<div class="modal-footer">' +
                    '<a href="#" class="btn action insert">Insert</a>' +
                    '<a href="#" class="btn cancel" data-dismiss="modal">Cancel</a></div>');
            $body.append(DIALOG);

            // Add click handlers
            $body.find('.search-oea-link').on('click', function(e){
                $body.find('.upload-url-form').hide();
                $body.find('.placeholder.preview').hide();
                plugin._initSearchTabs();
                return e.preventDefault();
            });
            $body.find('.upload-url-link').on('click', function(e){
                $body.find('.search-tabs').hide();
                $body.find('.placeholder.preview').hide();
                $body.find('.upload-url-form').show();
                return e.preventDefault();
            });
            $dialog.find('.action.insert').on('click', function(e){
                var oea = $('.placeholder.preview').html();
                $dialog.data('placeholder').replaceWith(oea);
                plugin._hideModal();

                return e.preventDefault();
            });
            $body.find('.oea-url').on('input', function(e){
                var url = $(this).val();
                plugin._getOembed(url, function (results) {
                    plugin._setPreview(results);
                });
                return e.preventDefault();
            });
            $body.find('.search-tabs').hide();
            $body.find('.placeholder.preview').hide();
            $body.find('.upload-url-form').hide();
            $('body').append($dialog);
        },
        _hideModal: function(){
        },
        _createoeaButton: undefined,
        _initOEASearch: function() {
            var plugin = this;
            $( "#oea_search" ).autocomplete({
                source: function( request, response ) {
                    $.ajax({
                        url: "http://www.openassessments.com/api/assessments.json",
                        dataType: "json",
                        data: {
                            q: request.term
                        },
                        success: function(data) {
                            if (data.assessments.length > 0) {
                                $('.plugin.oea').find('.placeholder.preview')
                                        .text('')
                                        .hide();
                                response($.map(data.assessments, function(item) {
                                    var i = item.assessments,
                                            url = 'http://www.openassessments.com/users/' +
                                                    i.user_id + '/assessments/' + i.id;
                                    return {
                                        label: i.title,
                                        value: url
                                    }
                                }));
                            } else {
                                $('.plugin.oea').find('.placeholder.preview')
                                        .text('Nothing found for: ' + term + '.')
                                        .show();
                            }
                        }
                    });
                },
                minLength: 2,
                select: function( event, ui ) {
                    plugin._getOembed(ui.item.value, function (results) {
                        plugin._setPreview(results);
                    });
                    event.preventDefault();
                    $('#oea_search').val(ui.item.label);
                },
                focus: function (event, ui) {
                    event.preventDefault();
                    $('#oea_search').val(ui.item.label);
                },
                open: function() {
                    $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
                },
                close: function() {
                    $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
                }
            });
        },
        _getBody: function () {
            return $('.plugin.oea').find('.modal-body');
        },
        _getOembed: function (url, callback) {
            $.ajax({
                url: "http://www.openassessments.com/oembed.json",
                dataType: "json",
                data: {
                    url: url
                },
                success: function(data) {
                    callback(data);
                }
            });
        },
        _setPreview: function (ele) {
            $('.placeholder.preview').empty()
                    .html(ele.html)
                    .show();
        },
        _initSearchTabs: function () {
            var $body = $('.plugin.oea').find('.modal-body');
            $('.search-tabs').tabs();
            $body.find('.search-tabs').show();
        },
        _initMC3Search: function () {
            var target = $('#search-mc3-form').empty();
            MC3AUTH.append_outcomes_selector(target);
        },
        _resetModalForms: function () {
            var $modal = $('.plugin.oea');
            $modal.find('.placeholder.preview')
                    .empty()
                    .hide();
            $modal.find('.upload-url-form')
                    .hide();
            $modal.find('input.oea-input')
                    .val('');
            $modal.find('.search-tabs')
                    .hide();
            $modal.find('.search-mc3-form')
                    .select2('data', null);
        }
    });
});
