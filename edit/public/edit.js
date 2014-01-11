/* global variables */
var sysvars = {
	default_paradigm_id:1,
	protocol_id:0,
	paradigm_types: {},
	pps : 1,
	paddingTop:40,
	paddingLeft:5,
	paddingRight:30,
};

var toolbox = {
	timeOffset : 0.0,
	seleted_intervalId:0,
};

// protocol data. stored in json
var protocol = {
	trial_duration:0.0,
	intervals: {},
	actions: {}
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

function clone(obj) {
    if (null == obj || "object" != typeof obj) return obj;
    var copy = obj.constructor();
    for (var attr in obj) {
        if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
    }
    return copy;
}

function findProp(props, name){
    var len = props.length;
    var result = null;
    for(var i=0; i<len; i++){
        if(props[i]['name']===name){
            result = props[i];
            break;
        }
    }
    return result;
}

function findPropIndex(props, name){
    var len = props.length;
    var result = -1;
    for(var i=0; i<len; i++){
        if(props[i]['name']===name){
            result = i;
            break;
        }
    }
    return result;
}

function findPropValue(props, name){
    var len = props.length;
    var result = null;
    for(var i=0; i<len; i++){
        if(props[i]['name']===name){
            result = props[i]['value'];
            break;
        }
    }
    return result;
}

function checkAgainstTrialDuration(intervals, trial_duration){
    var total_time = 0.0;
    for(var i in intervals){
        var ival = intervals[i];
        var varyby = findPropValue(ival.props,'varyby');
        if(varyby===null){
            varyby = 0.0;
        } else {
        	varyby = parseFloat(varyby);
        }
        total_time += (parseFloat(ival.duration)+varyby);        
    }
    return (total_time<=trial_duration);
}

function matchIdsWithNames(props,map){
	var len = props.length;
	for(var i=0; i<len; i++){
		var name = props[i]['name'];
		props[i]['id'] = map[name];
	}
	return props;
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
		set_trialDuration();
	});
	protocol.trial_duration = parseFloat(duration);
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
	} else if(!checkAgainstTrialDuration(protocol.intervals,duration)) {
		alert('The sum of all interval durations cannot exceed trial duration');
	}
	 else {
		//end to db
		$.post('/edit/protocol/'+sysvars.protocol_id+'/set_trial_duration',{'duration':duration},
		function(data){
			if(!data.success){
				alert(data.errors[0]);
			}
		});
		protocol.trial_duration = duration;
		//set graph
		set_PixelsPerSecond(duration);
		redraw_all();	
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
		if(obj['value']!==undefined){
			input.attr('value',obj['value']);
		}
		panel.append(label);
		input.insertAfter(label);
	}
}

function make_IntervalListener(id){
	return function(data){
		toolbox.seleted_intervalId = id;
		var stuff = protocol.intervals[id];
		toolbox.interval_typeselect.value(stuff.type);
		toolbox.interval_typeselect.enable(false);
		$('#interval_name').val(stuff.name);
		$('#interval_duration').val(stuff.duration);
		toolbox.interval_colorpicker.value(stuff.color);
		populate_propsPanel(stuff.props,'#interval_details');
		$('#interval_details button[name="go"]').unbind('click')
											.text('Save')
											.click(save_Interval);
		$('#interval_details').show();
	}
}

function applyChanges(delta){
	for(var key in delta){
		if(key==='id'){continue; }
		else if (key==='props'){
			var props = $.parseJSON(delta['props']);
			var len = props.length;
			for(var i=0; i<len; i++){
				var p = findProp(this.props,props[i].name);
				p.value = props[i].value;
			}
		} else {
			this[key] = delta[key];
		}
	}
}

