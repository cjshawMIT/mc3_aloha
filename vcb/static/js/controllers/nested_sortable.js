var NS = (function (window, document, $, ns, undefined) {
    ns.append_element = function (parent, data) {
        var child_element = $('<li></li>')
                .addClass('mjs-nestedSortable-branch')
                .addClass('mjs-nestedSortable-collapsed');
        var child_heading = $('<div></div>')
                .addClass('menu_heading');
        var toggle = $('<span></span>')
                .addClass('disclose')
                .append('<i class="fa fa-plus"></i>');
        var heading_text = $('<p></p>')
                .addClass('heading_text')
                .text(data['text']);
        child_heading.append(toggle);
        child_heading.append(heading_text);
        child_element.append(child_heading);
        parent.append(child_element);
    };

    ns.collapse_nested_sortable = function (ele) {
        ele.children('div')
                .children('span.disclose')
                .children('i')
                .removeClass('fa-minus')
                .addClass('fa-plus');
        ele.toggleClass('mjs-nestedSortable-collapsed');
        ele.toggleClass('mjs-nestedSortable-expanded');
    };

    ns.create_nested_sortable = function (wrapper, obj, _callback) {
        var list = $('<ol></ol>');
        var child_list = $('<ol></ol>')
                .addClass('child_list');
        list.append(child_list);

        function attach_children (ele, parent) {
            var children = parent.children;
            var child_counter = children.length;
            if (child_counter > 0) {
                var target = ele.children('.child_list');
                $.each(children, function (name, value) {
                    var data = {
                        'text': name + ': ' + value.size + ' bytes'
                    };
                    NS.append_element(target, data);
                    if (value.hasOwnProperty('children')) {
                        // TODO: test this...need an NS 3 levels deep
                        var grandchild_list = $('<ol></ol>')
                                .addClass('child_list');
                        target.append(grandchild_list);
                        attach_children(target, value.children);
                    }

                    if (--counter === 0) {
                        _callback();
                    }
                });
            } else {
                if (--counter === 0) {
                    _callback();
                }
            }
        }

        wrapper.append(list);
        attach_children(list, obj);
    };

    ns.expand_nested_sortable = function (ele) {
        ele.children('div')
                .children('span.disclose')
                .children('i')
                .removeClass('fa-plus')
                .addClass('fa-minus');
        ele.toggleClass('mjs-nestedSortable-expanded');
        ele.toggleClass('mjs-nestedSortable-collapsed');
    };

    ns.get_topic_name = function (ele) {
        return ele.find('.heading_text').text();
    };

    ns.nested_sortable_is_open = function (ele) {
        if (ele.hasClass('mjs-nestedSortable-expanded')) {
            return true;
        } else {
            return false;
        }
    };

    return ns;
})(this, document, jQuery, NS || {});