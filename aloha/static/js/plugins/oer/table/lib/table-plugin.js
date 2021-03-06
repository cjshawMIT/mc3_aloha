define([
  'aloha',
  'aloha/plugin',
  'jquery',
  'ui/ui',
  'ui/button',
  'PubSub',
  'ui/dialog',
  'aloha/ephemera',
  'semanticblock/semanticblock-plugin',
  'table/table-create-layer',
  'css!../../../common/table/css/table.css'],
function(Aloha, plugin, $, Ui, Button, PubSub, Dialog, Ephemera, semanticBlock, CreateLayer) {
    "use strict";

	var GENTICS = window.GENTICS;

	function prepareRangeContainersForInsertion(range, table){
		var	eNode = range.endContainer,
			sNode = range.startContainer,
			eNodeLength =(eNode.nodeType == 3)
				? eNode.length
				: eNode.childNodes.length;		
		
		if(sNode.nodeType == 3 &&
				sNode.parentNode.tagName == 'P' &&
					sNode.parentNode.childNodes.length == 1 &&
						/^(\s|%A0)$/.test( escape( sNode.data))){
			sNode.data = '';
			range.startOffset = 0;
			
			// In case ... <p> []</p>
			if(eNode == sNode){
				range.endOffset = 0;
			}
		}
		
		// If the table is not allowed to be nested inside the startContainer,
		// then it will have to be split in order to insert the table.
		// We will therefore check if the selection touches the start and/or
		// end of their container nodes.
		// If they do, we will mark their container so that after they are
		// split we can check whether or not they should be removed
		if(!GENTICS.Utils.Dom.allowsNesting(
				sNode.nodeType == 3 ? sNode.parentNode : sNode, table)){
			
			if(range.startOffset == 0){
				$( sNode.nodeType == 3 ? sNode.parentNode : sNode)
					.addClass( 'aloha-table-cleanme');
			}
			
			if(range.endOffset == eNodeLength){
				$( eNode.nodeType == 3 ? eNode.parentNode : eNode)
					.addClass( 'aloha-table-cleanme');
			}
		}
	}

	function cleanupAfterInsertion(){
		var dirty = $('.aloha-table-cleanme').removeClass(
						'aloha-table-cleanme');
		
		for (var i=0; i<dirty.length; i++){
			if ($.trim($(dirty[i]).html()) == '' &&
					!GENTICS.Utils.Dom.isEditingHost(dirty[i])){
				$(dirty[i]).remove();
			}
		}
	}

    function createRow(cols, tagname){
        tagname = tagname || 'td';
        var tr = document.createElement('tr');
        for (var i=0; i<cols; i++) {
            var text = document.createTextNode('\u00a0');
            var td = document.createElement(tagname);
            td.appendChild(text);
            tr.appendChild(td);
        }
        return tr;
    }

    // Re-implementing this, cause Aloha.Selection gets out of sync
    // and causes weirdness.
    var getSelection = (function(window, document){
        if (window.getSelection) {
            return window.getSelection;
        } else if (document.getSelection) {
            return document.getSelection;
        }
        return function(){ throw "getSelection not implemented"; }
    })(window, document);

    function prepareTable(plugin, table){
        // Wrap table in ui-wrappper
        var w1 = $('<div class="canvas-wrap aloha-ephemera-wrapper" />');
        var w2 = $('<div class="table canvas aloha-ephemera-wrapper" />');
        var w3 = $('<div class="canvas-inner aloha-ephemera-wrapper" />');

        table.wrap(w1).wrap(w2).wrap(w3);

        // glue a mouseover event onto it
        table.on('mouseenter', function(e){
            // We will later use this to bring up ui
            //console && console.log(e.target);
        });
        table.on('mouseleave', function(e){
            // We will later use this to hide ui
            //console && console.log(e.target);
        });
    }

    function placeCursor(cell){
        var range = document.createRange();
        range.setStart(cell.get(0), 0);
        range.setEnd(cell.get(0), 0);
        getSelection().removeAllRanges();
        getSelection().addRange(range);
    }
  
    var plugin;

    return plugin.create('table', {
        defaults: {
        },
        selector: 'table',
        getLabel: function() {
          return 'Table';
        },
        activate: function($element) {

          var $body = $element.wrap('<div class="body">')
            .parent()
            .aloha()
            .data('disableDropTarget', true)
            ;

          // this reference is broken by the above rejiggering
          $element = $body.find('table').first(); 

          // wraps element in a bunch of wrappers i'm not totally sure are necessary
          prepareTable(plugin, $element);
        },
        deactivate: function($element) {
          $element.parents('.body').first().children().unwrap();
        },
        init: function(){
            plugin = this;
            this.createLayer = new CreateLayer(this);
            this.initButtons();

            semanticBlock.register(plugin);

            semanticBlock.registerEvent('click', 'table', this.clickTable);

            // Mark some classes as ephemeral
            Ephemera.classes('aloha-current-cell', 'aloha-current-row', 'add-column-before', 'add-column-after');

            Aloha.bind('aloha-editable-created', function(event, editable){
                var config = plugin.getEditableConfig(editable.obj);

                /* If a config is available and this plugin is not explicitly
                   enabled for this editable, disable it. In the absence of
                   a specific configuration, default to enabling table
                   events. */
                if(config && config.enabled != undefined && !config.enabled){
                    return
                }
                editable.obj.on('keydown', null, 'return', function(e){
                    var $canvas = editable.obj;
                    var $currentTableCell = $canvas.find('.aloha-current-cell');
                    var inTable = ( $currentTableCell.length > 0 ? true : false );
                    if ( inTable ) {
                        // default action for 'return' is to insert a new line,
                        // so we want this and thus do not call e.preventDefault() here
                        e.stopPropagation(); 
                        e.stopImmediatePropagation();
                    }
                });
                // Aloha has its own 'keydown' event handler which will fire before the above handler
                // and which will cause havoc ... havoc I tell you. Tables will be split!!!
                // Change the order of the event handlers to suit our own purposes.
                // XXX: Modifying internal structures like this is evil
                // and unsupported. This will break again in future.
                var handlers = $._data(editable.obj[0], 'events')['keydown'];
                handlers.unshift(handlers.pop());

                editable.obj.bind('keydown', 'tab shift+tab', function(e){
                    var $cell = $(
                        getSelection().focusNode).closest('td,th');
                    if ($cell.length > 0){
                        var next = function(ob, filter){
                            if (e.shiftKey){
                                return ob.prev(filter);
                            } else {
                                return ob.next(filter);
                            }
                        }
                        var border = 'td:last-child,th:last-child';
                        if (e.shiftKey){
                            border = 'td:first-child,th:first-child';
                        }
                        if ($cell.is(border)) {
                            var nextrow = next($cell.closest('tr'), 'tr');
                            if (nextrow.length > 0){
                                var offset = e.shiftKey ? nextrow[0].cells.length-1 : 0;
                                var nextcell = $(nextrow[0].cells[offset]);
                                plugin.focusCell(nextcell);
                            } else {
                                // Last column, last row
                                // Add more
                                var newrow = plugin.addRowAfter();
                                if (newrow !== null){
                                    plugin.focusCell($(newrow).find('td,th').first());
                                }
                            }
                        } else {
                            var nextcell = next($cell, 'td,th');
                            plugin.focusCell(nextcell);
                        }
                    }
                    e.preventDefault();
                    e.stopPropagation();
                });
                // Disable firefox's inline table editing.
                try {
                    document.execCommand("enableInlineTableEditing", null, false);
                } catch(ignore){}
                // Place the cursor at the start of the editable. If you don't
                // do this, Firefox goes weird when placing the cursor in a
                // table cell.
                placeCursor(editable.obj);
            });
            PubSub.sub('aloha.selection.context-change', function(m){
                var table = $(m.range.markupEffectiveAtStart)
                    .parent('table').eq(0);
                if (table.length > 0) {
                    // We're inside a table, disable table insertion, enable
                    // others
                    plugin._createTableButton.enable(false);
                    plugin._addrowbeforeButton.enable(true);
                    plugin._addrowafterButton.enable(true);
                    plugin._deleterowButton.enable(true);
                    plugin._deleteColumnButton.enable(true);
                    plugin._addColumnBefore.enable(true);
                    plugin._addColumnAfter.enable(true);
                    plugin._deleteTableButton.enable(true);
                    if(!table.find('th').length){
                        // only enable header insertion if we have no header
                        plugin._addHeaderRow.enable(true);
                    }
                } else {
                    // Disable table functions, enable table insertion
                    plugin._createTableButton.enable(true);
                    plugin._addrowbeforeButton.enable(false);
                    plugin._addrowafterButton.enable(false);
                    plugin._deleterowButton.enable(false);
                    plugin._deleteColumnButton.enable(false);
                    plugin._addColumnBefore.enable(false);
                    plugin._addColumnAfter.enable(false);
                    plugin._deleteTableButton.enable(false);
                    plugin._addHeaderRow.enable(false);
                }
            });
            $('body').on('click', function(e){
                // Click outside table deselects current row and cell
                if(!e.isDefaultPrevented() &&
                        $(e.target).parents('.aloha-editable').length){
                    plugin.currentCell.length && plugin.currentCell.removeClass('aloha-current-cell');
                    plugin.currentRow.length && plugin.currentRow.removeClass('aloha-current-row');
                    plugin.currentRow = $();
                    plugin.currentCell = $();
                    plugin.currentTable = $();
                }
            });
        },
        initButtons: function(){
            var that = this;
            this._createTableButton = Ui.adopt("createTable", Button, {
                tooltip: "Add a new table",
                icon: "aloha-icon aloha-icon-createTable",
                scope: 'Aloha.continuoustext',
                click: function(e){
                    that.createLayer.show(e);
                }
            });

            this._addrowbeforeButton = Ui.adopt("addrowbefore", Button, {
                tooltip: "Add new row before",
                icon: "aloha-icon aloha-icon-addrowbefore",
                scope: this.name + '.row',
                click: function(){
                    if(!that.currentRow.length){ return; }
                    var colcount = that.currentRow.find('td,th').length;
                    var newrow = createRow(colcount);
                    that.currentRow.before(newrow);
                },
                preview: function(e){
                    that.currentRow.length && that.currentRow.addClass("add-row-before");
                },
                unpreview: function(e){
                    that.currentRow.length && that.currentRow.removeClass("add-row-before");
                }
            });

            this._addrowafterButton = Ui.adopt("addrowafter", Button, {
                tooltip: "Add new row after",
                icon: "aloha-icon aloha-icon-addrowafter",
                scope: this.name + '.row',
                click: function(){
                    that.addRowAfter();
                },
                preview: function(e){
                    that.currentRow.length && that.currentRow.addClass("add-row-after");
                },
                unpreview: function(e){
                    that.currentRow.length && that.currentRow.removeClass("add-row-after");
                }
            });
            this._deleterowButton = Ui.adopt("deleterow", Button, {
                tooltip: "Delete row",
                icon: "aloha-icon aloha-icon-deleterow",
                scope: this.name + '.row',
                click: function(){
                    if(!that.currentRow.length){ return; }
                    that.currentRow.remove();
                    that.currentRow = $();
                    if(that.currentTable.find("td,th").length==0){
                        that.currentTable.remove();
                        that.currentTable = $();
                    }
                },
                preview: function(){
                    that.currentRow.length && that.currentRow.addClass("delete-row");
                },
                unpreview: function(){
                    that.currentRow.length && that.currentRow.removeClass("delete-row");
                }
            });
            this._deleteColumnButton = Ui.adopt("deletecolumn", Button, {
                tooltip: "Delete column",
                icon: "aloha-icon aloha-icon-deletecolumn",
                scope: this.name + '.column',
                click: function(){
                    if(!that.currentCell.length){ return; }
                    var idx = that.currentCell[0].cellIndex;
                    that.currentTable.find("tr").each(function(){
                        this.removeChild(this.cells[idx]);
                    });
                    // If the table is now devoid of any rows, delete it
                    if(that.currentTable.find("td,th").length==0){
                        that.currentTable.remove();
                        that.currentTable = $();
                    }
                },
                preview: function(){
                    if(!that.currentCell.length){ return; }
                    var idx = that.currentCell[0].cellIndex;
                    that.currentTable.find("tr").each(function(){
                        $(this.cells[idx]).addClass("delete-column");
                    });
                },
                unpreview: function(){
                    that.currentTable.find('td,th')
                        .removeClass('delete-column');
                }
            });
            this._deleteTableButton = Ui.adopt("deletetable", Button, {
                tooltip: "Delete table",
                icon: "aloha-icon aloha-icon-deletetable",
                scope: this.name,
                click: function(){
                    that.currentTable.parents('.semantic-container').remove();
                    that.currentTable = $();
                },
                preview: function(){
                    that.currentTable.addClass("delete-table");
                },
                unpreview: function(){
                    that.currentTable.removeClass('delete-table');
                }
            });
            this._addColumnBefore = Ui.adopt("addcolumnbefore", Button, {
                tooltip: "Add new column before",
                icon: "aloha-icon aloha-icon-addcolumnbefore",
                scope: this.name + '.column',
                click: function(){
                    if(!that.currentCell.length){ return; }
                    var idx = that.currentCell[0].cellIndex;
                    var table = that.currentCell.parents('.aloha-editable table');
                    table.find("tr").each(function(){
                        var toclone = $(this).find('td,th').eq(idx);
                        var newcell = toclone.clone().html('\u00a0');
                        toclone.before(newcell);
                    });
                },
                preview: function(e){
                    if(!that.currentCell.length){ return; }
                    var idx = that.currentCell[0].cellIndex;
                    that.currentTable.find("tr").each(function(){
                        $(this.cells[idx]).addClass("add-column-before");
                    });
                },
                unpreview: function(e){
                    that.currentTable.find('td,th')
                        .removeClass('add-column-before');
                }
            });
            this._addColumnAfter = Ui.adopt("addcolumnafter", Button, {
                tooltip: "Add new column after",
                icon: "aloha-icon aloha-icon-addcolumnafter",
                scope: this.name + '.column',
                click: function(){
                    if(!that.currentCell.length){ return; }
                    var idx = that.currentCell[0].cellIndex;
                    that.currentTable.find("tr").each(function(){
                        var toclone = $(this).find('td,th').eq(idx);
                        var newcell = toclone.clone().html('\u00a0');
                        toclone.after(newcell);
                    });
                },
                preview: function(e){
                    if(!that.currentCell.length){ return; }
                    var idx = that.currentCell[0].cellIndex;
                    that.currentTable.find("tr").each(function(){
                        $(this.cells[idx]).addClass("add-column-after");
                    });
                },
                unpreview: function(e){
                    that.currentTable.find('td,th')
                        .removeClass('add-column-after');
                }
            });
            this._addHeaderRow = Ui.adopt("addheaderrow", Button, {
                tooltip: "Add header row",
                icon: "aloha-icon aloha-icon-addheaderrow",
                scope: this.name,
                click: function(){
                    if(!that.currentTable.length){ return; }
                    var firstrow = that.currentTable.find('tr').eq(0),
                        colcount = firstrow.find('td,th').length;
                    var newrow = createRow(colcount, 'th');
                    firstrow.before(newrow);
                    // Disable function now to prevent adding another
                    // header row. Also cleanup after preview.
                    that.currentTable.find('tr').slice(0, 2).removeClass("add-row-before");
                    that._addHeaderRow.enable(false);
                },
                preview: function(e){
                    that.currentTable.length && that.currentTable.find('tr').eq(0).addClass("add-row-before");
                },
                unpreview: function(e){
                    // use slice() to remove class from first two rows, cause
                    // adding a new header row means the preview css is now on
                    // the second row.
                    that.currentTable.length && that.currentTable.find('tr').slice(0, 2).removeClass("add-row-before");
                }
            });
            // Disable the table functions by default, they are enabled when
            // a selection is inside a table
            this._addrowbeforeButton.enable(false);
            this._addrowafterButton.enable(false);
            this._deleterowButton.enable(false);
            this._deleteColumnButton.enable(false);
            this._addColumnBefore.enable(false);
            this._addColumnAfter.enable(false);
            this._addHeaderRow.enable(false);
            this._deleteTableButton.enable(false);
        },
        addRowAfter: function(){
            // Factored out because we re-use this when tabbing through the
            // table.
            if(this.currentRow.length){
                var colcount = this.currentRow.find('td,th').length;
                var newrow = createRow(colcount);
                this.currentRow.after(newrow);
                return newrow;
            }
            return null;
        },
        createTable: function(cols, rows, headerrows){
            // Check if there is an active Editable and that it contains an element (= .obj)
            if (Aloha.activeEditable && typeof Aloha.activeEditable.obj !== 'undefined'){
                // create a dom-table object
                var table = document.createElement('table');
                var tableId = table.id = GENTICS.Utils.guid();
                var tbody = document.createElement('tbody');

                // Create headerrows of headers
                for(var i=0; i<headerrows; i++){
                    var tr = document.createElement('tr');
                    // create "cols"-number of columns
                    for (var j = 0; j < cols; j++) {
                        var text = document.createTextNode('\u00a0');
                        var td = document.createElement('th');
                        td.appendChild(text);
                        tr.appendChild(td);
                    }
                    tbody.appendChild(tr);
                }

                // create "rows"-number of rows
                for (var i=0; i<rows; i++){
                    var tr = document.createElement('tr');
                    // create "cols"-number of columns
                    for (var j = 0; j < cols; j++) {
                        var text = document.createTextNode('\u00a0');
                        var td = document.createElement('td');
                        td.appendChild(text);
                        tr.appendChild(td);
                    }
                    tbody.appendChild(tr);
                }
                table.appendChild(tbody);

                semanticBlock.insertAtCursor(table)

                // not sure if this is necessary, but leaving anyway
                cleanupAfterInsertion();
            } else {
                this.error('There is no active Editable where the table can be inserted!');
            }
        },
        clickTable: function(e){
            plugin.currentCell.length && plugin.currentCell.removeClass('aloha-current-cell');
            plugin.currentRow.length && plugin.currentRow.removeClass('aloha-current-row');

            if (plugin.currentCell.attr('class') == '') {
              plugin.currentCell.removeAttr('class')
            }
            if (plugin.currentRow.attr('class') == '') {
              plugin.currentRow.removeAttr('class')
            }

            plugin.currentCell = $(e.target).closest('td,th');
            plugin.currentRow = $(e.target).closest('tr');
            plugin.currentTable = $(e.target).closest('table');
            plugin.currentCell.length && plugin.currentCell.addClass('aloha-current-cell');
            plugin.currentRow.length && plugin.currentRow.addClass('aloha-current-row');

            e.preventDefault();
        },
        focusCell: function(cell){
            placeCursor(cell);
            cell.click();
        },
	      error: function(msg){
            Aloha.Log.error(this, msg);
        },
        currentCell: $(), // Defined when clicked
        currentRow: $(),  // Defined when clicked
        currentTable: $(), // Defined when clicked
        createLayer: undefined // Defined in init above.
    });
});
