// Modified from the OER Definition plugin
(function() {
  define(['aloha', 'aloha/plugin', 'jquery', 'aloha/ephemera', 'ui/ui', 'ui/button', 'semanticblock/semanticblock-plugin', 'css!../../mc3definition/css/mc3definition-plugin.css'], function(Aloha, Plugin, jQuery, Ephemera, UI, Button, semanticBlock) {
    var TEMPLATE;
    TEMPLATE = '<dl class="mc3definition"><dt></dt><dd></dd></dl>';
    return Plugin.create('mc3definition', {
      getLabel: function($element) {
        return 'MC3 Definition';
      },
      activate: function($element) {
        var $definition, term;
        term = $element.children('dt').contents();
        $definition = $element.children('dd').contents();
        jQuery('<div>').append(term)
                .addClass('term')
                .attr('placeholder', 'Enter the term to be defined here')
                .appendTo($element)
                .wrap('<div class="term-wrapper"></div>')
                .aloha();
        jQuery('<div>').addClass('body')
                .addClass('aloha-block-dropzone')
                .attr('placeholder', "Type the definition here.")
                .appendTo($element)
                .aloha()
                .append($definition);
        // Bind events on the term to search for the topic in MC3
        // when the contenteditable is blurred
        jQuery($element).find('.term[contenteditable]')
                .on('focus', function () {
                    var $this = $(this);
                    $this.data('before', $this.html().trim().replace(/[<]br[^>]*[>]/gi,""));
                    return $this;
                }).on('blur', function () {
                    var _this = $(this);
                    var new_value = _this.html().trim().replace(/[<]br[^>]*[>]/gi,"");
                    if (_this.data('before') !== new_value) {
                        _this.data('new_value', new_value);
                        MC3UTILS.search_bank_objectives(_this);
                    }
                });
        return $element.find('dt,dd')
                .remove();
      },
      deactivate: function($element) {
        var $definition, term;
        term = $element.find('.term').text();
        $definition = $element.children('.body').contents();
        if (!$definition.length) {
          $definition = $element.children('dd').contents();
        }
        $element.empty();
        jQuery('<dt>').text(term).appendTo($element);
        return jQuery('<dd>').html($definition).appendTo($element);
      },
      selector: 'dl.mc3definition',
      init: function() {
        UI.adopt("insert-mc3definition", Button, {
          click: function() {
            return semanticBlock.insertAtCursor(jQuery(TEMPLATE));
          }
        });
        UI.adopt("insertMC3Definition", Button, {
          click: function() {
            return semanticBlock.insertAtCursor(jQuery(TEMPLATE));
          }
        });
        return semanticBlock.register(this);
      }
    });
  });

}).call(this);
