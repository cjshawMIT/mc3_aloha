var MC3AUTH = (function(window, document, $, _auth, undefined) {
    var _host = '';
    var _bank = '';

    _auth.append_outcomes_selector = function(parent) {
        var selector = $('<input />')
                .addClass('outcome_selector')
                .attr('type', 'hidden')
                .attr('value', '');
        var wrapper = $('<div></div>')
                .addClass('mc3activity_outcome_link')
                .append('<span>Link to: </span>');
        if (_auth.get_active_bank() !== '') {
            wrapper.append(selector);
        } else {
            wrapper.append('<span class="red">Please pick an MC3 Objective Bank, first.</span>');
        }
        parent.append(wrapper);
        _auth.init_outcome_selectors();
        return wrapper;
    };

    _auth.close_parent_dialog = function (ele) {
        ele.parent()
                .parent()
                .dialog('close');
    };

    _auth.construct_objective = function (ele) {
        var obj = {
            'description': {
                'text': $(ele).children('.body').text()
            },
            'displayName': {
                'text': $(ele).children('.term-wrapper').text()
            },
            'genusTypeId': 'mc3-objective%3Amc3.learning.outcome%40MIT-OEIT'
        };

        if ($(ele).data().hasOwnProperty('mc3_id')) {
            obj['id'] = $(ele).data('mc3_id');
        }
        return JSON.stringify(obj);
    };

    _auth.get_active_bank = function () {
        return _bank;
    };

    _auth.get_active_bank_url = function () {
        return _auth.get_banks() + _bank;
    };

    _auth.get_banks = function () {
        return _auth.get_handcar() + '/objectivebanks/';
    };

    _auth.get_handcar = function () {
        return _auth.get_host() + '/handcar/services/learning';
    };

    _auth.get_host = function () {
        return 'https://' + _host;
    };

    _auth.get_mc3_host = function () {
        return _host;
    };

    _auth.get_objectives_url = function (key) {
        var url = _auth.get_active_bank_url() + '/objectives';
        if (typeof key !== 'undefined') {
//            url += '/?proxyname=' + key;
        }
        return url
    };

    _auth.init_bank_selector = function () {
        var search_term = '';
        $('#bank_selector').select2({
            placeholder: 'Select MC3 Bank To Save To',
            id: function(bank) {return bank.id;},
            ajax: {
                url: _auth.get_banks(),
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
                        var filtered_banks = [];
                        $.each(data, function(index, bank) {
                            var bank_name = bank.displayName.text;
                            bank_name = bank_name.toLowerCase();

                            if (bank_name.indexOf(search_term) >= 0) {
                                filtered_banks.push(bank);
                            }
                        });
                        return {results: filtered_banks};
                    } else {
                        var tmp = [{
                            'displayName': {
                                'text': 'None Found'
                            }
                        }];
                        return {results: tmp};
                    }
                }
            },
            formatResult: function(bank) {
                return bank.displayName.text;
            },
            formatSelection: function(bank) {
                return bank.displayName.text;
            }
        });
    };

    _auth.init_host_selector = function () {
        $('#host_selector').select2();
        $('#host_selector').select2('val','oki-dev.mit.edu');
    };

    _auth.init_outcome_selectors = function () {
        var search_term = '';
        $('.outcome_selector').select2({
            placeholder: 'Link to an MC3 Learning Outcome',
            id: function(obj) {return obj.id;},
            ajax: {
                url: _auth.get_objectives_url(),
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
                        var filtered_objs = [];
                        $.each(data, function(index, obj) {
                            var obj_name = obj.displayName.text;
                            obj_name = obj_name.toLowerCase();

                            if (obj_name.indexOf(search_term) >= 0 &&
                                    _auth.obj_is_outcome(obj)) {
                                filtered_objs.push(obj);
                            }
                        });
                        return {results: filtered_objs};
                    } else {
                        var tmp = [{
                            'displayName': {
                                'text': 'None Found'
                            }
                        }];
                        return {results: tmp};
                    }
                }
            },
            formatResult: function(obj) {
                return obj.displayName.text;
            },
            formatSelection: function(obj) {
                return obj.displayName.text;
            }
        });
    };

    _auth.obj_is_incomplete = function (obj) {
        if (obj.displayName.text === '' ||
                obj.description.text === '') {
            return true;
        } else {
            return false;
        }
    };

    _auth.obj_is_outcome = function (obj) {
        var genus = obj.genusTypeId;
        if (genus === 'mc3-objective%3Amc3.learning.outcome%40MIT-OEIT' ||
                genus === 'mc3-objective%3Amc3.learning.generic.outcome%40MIT-OEIT') {
            return true;
        } else {
            return false;
        }
    };

    _auth.prompt_user_with_similar_terms = function (terms, ele) {
        var counter = terms.length;
        var target = $($(ele).closest('.body').context)
                .parent()
                .siblings('.body');
        var title = counter + ' definitions like: ' + MC3UTILS.get_new_definition(ele);
        var toggle = $('<div></div>')
                .addClass('toggle_similar')
                .addClass('pointer')
                .html('Click one to use it, or type your own.   <i class="fa fa-sort-down"></i>');
        var similar_defs = $('<div></div>')
                .addClass('container')
                .attr('id', 'similar_defs')
                .hide();
        var wrapper = $('<div></div>')
                .append(toggle)
                .append(similar_defs);
        $.each(terms, function (index, term) {
            var desc = term.description.text;
            var name = term.displayName.text;
            var row = $('<div></div>')
                    .addClass('row')
                    .addClass('box')
                    .addClass('existing_mc3_def')
                    .append('<div class="left_col col-sm-5">' + name + '</div>')
                    .append('<div class="col-sm-7">' + desc + '</div>')
                    .data('mc3_id', term.id)
                    .data('target', target)
                    .data('description', desc)
                    .data('name', name);
            similar_defs.append(row);
            if (--counter === 0) {
                wrapper.dialog({
                    title: title,
                    width: 800,
                    close: function (event, ui) {
                        $(this).dialog('destroy').remove();
                    },
                    position: {
                        my: 'top',
                        at: 'bottom',
                        of: '.toolbar.aloha-dialog'
                    }
                });
            }
        });
    };

    _auth.remove_outcomes_selector = function () {
        $('.mc3activity_outcome_link').remove();
    };

    _auth.save_definitions_to_mc3 = function () {
        var defs = $('dl.mc3definition.aloha-oer-block');
        $.each(defs, function (index, def) {
            var obj = _auth.construct_objective(def);
            if (!_auth.obj_is_incomplete(obj)) {
                MC3UTILS.send_authorized_ajax(obj, def);
            }
        });
    };

    _auth.set_active_bank = function (id) {
        _bank = id;
    };

    _auth.set_definition = function (ele) {
        var target = $($(ele).data('target'));
        target.text($(ele).data('description')).aloha();
    };

    _auth.set_definition_mc3_id = function (ele) {
        var target = $($(ele).data('target'))
                .parent();
        target.data('mc3_id', $(ele).data('mc3_id'));
    };

    _auth.set_mc3_host = function (host) {
        _host = host;
    };

    _auth.set_name = function (ele) {
        var target = $($(ele).data('target'))
                .siblings('.term-wrapper');
        target.text($(ele).data('name')).aloha();
    };

    _auth.toggle_icon = function (icon) {
        if (icon.hasClass('fa-sort-down')) {
            icon.removeClass('fa-sort-down')
                    .addClass('fa-sort-up');
        } else {
            icon.removeClass('fa-sort-up')
                    .addClass('fa-sort-down');
        }
    };

    return _auth;
})(this, document, jQuery, MC3AUTH || {});