function save_Interval(evt){
	var stuff = clone(protocol.intervals[toolbox.seleted_intervalId]);
	
	var timesChanged = false;
	var durationKeep = false;
	if ($('#interval_name').val() !== stuff.name) {
		stuff.name = $('#interval_name').val();
	} else {
		delete stuff.name;
	}
	if (toolbox.interval_colorpicker.value() !== stuff.color) {
		stuff.color = toolbox.interval_colorpicker.value();
	} else {
		delete stuff.color;
	}

	if ($('#interval_duration').val() !== stuff.duration) {
		timesChanged = true;
		stuff.duration = $('#interval_duration').val();
	} else {
		durationKeep = true;
	}

	var varyByKeep = false;
	$('#interval_details div.prop_details input').each(function() {
		var name = $(this).attr('name');
		var varybyObj = findProp(stuff.props, name);
		if ($(this).val() !== varybyObj.value) {
			varybyObj.value = $(this).val();
			if (name === 'varyby') {
				timesChanged = true;
			}
		} else {
			if (name === 'varyby') {
				varyByKeep = true;
			 } else{
				var ind = findPropIndex(stuff.props, name);
				stuff.props.splice(ind, 1);
			}
		}
	});
	
	var timesOkay = true;
	if (timesChanged){
		var intervals = clone(protocol.intervals);
		intervals[stuff.id] = stuff;
		timesOkay = checkAgainstTrialDuration(intervals, protocol.trial_duration);
		if(varyByKeep){
			var ind = findPropIndex(stuff.props, 'varyby');
			stuff.props.splice(ind, 1);
		}
		if(durationKeep){
			delete stuff.duration;
		}
	}

	if (timesOkay) {
		delete stuff.type;
		//do post
		stuff.props = JSON.stringify(stuff.props);
		stuff.pps = sysvars.pps;
		$.post('/edit/interval/'+stuff.id+'/edit',stuff,function(data){
			if(data.success){
				applyChanges.call(protocol.intervals[toolbox.seleted_intervalId],stuff);
				clearIntervalFields();
				redraw_interval(stuff,data.content.graphOffsets);
			} else {
				alert(data.errors[0]);		
			}
		});
	} else {
		alert('The sum of all interval durations cannot exceed trial duration');
	}		
}


function save_newInterval(evt){
	var postbody = {};
	postbody.type = toolbox.interval_typeselect.value();
	postbody.color = toolbox.interval_colorpicker.value();
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
	var intervals = clone(protocol.intervals);
	postbody.props = props;
	intervals['new'] = postbody;
	if(checkAgainstTrialDuration(intervals, protocol.trial_duration)){
		postbody.props = JSON.stringify(postbody.props);
		$.post('/edit/protocol/'+sysvars.protocol_id+'/new_interval',postbody, function(data){
				if(data.success){
					var stuff = postbody;
					stuff.id = data.content.interval_id
					var ival = draw_interval(stuff);
					stuff.props = matchIdsWithNames(props,data.content.prop_ids);
					protocol.intervals[stuff.id] = stuff;
					var ilisten = make_IntervalListener(stuff.id);
					ival.on('click',ilisten);
					ival.attr('id','rect'+stuff.id);
					clearIntervalFields();
				} else {
					alert(data.errors[0]);
				}
			});
	} else {
		alert('The sum of all interval durations cannot exceed trial duration');
	}
}

function save_newEvent(evt){
	var type = toolbox.event_typeselect.value();	
}

function clearIntervalFields(){
	toolbox.interval_typeselect.text('');
	toolbox.interval_typeselect.enable(true);
	$('#interval_name').val('');
	$('#interval_duration').val('');
	toolbox.interval_colorpicker.value('#FFFFFF');
	$('#interval_details div.prop_details').html('');
	$('#interval_details').hide();
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
	var result = d3.select('#flow').append('rect')
		.attr('width',sysvars.pps*duration)
		.attr('height',100)
		.attr('transform','translate('+offset+','+sysvars.paddingTop+')' )
		.attr('fill',properties.color);
	toolbox.timeOffset += duration;
	return result;
}

function redraw_interval(properties,moveMap){
	var rect = d3.select('#rect'+properties.id);
	if(properties.color!==undefined){
		rect.attr('fill',properties.color);
	}
	if(properties.duration!==undefined){
		var duration = parseFloat(properties.duration);
		rect.attr('width',sysvars.pps*duration);
		
		for(var keyid in moveMap){
			var sibling = $('#'+keyid);
			var offset = sysvars.paddingLeft+parseFloat(moveMap[keyid]);
			sibling.attr('transform', 'translate('+offset+','+sysvars.paddingTop+')')
		}
	}
}

function redraw_all(){
$('#flow rect').remove();	
}

window.onload = function() {
	makeNewProtocol();
	
	cssExpandHeightUntilEnd('.toolbox');
	cssExpandHeightUntilEnd('.buttons-panel');
	cssExpandHeightUntilEnd('.details-panel');
	cssExpandWidthUntilEnd('.details-panel');
	$("#menu").kendoMenu();

	toolbox.interval_colorpicker = $("#interval_color").kendoColorPicker({
            value: "#ffffff"
        }).data("kendoColorPicker");
    toolbox.event_colorpicker = $("#event_color").kendoColorPicker({
            value: "#ffffff"
        }).data("kendoColorPicker");
};