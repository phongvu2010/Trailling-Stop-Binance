var myPlot = document.getElementById('plotly-div');

var isUnderRelayout = false;
myPlot.on('plotly_relayout', function(relayoutData) {
    if(isUnderRelayout != true) {
        isUnderRelayout = true;

        // get the start and end dates of current 'view'
        var start = relayoutData['xaxis.range'][0];
        var end = relayoutData['xaxis.range'][1];	

        // get the index of the start and end dates
		var xstart = myPlot.data[0].x.map(function(e) { return e; }).indexOf(start.substring(0, 10));
        var xend = myPlot.data[0].x.map(function(e) { return e; }).indexOf(end.substring(0, 10));

        if(xstart < 0) { xstart = 0;} // sometimes the date is before the data and returns -1

        // get the min and max's
        var low = Math.min.apply(null, myPlot.data[0].low.slice(xstart, xend));
		var high = Math.max.apply(null, myPlot.data[0].high.slice(xstart, xend));

        // update the yaxis range and set flag to false
        var update = {'yaxis.range': [low, high]};	
		Plotly.relayout(myPlot, update).then(() => {isUnderRelayout = false})
    }
});