// Generated by CoffeeScript 1.6.3
(function() {
  define(['aloha',
          'aloha/plugin',
          'jquery',
          'aloha/ephemera',
          'ui/ui',
          'ui/button',
          'semanticblock/semanticblock-plugin',
          './select2.js',
          'css!../../mc3activity/css/mc3activity-plugin.css',
          'css!../../mc3activity/css/select2.css'],
          function(Aloha, Plugin, jQuery, Ephemera, UI, Button, semanticBlock, select2) {
    var TYPE_CONTAINER, exampleishClasses, types, mc3_host, mc3_bank;
    TYPE_CONTAINER = jQuery('<span class="type-container dropdown aloha-ephemera">\n    <span class="type btn-link" href="#" data-toggle="dropdown"></span>\n    <ul class="dropdown-menu">\n    </ul>\n</span>');
    exampleishClasses = {};
    types = [];
    mc3_host = 'oki-dev.mit.edu';
    mc3_bank = 'mc3-objectivebank%3A2%40MIT-OEIT';
    function append_outcomes_selector (parent) {
        var selector = $('<input />')
                .addClass('outcome_selector')
                .attr('type', 'hidden')
                .attr('value', '');
        var wrapper = $('<div></div>')
                .addClass('mc3activity_outcome_link')
                .append('<span>Link to: </span>');
        wrapper.append(selector);
        parent.append(wrapper);
        return wrapper;
    }

    function get_objectives_url (key) {
        var url = 'https://' + mc3_host + '/handcar/services/learning/objectivebanks/' +
                mc3_bank + '/objectives';
        if (typeof key !== 'undefined') {
//            url += '/?proxyname=' + key;
        }
        return url
    }

    function init_outcome_selectors () {
        var search_term = '';
        $('.outcome_selector').select2({
            placeholder: 'Link to an MC3 Learning Outcome',
            id: function(obj) {return obj.id;},
            ajax: {
                url: get_objectives_url(),
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
                                    obj_is_outcome(obj)) {
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
    }

    function obj_is_outcome (obj) {
        var genus = obj.genusTypeId;
        if (genus === 'mc3-objective%3Amc3.learning.outcome%40MIT-OEIT' ||
                genus === 'mc3-objective%3Amc3.learning.generic.outcome%40MIT-OEIT') {
            return true;
        } else {
            return false;
        }
    }

    return Plugin.create('mc3activity', {
      defaults: [
        {
          label: 'Read',
          cls: 'mc3activity',
          hasTitle: true
        }, {
          label: 'Practice',
          cls: 'mc3activity',
          hasTitle: true,
          type: 'practice'
        }, {
          label: 'Watch',
          cls: 'mc3activity',
          hasTitle: true,
          type: 'watch'
        }, {
          label: 'Play',
          cls: 'mc3activity',
          hasTitle: true,
          type: 'play'
        }
      ],
      getLabel: function($element) {
        var type, _i, _len;
        for (_i = 0, _len = types.length; _i < _len; _i++) {
          type = types[_i];
          if ($element.is(type.selector)) {
            return type.label;
          }
        }
      },
      activate: function($element) {
        var $body, $title, label,
          _this = this;
        $title = $element.children('.title');
        $title.attr('hover-placeholder', 'Add a title');
        $title.aloha();
        label = 'MC3 Activity';
        $body = $element.contents().not($title);
        jQuery.each(types, function(i, type) {
          var typeContainer;
          if ($element.is(type.selector)) {
            label = type.label;
            typeContainer = TYPE_CONTAINER.clone();
            if (types.length > 1) {
              jQuery.each(types, function(i, dropType) {
                var $option;
                $option = jQuery('<li><a href="#"></a></li>');
                $option.appendTo(typeContainer.find('.dropdown-menu'));
                $option = $option.children('a');
                $option.text(dropType.label);
                typeContainer.find('.type').on('click', function() {
                  return jQuery.each(types, function(i, dropType) {
                    if ($element.attr('data-type') === dropType.type) {
                      return typeContainer.find('.dropdown-menu li').each(function(i, li) {
                        jQuery(li).removeClass('checked');
                        if (jQuery(li).children('a').text() === dropType.label) {
                          return jQuery(li).addClass('checked');
                        }
                      });
                    }
                  });
                });
                return $option.on('click', function(e) {
                  var $newTitle, key;
                  e.preventDefault();
                  if (dropType.hasTitle) {
                    if (!$element.children('.title')[0]) {
                      $newTitle = jQuery("<" + (dropType.titleTagName || 'span') + " class='title'></" + (dropType.titleTagName || 'span'));
                      $element.append($newTitle);
                      $newTitle.aloha();
                    }
                  } else {
                    $element.children('.title').remove();
                  }
                  if (dropType.type) {
                    $element.attr('data-type', dropType.type);
                  } else {
                    $element.removeAttr('data-type');
                  }
                  typeContainer.find('.type').text(dropType.label);
                  for (key in exampleishClasses) {
                    $element.removeClass(key);
                  }
                  return $element.addClass(dropType.cls);
                });
              });
            } else {
              typeContainer.find('.dropdown-menu').remove();
              typeContainer.find('.type').removeAttr('data-toggle');
            }
            typeContainer.find('.type').text(type.label);
            return typeContainer.prependTo($element);
          }
        });
        jQuery('<div>').addClass('body')
                .addClass('aloha-block-dropzone')
                .attr('placeholder', "Paste the URL of your MC3 activity here.")
                .appendTo($element)
                .aloha()
                .append($body);
        append_outcomes_selector($element);
        init_outcome_selectors();
        return true;
      },
      deactivate: function($element) {
        var $body, $title, $titleElement, hasTextChildren, hasTitle, isEmpty, titleTag,
          _this = this;
        $body = $element.children('.body');
        hasTextChildren = $body.children().length !== $body.contents().length;
        isEmpty = $body.text().trim() === '';
        if (isEmpty) {
          $body = jQuery('<p class="para"></p>');
        } else {
          $body = $body.contents();
          if (hasTextChildren) {
            $body = $body.wrap('<p></p>').parent();
          }
        }
        $element.children('.body').remove();
        hasTitle = void 0;
        titleTag = 'span';
        jQuery.each(types, function(i, type) {
          if ($element.is(type.selector)) {
            hasTitle = type.hasTitle || false;
            return titleTag = type.titleTagName || titleTag;
          }
        });
        if (hasTitle || hasTitle === void 0) {
          $titleElement = $element.children('.title');
          $title = jQuery("<" + titleTag + " class=\"title\"></" + titleTag + ">");
          if ($titleElement.length) {
            $title.append($titleElement.contents());
            $titleElement.remove();
          }
          $title.prependTo($element);
        }
        return $element.append($body);
      },
      selector: '.mc3activity',
      init: function() {
        var _this = this;
        types = this.settings;
        jQuery.each(types, function(i, type) {
          var className, hasTitle, label, newTemplate, tagName, titleTagName, typeName;
          className = type.cls || (function() {
            throw 'BUG Invalid configuration of mc3activity plugin. cls required!';
          })();
          typeName = type.type;
          hasTitle = !!type.hasTitle;
          label = type.label || (function() {
            throw 'BUG Invalid configuration of mc3activity plugin. label required!';
          })();
          tagName = type.tagName || 'div';
          titleTagName = type.titleTagName || 'div';
          if (typeName) {
            type.selector = "." + className + "[data-type='" + typeName + "']";
          } else {
            type.selector = "." + className + ":not([data-type])";
          }
          exampleishClasses[className] = true;
          newTemplate = jQuery("<" + tagName + "></" + tagName);
          newTemplate.addClass(className);
          if (typeName) {
            newTemplate.attr('data-type', typeName);
          }
          if (hasTitle) {
            newTemplate.append("<" + titleTagName + " class='title'></" + titleTagName);
          }
          UI.adopt("insert-" + className + typeName, Button, {
            click: function() {
              return semanticBlock.insertAtCursor(newTemplate.clone());
            }
          });
          if ('mc3activity' === className && !typeName) {
            return UI.adopt("insertMC3Activity", Button, {
              click: function() {
                return semanticBlock.insertAtCursor(newTemplate.clone());
              }
            });
          }
        });
        return semanticBlock.register(this);
      }
    });
  });

}).call(this);
