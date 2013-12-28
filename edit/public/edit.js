/* global variables */
var sysvars = {
	default_paradigm_id:1,
	protocol_id:0
};

/* Menu functions */

function edit_trialDuration(){
	loadInDetails('#trial_duration');
}

function makeNewProtocol(paradigm_id){
	if(paradigm_id===undefined){
		paradigm_id = sysvars.default_paradigm_id;
	}
	var url = '/edit/paradigm/'+paradigm_id+'/make_experiment';
	var duration = $('input[name="duration"]').val();
	$.post(url,{'duration':duration}, function(data){
		sysvars.protocol_id = data.protocol_id;
	});
}


/*Panel functions */

function loadInDetails(selector){
	$('.details-panel').html($(selector).html());
}

function clearInDetails(){
	$('.details-panel').html('');
}

function set_trialDuration(){
	var duration = $('.details-panel input[name="duration"]').val();
	duration = parseFloat(duration);
	if(isNaN(duration)){
		alert("Entered duration is not a number");
	} else {
		//set graph
		set_PixelsPerSecond(duration);
		//end to db
		
		
		clearInDetails();
	}
}

/* Graph functions */

function set_PixelsPerSecond(duration){
	d3.select('#timeline').remove();
	var w = $('#flow').width();
	var pps = w / duration;
	var sc = d3.time.scale().domain([0,duration*1000]).range([0,w-30]);
	//var sc = d3.scale.linear().domain([0,duration]).range([0,w-30]);
	var ax = d3.svg.axis().scale(sc).orient('top');
	d3.select('#flow')
		.attr('width',w)
		.attr('height',400)
		.append('g')
			.attr('id','timeline')
			.attr("transform", "translate(5,25)")
			.attr('class','axis')
			.style({'font-size':'0.5em','stroke-width':1})
			.call(ax);
}

window.onload = function() {
	makeNewProtocol();
	
	cssExpandHeightUntilEnd('.toolbox');
	cssExpandHeightUntilEnd('.buttons-panel');
	cssExpandHeightUntilEnd('.details-panel');
	cssExpandWidthUntilEnd('.details-panel');
	$("#menu").kendoMenu();
};