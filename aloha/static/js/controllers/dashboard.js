var MC3AUTH = (function(window, document, $, auth, undefined) {
    var _host = '';
    var _bank = '';

    auth.construct_objective = function (ele) {
        var obj = {
            'description': {
                'text': $(ele).children('.body').text()
            },
            'displayName': {
                'text': $(ele).children('.term-wrapper').children('.term').text()
            },
            'genusTypeId': 'mc3-objective%3Amc3.learning.topic%40MIT-OEIT'
        };
        return JSON.stringify(obj);
    };

    auth.get_active_bank = function () {
        return _bank;
    };

    auth.get_active_bank_url = function () {
        return auth.get_banks() + _bank;
    };

    auth.get_banks = function () {
        return auth.get_handcar() + '/objectivebanks/';
    };

    auth.get_handcar = function () {
        return auth.get_host() + '/handcar/services/learning';
    };

    auth.get_host = function () {
        return 'https://' + _host;
    };

    auth.get_mc3_host = function () {
        return _host;
    };

    auth.get_objectives_url = function (key) {
        var url = auth.get_active_bank_url() + '/objectives';
        if (typeof key !== 'undefined') {
            url += '/?proxyname=' + key;
        }
        return url
    };

    auth.init_bank_selector = function () {
        var search_term = '';
        $('#bank_selector').select2({
            placeholder: 'Select MC3 Bank To Save To',
            id: function(bank) {return bank.id;},
            ajax: {
                url: auth.get_banks(),
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

    auth.save_definitions_to_mc3 = function () {
        var defs = $('dl.definition.aloha-oer-block');
        $.each(defs, function (index, def) {
            var obj = auth.construct_objective(def);
            MC3UTILS.send_authorized_ajax(obj);
        });
    };

    auth.set_active_bank = function (id) {
        _bank = id;
    };

    auth.set_mc3_host = function (host) {
        _host = host;
    };

    auth.set_mc3_host_display = function () {
        $('#mc3_host').text(_host);
    };

    return auth;
})(this, document, jQuery, MC3AUTH || {});