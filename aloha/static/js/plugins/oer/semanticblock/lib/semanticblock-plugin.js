// Generated by CoffeeScript 1.6.3
(function() {
  var __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  define(['aloha', 'block/block', 'block/blockmanager', 'aloha/plugin', 'aloha/pluginmanager', 'jquery', 'aloha/ephemera', 'ui/ui', 'ui/button', 'copy/copy-plugin', 'css!semanticblock/css/semanticblock-plugin.css'], function(Aloha, Block, BlockManager, Plugin, pluginManager, jQuery, Ephemera, UI, Button, Copy) {
    var DIALOG_HTML, activate, bindEvents, blockControls, blockDragHelper, blockIdentifier, blockTemplate, cleanIds, cleanWhitespace, copyBuffer, deactivate, getLabel, getType, insertElement, pluginEvents, registeredTypes, semanticBlock, topControls;
    if (pluginManager.plugins.semanticblock) {
      return pluginManager.plugins.semanticblock;
    }
    semanticBlock = Block.AbstractBlock.extend({
      shouldDestroy: function() {
        return false;
      }
    });
    BlockManager.registerBlockType('semanticBlock', semanticBlock);
    DIALOG_HTML = '<div class="semantic-settings modal hide" id="linkModal" tabindex="-1" role="dialog" aria-hidden="true" data-backdrop="false">\n  <div class="modal-header">\n    <h3></h3>\n  </div>\n  <div class="modal-body">\n    <div style="margin: 20px 10px 20px 10px; padding: 10px; border: 1px solid grey;">\n        <strong>Custom class</strong>\n        <p>\n            Give this element a custom "class". Nothing obvious will change in your document.\n            This is for advanced book styling and requires support from the publishing system.\n        </p> \n        <input type="text" placeholder="custom element class" name="custom_class">\n    </div>\n  </div>\n  <div class="modal-footer">\n    <button class="btn btn-primary action submit">Save changes</button>\n    <button class="btn action cancel">Cancel</button>\n  </div>\n</div>';
    blockTemplate = jQuery('<div class="semantic-container aloha-ephemera-wrapper"></div>');
    topControls = jQuery('<div class="semantic-controls-top aloha-ephemera">\n  <a class="copy" title="Copy this element"><i class="icon-copy"></i> Copy element</button>\n</div>');
    blockControls = jQuery('<div class="semantic-controls aloha-ephemera">\n  <button class="semantic-delete" title="Remove this element"><i class="icon-remove"></i></button>\n  <button class="semantic-settings" title="Advanced options for this element"><i class="icon-cog"></i></button>\n</div>');
    blockDragHelper = jQuery('<div class="semantic-drag-helper aloha-ephemera">\n    <div class="title"></div>\n    <div class="body">Drag me to the desired location in the document</div>\n</div>');
    registeredTypes = [];
    copyBuffer = null;
    pluginEvents = [
      {
        name: 'mouseenter',
        selector: '.aloha-block-draghandle',
        callback: function() {
          return jQuery(this).parent('.semantic-container').addClass('drag-active');
        }
      }, {
        name: 'mouseleave',
        selector: '.aloha-block-draghandle',
        callback: function() {
          if (!jQuery(this).parent('.semantic-container').is('.ui-sortable-helper')) {
            return jQuery(this).parent('.semantic-container').removeClass('drag-active');
          }
        }
      }, {
        name: 'mouseenter',
        selector: '.semantic-delete',
        callback: function() {
          return jQuery(this).parents('.semantic-container').first().addClass('delete-hover');
        }
      }, {
        name: 'mouseleave',
        selector: '.semantic-delete',
        callback: function() {
          return jQuery(this).parents('.semantic-container').removeClass('delete-hover');
        }
      }, {
        name: 'click',
        selector: '.semantic-container .semantic-delete',
        callback: function() {
          return jQuery(this).parents('.semantic-container').first().slideUp('slow', function() {
            return jQuery(this).remove();
          });
        }
      }, {
        name: 'click',
        selector: '.semantic-container .semantic-controls-top .copy',
        callback: function(e) {
          var $element;
          $element = jQuery(this).parents('.semantic-container').first();
          return Copy.buffer($element.outerHtml());
        }
      }, {
        name: 'mouseover',
        selector: '.semantic-container .semantic-controls-top .copy',
        callback: function(e) {
          var $elements;
          $elements = jQuery(this).parents('.semantic-container');
          return $elements.removeClass('copy-preview').first().addClass('copy-preview');
        }
      }, {
        name: 'mouseout',
        selector: '.semantic-container .semantic-controls-top .copy',
        callback: function(e) {
          return jQuery(this).parents('.semantic-container').removeClass('copy-preview');
        }
      }, {
        name: 'click',
        selector: '.semantic-container .semantic-settings',
        callback: function(e) {
          var $element, dialog, elementName;
          if (jQuery('.semantic-settings.modal:visible').length) {
            return;
          }
          dialog = jQuery(DIALOG_HTML);
          dialog.modal('show');
          dialog.css({
            'margin-top': (jQuery(window).height() - dialog.height()) / 2,
            'top': '0'
          });
          $element = jQuery(this).parents('.semantic-controls').siblings('.aloha-oer-block');
          elementName = getLabel($element);
          dialog.find('h3').text('Edit options for this ' + elementName);
          dialog.find('[name=custom_class]').val($element.attr('data-class'));
          return dialog.data('element', $element);
        }
      }, {
        name: 'click',
        selector: '.modal.semantic-settings .action.cancel',
        callback: function(e) {
          var $dialog;
          $dialog = jQuery(this).parents('.modal');
          return $dialog.modal('hide');
        }
      }, {
        name: 'click',
        selector: '.modal.semantic-settings .action.submit',
        callback: function(e) {
          var $dialog, $element;
          $dialog = jQuery(this).parents('.modal');
          $dialog.modal('hide');
          $element = $dialog.data('element');
          $element.attr('data-class', $dialog.find('[name=custom_class]').val());
          if ($element.attr('data-class') === '') {
            return $element.removeAttr('data-class');
          }
        }
      }, {
        name: 'mouseover',
        selector: '.semantic-container',
        callback: function() {
          var label, wrapped;
          jQuery(this).parents('.semantic-container').removeClass('focused');
          if (!jQuery(this).find('.focused').length) {
            jQuery(this).addClass('focused');
          }
          wrapped = jQuery(this).find('.aloha-oer-block').first();
          label = wrapped.length && blockIdentifier(wrapped);
          return jQuery(this).find('.aloha-block-handle').first().attr('title', "Drag this " + label + " to another location");
        }
      }, {
        name: 'mouseout',
        selector: '.semantic-container',
        callback: function() {
          return jQuery(this).removeClass('focused');
        }
      }, {
        name: 'blur',
        selector: '[placeholder],[hover-placeholder]',
        callback: function() {
          var $el;
          $el = jQuery(this);
          if (!$el.text().trim() && !$el.find('.aloha-oer-block').length) {
            return $el.empty();
          }
        }
      }
    ];
    insertElement = function(element) {};
    getType = function($element) {
      var type, _i, _len;
      if ($element.is('.semantic-container')) {
        $element = $element.find('.aloha-oer-block').first();
      }
      for (_i = 0, _len = registeredTypes.length; _i < _len; _i++) {
        type = registeredTypes[_i];
        if ($element.is(type.selector)) {
          return type;
        }
      }
    };
    getLabel = function($element) {
      var _ref;
      return (_ref = getType($element)) != null ? _ref.getLabel($element) : void 0;
    };
    blockIdentifier = function($element) {
      var c, classes, elementName, label;
      label = getLabel($element);
      if (label) {
        return elementName = label.toLowerCase();
      } else {
        classes = (function() {
          var _i, _len, _ref, _results;
          _ref = $element.attr('class').split(/\s+/);
          _results = [];
          for (_i = 0, _len = _ref.length; _i < _len; _i++) {
            c = _ref[_i];
            if (!/^aloha/.test(c)) {
              _results.push(c);
            }
          }
          return _results;
        })();
        return elementName = classes.length && ("element (class='" + (classes.join(' ')) + "')") || 'element';
      }
    };
    activate = function($element) {
      var $body, $title, controls, label, options, top, type;
      if (!($element.is('.semantic-container') || ($element.is('.alternates') && $element.parents('figure').length))) {
        $element.addClass('aloha-oer-block');
        if ($element.parent().is('.aloha-editable')) {
          jQuery('<p class="aloha-oer-ephemera-if-empty"></p>').insertBefore($element);
          jQuery('<p class="aloha-oer-ephemera-if-empty"></p>').insertAfter($element);
        }
        type = getType($element);
        controls = blockControls.clone();
        top = topControls.clone();
        label = blockIdentifier($element);
        controls.find('.semantic-delete').attr('title', "Remove this " + label);
        controls.find('.semantic-settings').attr('title', "Advanced options for this " + label);
        top.find('.copy').attr('title', "Copy this " + label);
        top.find('.copy').contents().last().replaceWith(" Copy " + label);
        if (!type) {
          $element.wrap(blockTemplate).parent().append(controls).prepend(top).alohaBlock({
            'aloha-block-type': 'semanticBlock'
          });
        } else {
          if (type.options) {
            if (typeof type.options === 'function') {
              options = type.options($element);
            } else {
              options = type.options;
            }
            if (options.buttons) {
              if (__indexOf.call(options.buttons, 'settings') < 0) {
                controls.find('button.semantic-settings').remove();
              }
              if (__indexOf.call(options.buttons, 'copy') < 0) {
                top.find('a.copy').remove();
              }
            }
          }
          $element.wrap(blockTemplate).parent().append(controls).prepend(top).alohaBlock({
            'aloha-block-type': 'semanticBlock'
          });
          type.activate($element);
          return;
        }
        $element.children('[placeholder],[hover-placeholder]').andSelf().filter('[placeholder],[hover-placeholder]').each(function() {
          if (!jQuery(this).text().trim()) {
            return jQuery(this).empty();
          }
        });
        $title = $element.children('.title').first();
        $title.attr('hover-placeholder', 'Add a title');
        $title.aloha();
        $body = $element.contents().not($title);
        return jQuery('<div>').addClass('body aloha-block-dropzone').appendTo($element).aloha().append($body);
      }
    };
    deactivate = function($element) {
      var $title, content, type;
      $element.removeClass('aloha-oer-block ui-draggable');
      $element.removeAttr('style');
      type = getType($element);
      if (type) {
        type.deactivate($element);
        return;
      }
      $title = $element.children('.title').first().mahalo().removeClass('aloha-editable aloha-block-blocklevel-sortable ui-sortable').removeAttr('hover-placeholder').removeAttr('id');
      content = $element.children('.body');
      if (content.is(':empty')) {
        content.remove();
      } else {
        $element.children('.body').contents().unwrap();
      }
      return $element.attr('data-unknown', 'true');
    };
    bindEvents = function(element) {
      var event, i, _results;
      if (element.data('oerBlocksInitialized')) {
        return;
      }
      element.data('oerBlocksInitialized', true);
      event = void 0;
      i = void 0;
      i = 0;
      _results = [];
      while (i < pluginEvents.length) {
        event = pluginEvents[i];
        element.on(event.name, event.selector, event.callback);
        _results.push(i++);
      }
      return _results;
    };
    cleanIds = function(content) {
      var element, elements, i, id, ids, _i, _ref, _results;
      elements = content.find('[id]');
      ids = {};
      _results = [];
      for (i = _i = 0, _ref = elements.length; 0 <= _ref ? _i <= _ref : _i >= _ref; i = 0 <= _ref ? ++_i : --_i) {
        element = jQuery(elements[i]);
        id = element.attr('id');
        if (ids[id]) {
          _results.push(element.attr('id', ''));
        } else {
          _results.push(ids[id] = element);
        }
      }
      return _results;
    };
    cleanWhitespace = function(content) {
      return content.find('.aloha-oer-ephemera-if-empty').each(function() {
        var $el;
        $el = jQuery(this);
        if ($el.text().trim().length) {
          return $el.removeClass('aloha-oer-ephemera-if-empty');
        } else {
          return $el.remove();
        }
      });
    };
    Aloha.ready(function() {
      return bindEvents(jQuery(document));
    });
    return Plugin.create('semanticblock', {
      defaults: {
        defaultSelector: 'div:not(.title,.aloha-oer-block,.aloha-editable,.aloha-block,.aloha-ephemera-wrapper,.aloha-ephemera)'
      },
      makeClean: function(content) {
        content.find('.semantic-container').each(function() {
          if (jQuery(this).children().not('.semantic-controls').length === 0) {
            return jQuery(this).remove();
          }
        });
        content.find(".aloha-oer-block").each(function() {
          return deactivate(jQuery(this));
        });
        cleanIds(content);
        return cleanWhitespace(content);
      },
      init: function() {
        var _this = this;
        Ephemera.ephemera().pruneFns.push(function(node) {
          return jQuery(node).removeClass('aloha-block-dropzone aloha-editable-active aloha-editable aloha-block-blocklevel-sortable ui-sortable').removeAttr('contenteditable placeholder').get(0);
        });
        return Aloha.bind('aloha-editable-created', function(e, params) {
          var $root, classes, selector, sortableInterval, type, _i, _len;
          $root = params.obj;
          classes = [];
          for (_i = 0, _len = registeredTypes.length; _i < _len; _i++) {
            type = registeredTypes[_i];
            classes.push(type.selector);
          }
          selector = _this.settings.defaultSelector + ',' + classes.join();
          sortableInterval = setInterval(function() {
            if ($root.data('sortable')) {
              clearInterval(sortableInterval);
              if ($root.data('disableDropTarget')) {
                $root.removeClass('aloha-block-blocklevel-sortable aloha-block-dropzone');
              }
              $root.sortable('option', 'helper', 'clone');
              $root.sortable('option', 'appendTo', jQuery('#content').parent());
              $root.sortable('option', 'change', function(e, ui) {
                return ui.item.data("disableDrop", ui.placeholder.parent().data('disableDropTarget'));
              });
              $root.sortable('option', 'stop', function(e, ui) {
                var $element, _ref;
                if (ui.item.data('disableDrop')) {
                  jQuery(this).sortable("cancel");
                  return;
                }
                $element = jQuery(ui.item);
                if ($element.is(selector)) {
                  activate($element);
                }
                if ((_ref = getType($element)) != null) {
                  if (typeof _ref.onDrop === "function") {
                    _ref.onDrop($element);
                  }
                }
                Aloha.activeEditable.smartContentChange({
                  type: 'block-change'
                });
                return $element.removeClass('drag-active');
              });
              $root.sortable('option', 'placeholder', 'aloha-oer-block-placeholder aloha-ephemera');
            }
            return 100;
          });
          if ($root.is('.aloha-root-editable')) {
            $root.find(selector).each(function() {
              if (!jQuery(this).parents('.semantic-drag-source').length) {
                return activate(jQuery(this));
              }
            });
            return jQuery('.semantic-drag-source').children().each(function() {
              var element, elementLabel;
              element = jQuery(this);
              elementLabel = (element.data('type') || element.attr('class')).split(' ')[0];
              return element.draggable({
                connectToSortable: $root,
                appendTo: jQuery('#content'),
                revert: 'invalid',
                helper: function() {
                  var helper;
                  helper = jQuery(blockDragHelper).clone();
                  helper.find('.title').text(elementLabel);
                  return helper;
                },
                start: function(e, ui) {
                  $root.addClass('aloha-block-dropzone');
                  return jQuery(ui.helper).addClass('dragging');
                },
                refreshPositions: true
              });
            });
          }
        });
      },
      insertAtCursor: function(template) {
        var $element, range;
        $element = jQuery(template);
        range = Aloha.Selection.getRangeObject();
        $element.addClass('semantic-temp');
        GENTICS.Utils.Dom.insertIntoDOM($element, range, Aloha.activeEditable.obj);
        $element = Aloha.jQuery('.semantic-temp').removeClass('semantic-temp');
        return activate($element);
      },
      appendElement: function($element, target) {
        $element.addClass('semantic-temp');
        target.append($element);
        $element = Aloha.jQuery('.semantic-temp').removeClass('semantic-temp');
        return activate($element);
      },
      register: function(plugin) {
        registeredTypes.push(plugin);
        if (plugin.ignore) {
          return this.settings.defaultSelector += ':not(' + plugin.ignore + ')';
        }
      },
      registerEvent: function(name, selector, callback) {
        return pluginEvents.push({
          name: name,
          selector: selector,
          callback: callback
        });
      }
    });
  });

}).call(this);
