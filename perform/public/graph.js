var Graphine = {
    fields: {
        chart: null,
        barHeight: 0,
        rows: 1,
        pps: 0,
        ivalColors: {},
        actColors: {},
        evtColors: {},
        dx:0,
        dy:0
    },
    setChart: function (classname) {
        this.fields.chart = d3.select(classname);
        return this.fields.chart;
    },
    getChart: function () {
        return this.fields.chart
    },
    setDimensions: function (w, h) {
        this.fields.chart.attr('width', w).attr('height', h);
        return this.fields.chart;
    },
    setPixelsPerSecond: function (maxTrialDuration) {
        // maxTrialDuration is in seconds
        var w = this.fields.chart.attr('width');
        this.fields.pps = w / maxTrialDuration;
        if (this.fields.pps < 1) {
            //TODO: throw error
        }
    },
    firstRow: function (row) {
        this.fields.barHeight = this.fields.chart.attr('height') / this.fields.rows;
        var line = this.fields.chart.append('g').attr('id', 'current');
        this.fields.chart.append('g').attr('id', 'past');

        var newrow = this.rowCalcX(row);
        var dy = (this.fields.rows - 1) * this.fields.barHeight;
        line.selectAll("rect").data(newrow).enter().append("rect")
            .attr("transform", function (d, i) {
            return "translate(" + d.x + "," + dy + ")";
        })
            .attr("width", function (d) {
            return d.w;
        }).attr("height", this.fields.barHeight)
           .attr("fill", function (d) {
            return '#'+d.color;
        }).attr('fill-opacity',0.5);
    },
    initActions: function(acts){
    	for(var i=0; i<acts.length; i++){
    		this.fields.actColors[acts[i]['type']] = acts[i]['color'];
    	}
    },
    initEvents: function(evts){
    	for(var i=0; i<evts.length; i++){
    		this.fields.evtColors[evts[i]['name']] = evts[i]['color'];
    	}
    },
    nextRow: function() {
    	//put in new row
    	var i = this.fields.rows;
    	
        var gid = 'trial' + i;
        this.fields.chart.select('#current').attr('id', gid);
        $('#past').append($('#' + gid))
        this.fields.chart.insert('g', '#past').attr('id', 'current');
    	
        var h = this.fields.chart.attr('height');
        var delta = i / (i + 1);
        var move = h / (i + 1);
        var m2 = move*delta;
        this.fields.chart.selectAll('#past rect').each(function () {
            Graphine.appendTransform(d3.select(this), 'translate(0,' + move + ') scale(1.0,' + delta + ')');
        });
         this.fields.chart.selectAll('#past circle').each(function () {
         	var cy = parseFloat(d3.select(this).attr('cy'));
         	var trial = parseInt(d3.select(this).parent().attr('id').replace('trial',''));
         	cy = move*trial - move*0.5;
            d3.select(this).attr('cy',cy);
            //appendTransform('transform','translate(0,' + m2 + ')');
        });

        this.fields.rows++;
        this.fields.barHeight = h / this.fields.rows;
      //  this.fields.dy = (this.fields.rows - 1) * this.fields.barHeight;
        this.fields.dx = 0;
    },
    addInterval: function(ival){
        /* ival = {'name': ..., 'duration': #} */
        var c = '#'+this.fields.ivalColors[ival['name']];
        var w = ival.duration * this.fields.pps;
        this.fields.chart.select("#current").append('rect')
        .attr("transform","translate("+this.fields.dx+","+this.fields.dy+")")
        .attr("width", w)
        .attr("height", this.fields.barHeight)
        .attr("fill",c).attr('fill-opacity',0.5).attr('stroke','#000000');
        this.fields.dx += w;
    },
    addAction: function(hap){
    	console.log(hap);
    	var x = hap.time_occurred * this.fields.pps;
    	var color = '#'+this.fields.actColors[hap['name']];
    	console.log(color);
    	this.fields.chart.select('#current').append('circle')
    	.attr('cx',x)
    	.attr('cy',this.fields.barHeight*0.5)
    	.attr('r',3)
    	.attr('stroke','none')
    	.attr('fill',color);
    },addEvent: function(hap){
    	       console.log(hap);
    	var x = hap.time_occurred * this.fields.pps;
    	var color = '#'+this.fields.evtColors[hap['name']];
    	this.fields.chart.select('#current').append('circle')
    	.attr('cx',x)
    	.attr('cy',this.fields.barHeight*0.5)
    	.attr('r',3)
    	.attr('fill','none')
    	.attr('stroke',color);
    },
    addMark: function(time_occurred){
    	var x = time_occurred * this.fields.pps;
    	this.fields.chart.select('#current').append('circle')
    	.attr('cx',x)
    	.attr('cy',this.fields.barHeight*0.5)
    	.attr('r',3)
    	.attr('stroke','none')
    	.attr('fill','#000000');
    },
    rowCalcX: function (row) {
        var x = 0;
        var len = row.length;
        for (var i = 0; i < len; i++) {
            row[i]['x'] = x;
            row[i]['w'] = row[i].duration * this.fields.pps;
            x += row[i]['w'];
            this.fields.ivalColors[row[i]['name']]=row[i]['color'];
        }
        return row;
    },
    appendTransform: function (selection, transform_str) {
        var orit = selection.attr('transform');
        if (orit == null) {
            orit = '';
        } else {
            orit = orit + ' ';
        }
        selection.attr('transform', orit + transform_str);
    }
};

function initGraph(protocol_obj) {
    Graphine.setChart('.rasta');
    Graphine.setDimensions(600, 400);
    Graphine.setPixelsPerSecond(protocol_obj.protocol.fields.trial_duration);
    Graphine.firstRow(protocol_obj.intervals);
    Graphine.initActions(protocol_obj.actions);
    Graphine.initEvents(protocol_obj.events);
}
