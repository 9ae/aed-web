/* global variables */
var sysvars = {
	default_paradigm_id:1,
	protocol_id:0,
	paradigm_types: {},
	pps : 1,
	paddingTop:40,
	paddingLeft:5,
	paddingRight:30,
	intervals : [],
};

var toolbox = {
	timeOffset : 0.0
	
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
	var url = '/edit/paradigm/'+paradigm_id+'/make_protocol';
	var duration = $('input[name="duration"]').val();
	$.post(url,{'duration':duration}, function(data){
		sysvars.protocol_id = data.protocol_id;
	//	delete sysvars.paradigm_types['protocol_id'];
		
		toolbox.interval_typeselect = $("#select_interval_type").kendoComboBox({ dataTextField:"type", dataValueField: "type",
          dataSource: data.intervals, select: select_intervalType}).data("kendoComboBox");
       	toolbox.event_typeselect = $('#select_event_type').kendoComboBox({ dataTextField:"type", dataValueField: "type",
          dataSource: data.events, select: select_eventType}).data("kendoComboBox");
          
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
		//end to db
		$.post('/edit/protocol/'+sysvars.protocol_id+'/set_trial_duration',{'duration':duration},
		function(data){
			if(!data.success){
				alert(data.errors[0]);
			}
		});
		//set graph
		set_PixelsPerSecond(duration);
		//TODO: update existing intervals		
		clearInDetails();
	}
}

function select_intervalType(e){
	var item = e.item;
    var text = item.text();
    populate_propsPanel(sysvars.paradigm_types.intervals[text].props,'#interval_details');
    $('#interval_details div.color-field').show();
    var c = kendo.parseColor('#'+sysvars.paradigm_types.intervals[text].color);
    toolbox.interval_colorpicker.value(c); 
}

function select_eventType(e){
	var item = e.item;
    var text = item.text();
    populate_propsPanel(sysvars.paradigm_types.events[text].props,'#event_details');
    $('#event_details div.color-field').show();
    var c = kendo.parseColor('#'+sysvars.paradigm_types.events[text].color);
    toolbox.event_colorpicker.value(c); 
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
	var postbody = {};
	postbody.type = toolbox.interval_typeselect.value();
	postbody.color = toolbox.interval_colorpicker.value();
	postbody.color = postbody.color.replace('#','');
	postbody.name = $('#interval_name').val();
	postbody.duration = $('#interval_duration').val();
	var props = [];
	$('#interval_details div.prop_details input').each(function(){
		var obj = {};
		obj.name = $(this).attr('name');
		obj.type = $(this).attr('data-type');
		obj.value = $(this).val();
		props.push(obj);
	});
	postbody.props = JSON.stringify(props);
	//var listener = makeListener_new_interval(postbody);
	$.post('/edit/protocol/'+sysvars.protocol_id+'/new_interval',postbody, function(data){
			if(!data.success){
				alert(data.errors[0]);
			} else {
				var stuff = postbody;
				stuff.id = data.content.interval_id
				sysvars.intervals.push(stuff);
				draw_interval(stuff);
			}
		});
}

function save_newEvent(evt){
	var type = toolbox.event_typeselect.value();	
}

/* Graph functions */

function set_PixelsPerSecond(duration){
	d3.select('#timeline').remove();
	var w = $('#flow').width();
	sysvars.pps = w / duration;
	var sc = d3.time.scale().domain([0,duration*1000]).range([0,w-sysvars.paddingRight]);
	//var sc = d3.scale.linear().domain([0,duration]).range([0,w-30]);
	var ax = d3.svg.axis().scale(sc).orient('top');
	d3.select('#flow')
		.attr('width',w)
		.attr('height',400)
		.append('g')
			.attr('id','timeline')
			.attr("transform", "translate("+sysvars.paddingLeft+","+sysvars.paddingTop+")")
			.attr('class','axis')
			.style({'font-size':'0.5em','stroke-width':1})
			.call(ax);
}

function draw_interval(properties){
	var duration = parseFloat(properties.duration);
	var offset = sysvars.paddingLeft+sysvars.pps*toolbox.timeOffset;
	d3.select('#flow').append('rect')
		.attr('width',sysvars.pps*duration)
		.attr('height',100)
		.attr('transform','translate('+offset+','+sysvars.paddingTop+')' )
		.attr('fill','#'+properties.color);
		console.log(properties.color);
	toolbox.timeOffset += duration;
}

window.onload = function() {
	makeNewProtocol();
	
	cssExpandHeightUntilEnd('.toolbox');
	cssExpandHeightUntilEnd('.buttons-panel');
	cssExpandHeightUntilEnd('.details-panel');
	cssExpandWidthUntilEnd('.details-panel');
	$("#menu").kendoMenu();
	set_trialDuration();
	
	toolbox.interval_colorpicker = $("#interval_color").kendoColorPicker({
            value: "#ffffff"
        }).data("kendoColorPicker");
    toolbox.event_colorpicker = $("#event_color").kendoColorPicker({
            value: "#ffffff"
        }).data("kendoColorPicker");
};