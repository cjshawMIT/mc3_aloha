var VCB = (function (window, document, $, vcb, undefined) {
    // draw the tree, using passed in tree data
    // Toggle children
    function toggle(d) {
      if (d.children) {
        d._children = d.children;
        d.children = null;
      }
      else {
        d.children = d._children;
        d._children = null;
      }
    }

    function color(d) {
      return d._children ? "#3182bd" : d.children ? "#c6dbef" : "#fd8d3c";
    }

    function toggleAll(d) {
      if (d.children) {
        d.children.forEach(toggleAll);
        toggle(d);
      }
    }

    var	i = 0,
        m = [50, 100, 50, 100],
        w = 400,
        h = 4000,
        barHeight = 30,
        barWidth = 0.4 * w,
        duration = 400,
        ry = 5,
        rx = 5;

    var diagonal = d3.svg.diagonal()
        .projection(function(d) { return [d.y, d.x]; });

    var tree = d3.layout.tree()
        .size([h - m[0] - m[2], w - m[1] - m[3]]);


    vcb.updateChart = function (root, source, vis) {
        // Compute the flattened node list. TODO use d3.layout.hierarchy.
        var nodes = tree.nodes(root);

        // Compute the "layout".
        nodes.forEach(function(n, i) {
            n.x = (i+1) * barHeight;
        });

        // Update the nodes…
        var node = vis.selectAll("g.node")
          .data(nodes, function(d) { return d.id || (d.id = ++i); });

        var nodeEnter = node.enter().append("svg:g")
          .attr("class", "node")
          .attr("transform", function(d) {
                    return "translate(" + source.y0 + "," + source.x0 + ")"; })
          .attr('id', function(d) {return d.item_id})
          .style("opacity", 1e-6)
          .on("mouseover", function(d) {
              if (d.title){
                  // initialize the tooltip
                  var div = d3.select("body").append("div")
                      .attr("class", "tooltip")
                      .style("opacity", 0);
                  div.transition()
                      .duration(200)
                      .style("opacity", .9);
                  div.html(d.title);

                  if (d3.event.pageX || d3.event.pageY) {
                      var x = d3.event.pageX;
                      var y = d3.event.pageY;
                  } else if (d3.event.clientX || d3.event.clientY) {
                      var x = d3.event.clientX + document.body.scrollLeft +
                              document.documentElement.scrollLeft;
                      var y = d3.event.clientY + document.body.scrollTop +
                              document.documentElement.scrollTop;
                  }
                  div.style("left", (x + 50) + "px")
                     .style("top", y + "px");
              }
          })
          .on("mouseout", function(d) {
              $('.tooltip').remove();
          })
          .on("click", function(d) {
              var spin_target = document.getElementById('main_status_box');
              var spinner = new Spinner().spin(spin_target);
              // Get the children data if not already present
              if (d._children == null || d.item_class == "root") {
                 if (d.item_class != 'asset') {
                      spinner.stop();
                  }
              }
              else {
                  if (d._children.length === 0) {
                  // do ajax call to get children and append to d if don't already exist
                      var item_class = d.item_class;
                      var bank = d.bank;
                      var item_id = d.item_id;

                      if (item_class != 'asset') {
                        $.ajax({
                            type: "GET",
                            url: "get_children/",
                            data: {
                                'item_id': item_id,
                                'bank': bank,
                                'itemClass': item_class,
                            },
                            success: function(children) {
                                spinner.stop();
                                console.log(children);
                                d.children = children;
                                d.children.forEach(toggleAll);
                                vcb.updateChart(root, d, vis);
                            },
                            error: function(xhr, status, error) {
                                spinner.stop();
                                alert(error);
                            }
                        });
                    }
                  } else {
                      spinner.stop();
                  }
              }
              //d.children.forEach(toggleAll);
              toggle(d);
              vcb.updateChart(root, d, vis);
              if (d.urls) {
                  vcb.playvid(d.item_id, spinner);
              }
          });

        // Enter any new nodes at the parent's previous position.
        nodeEnter.append("svg:rect")
          .attr("y", -barHeight / 2)
          .attr("height", barHeight)
          .attr("width", barWidth)
          .attr("rx", rx)
          .attr("ry", ry)
          .style("fill", color);

        nodeEnter.append("svg:text")
          .attr("dy", 3.5)
          .attr("dx", 5.5)
          .text(function(d) { return d.name; });

        // On this transition, do any jumpto clicking...?
        // https://groups.google.com/forum/?fromgroups=#!topic/d3-js/WC_7Xi6VV50
        function endall(transition, callback) {
           var n = 0;
           transition
               .each(function() { ++n; })
               .each("end", function() {
                   if (!--n) {
                       callback.apply(this, arguments);
                   }
               });
         }

        // Transition nodes to their new position.
        nodeEnter.transition()
          .duration(duration)
          .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
          .style("opacity", 1)
          .call(endall, function() {
              if (jumpto) {
                  $('#' + jumpobjs[jumpind]).d3Click();
                  if (--jumpnum === 0) {
                      jumpto = false;
                  }
                  jumpind++;
              }
          });

        node.transition()
          .duration(duration)
          .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
          .style("opacity", 1)
        .select("rect")
          .style("fill", color)
          .call(endall, function() {
              if (jumpto) {
                  $('#' + jumpobjs[jumpind]).d3Click();
                  if (--jumpnum === 0) {
                      jumpto = false;
                  }
                  jumpind++;
              }
          });

        // Transition exiting nodes to the parent's new position.
        node.exit().transition()
          .duration(duration)
          .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
          .style("opacity", 1e-6)
          .remove();

        // Update the links…
        var link = vis.selectAll("path.link")
          .data(tree.links(nodes), function(d) { return d.target.id; });

        // Enter any new links at the parent's previous position.
        link.enter().insert("svg:path", "g")
          .attr("class", "link")
          .attr("d", function(d) {
            var o = {x: source.x0, y: source.y0};
            return diagonal({source: o, target: o});
          })
        .transition()
          .duration(duration)
          .attr("d", diagonal);

        // Transition links to their new position.
        link.transition()
          .duration(duration)
          .attr("d", diagonal);

        // Transition exiting nodes to the parent's new position.
        link.exit().transition()
          .duration(duration)
          .attr("d", function(d) {
            var o = {x: source.x, y: source.y};
            return diagonal({source: o, target: o});
          })
          .remove();

        // Stash the old positions for transition.
        nodes.forEach(function(d) {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    };

    vcb.draw_new_tree = function (tree_data, spinner, container, tree_target) {
        spinner.stop();
        console.log(tree_data);

        if (!$(tree_target).hasClass('canvascontainer')) {
            $(tree_target).addClass('canvascontainer');
        }
        $('#recent_table').remove();
        d3.selectAll("svg").remove();
        //================
        // Also from Mike Bostock http://bl.ocks.org/mbostock/1093025
        //  And http://www.triballabs.net/2013/02/the-basics-of-responsive-d3-charts/


        //	Updated on Jul 12, 2013. cshaw
        //	Different menu format...draw the tree onclick events for menu items in sidebar.
        //	  Get JSON file from ajax call to drawtree...pass it some parameters that are
        //	  kept in the data fields (data-tree-type and data-class)
        // From http://bl.ocks.org/mbostock/1093025
        var root;

        var vis = d3.select(tree_target).append("svg:svg");
        var new_width = 0.9 * $('svg').parent().width();

        barWidth = 0.4 * new_width;
        var adj_height = barHeight/2;
        var adj_width = 0.6 * barWidth;
        m = [adj_height, adj_width, adj_height, adj_width];
        tree.size([h - m[0] - m[2], new_width - m[1] - m[3]]);

        w = new_width - m[1] - m[3];

        vis.attr("width", new_width)
            .attr("height", h)
            .attr("id", "tree_svg")
          .append("svg:g")
            //.attr("transform", "translate(20,20)")
            .attr("class", "chartContainer");


        vis.append("g")
            .attr("class", "x axis");

        vis.append("g")
            .attr("class", "y axis");

        root = tree_data[0];
        root.x0 = 30;
        root.y0 = 0;

        // initialize the display to show a few nodes.
        root.children.forEach(toggleAll);

        vcb.updateChart( root, root, vis );

        // End code from Mike Bostock
        // ===================
    };
    return vcb;
})(this, document, jQuery, VCB || {});