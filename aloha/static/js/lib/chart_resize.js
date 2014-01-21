//from http://www.triballabs.net/2013/02/the-basics-of-responsive-d3-charts/
function resizeChart() {
	// update the box size, from here
	// http://www.triballabs.net/2013/02/the-basics-of-responsive-d3-charts/
	var padding = {top: 20, right: 20, bottom: 20, left: 20};
	
	var prevChartWidth = 0, prevChartHeight = 0;
	
	var chartWidth = document.getElementById('tree').getBoundingClientRect().width - padding.left - padding.right;
	var chartHeight = document.getElementById('tree').getBoundingClientRect().height - padding.top - padding.bottom;
	
	// only update if chart size has changed
	if ((prevChartWidth != chartWidth) ||
	(prevChartHeight != chartHeight))
	{
		prevChartWidth = chartWidth;
		prevChartHeight = chartHeight;
		
		barWidth = 0.6 * chartWidth;
		
		//set the width and height of the SVG element
//		vis.attr("width", chartWidth + padding.left + padding.right)
//		.attr("height", chartHeight + padding.top + padding.bottom);
		
		updateChart( root );
//		console.log( 'svg resized' );
	}
}

var resizeTimer;
window.onresize = function(event) {
	clearTimeout(resizeTimer);
	resizeTimer = setTimeout(function() {
		resizeChart();
//		console.log( 'resized' );
	}, 100);
}