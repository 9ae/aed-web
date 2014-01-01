/* global variables */
var sysvars = {
	default_paradigm_id:1,
	protocol_id:0,
	paradigm_types: {}
};

function array2map(list,fun){
	var len = list.length;
	var map = {};
	for(var i=0; i<len; i++){
		var item = fun(list[i]);
		map[item[0]] = item[1];
	}
	return map;
}

function map2array(map,keyname){
	var array = [];
	for(var k in map){
		var val = map[k];
		if(keyname!==undefined){
			val[keyname] = k;
		} else {
			val['key'] = k;
		}
		array.push(val);
	}
	return array;
}

function mapByType(item){
	var key = item['type'];
	var value = item;
	delete value['type'];
	return [key,value];
}

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
	//	delete sysvars.paradigm_types['protocol_id'];
		
		$("#select_interval_type").kendoComboBox({ dataTextField:"type", dataValueField: "type",
          dataSource: data.intervals, select: select_intervalType});
       	$('#select_event_type').kendoComboBox({ dataTextField:"type", dataValueField: "type",
          dataSource: data.events, select: select_eventType});
          
        sysvars.paradigm_types = {};
		sysvars.paradigm_types['actions'] = array2map(data.actions,mapByType);
		sysvars.paradigm_types['events'] = array2map(data.events,mapByType);
		sysvars.paradigm_types['intervals'] = array2map(data.intervals,mapByType);
	});
}

/* Button functions */

function btn_newInterval(){
	loadInDetails('#interval_details');
	$('#interval_details button[name="go"]').unbind('click')
											.text('Make')
											.click(save_newInterval);
}

function btn_newEvent(){
	loadInDetails('#event_details');
	$('#event_details button[name="go"]').unbind('click')
											.text('Make')
											.click(save_newEvent);
}

/*Panel functions */

function loadInDetails(selector){
	$('div.details-panel>div').hide();
	$(selector).show();
}

function clearInDetails(){
	$('div.details-panel>div').hide();
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

function select_intervalType(e){
	var item = e.item;
    var text = item.text();
    populate_propsPanel(sysvars.paradigm_types.intervals[text].props,'#interval_details');
}

function select_eventType(e){
	var item = e.item;
    var text = item.text();
    populate_propsPanel(sysvars.paradigm_types.events[text].props,'#event_details');
}

function populate_propsPanel(props,parentSelector){
	var panel = $(parentSelector).children('div.prop_details').first();
	panel.html('');
	var propslen = props.length;
	for(var i=0; i<propslen; i++){
		var obj = props[i];
		var label = $('<label>'+obj.name+'</label>');
		var ftype = "text";
		if(obj.type==="BOO"){
			ftype = "checkbox"
		}
		var input = $('<input />',{	'type': ftype, 
									'name': obj.name, 
									'class':'k-input', 
									'data-type':obj.type});
		if(obj['default']!==undefined){
			input.attr('value',obj['default']);
		}
		panel.append(label);
		input.insertAfter(label);
	}
}

function save_newInterval(evt){
	var type = $('#select_interval_type').data("kendoComboBox").value();
	
}

function save_newEvent(evt){
	var type = $('#select_event_type').data("kendoComboBox").value();	
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
	set_trialDuration();
};