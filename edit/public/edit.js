/* global variables */
var sysvars = {
	default_paradigm_id:1,
	paradigm_types: {},
	pps : 1,
	paddingTop:40,
	paddingLeft:5,
	paddingRight:30,
};

var toolbox = {
	timeOffset : 0.0,
	selected_intervalId:-1,
	selected_actionId:-1
};

var protocol = {
	id:0,
	trial_duration:0.0,
	intervals: [],
	actions: {}
};

var Protocols = {
	saveNewProtocol : function(paradigm_id){
		if(paradigm_id===undefined){
			paradigm_id = sysvars.default_paradigm_id;
		}
		var url = '/edit/paradigm/'+paradigm_id+'/make_protocol';
		var duration = $('input[name="duration"]').val();
		$.post(url,{'duration':duration}, function(data){
			protocol.id = data.protocol_id;
			
			toolbox.interval_typeselect = $("#select_interval_type").kendoComboBox({ dataTextField:"type", dataValueField: "type",
	          dataSource: data.intervals, select: Intervals.selectType}).data("kendoComboBox");
	       	toolbox.event_typeselect = $('#select_event_type').kendoComboBox({ dataTextField:"type", dataValueField: "type",
	          dataSource: data.events, select: Events.selectType}).data("kendoComboBox");
	          
	        sysvars.paradigm_types = {};
			sysvars.paradigm_types['actions'] = array2map(data.actions,mapByType);
			sysvars.paradigm_types['events'] = array2map(data.events,mapByType);
			sysvars.paradigm_types['intervals'] = array2map(data.intervals,mapByType);
			Durations.saveTrialDuration();
		});
		protocol.trial_duration = parseFloat(duration);
	},
	delSelectedObject : function(){
		if(toolbox.selected_intervalId!==-1){
			Intervals.delSelected();
		}
		if(toolbox.selected_actiond!==-1){
			
		}
	},
	redrawAll : function(){
		var offset = sysvars.paddingLeft;
		var len = protocol.intervals.length;
		for(var i=0; i<len; i++){
			var ival = protocol.intervals[i];
			var w = sysvars.pps*ival.duration;
			d3.select('#rect'+ival.id)
				.attr('width',w)
				.attr('transform', 'translate('+offset+','+sysvars.paddingTop+')');
			offset += w;
		}
	},
};

var Durations = {
	checkAgainstTrialDuration : function(intervals, trial_duration){
	    var total_time = 0.0;
	    for(var i in intervals){
	        var ival = intervals[i];
	        var varyby = findByKey.call(ival.props, 'name', 'varyby');
	        varyby = varyby['value'];
	        if(varyby===null){
	            varyby = 0.0;
	        } else {
	        	varyby = parseFloat(varyby);
	        }
	        total_time += (parseFloat(ival.duration)+varyby);        
	    }
	    return (total_time<=trial_duration);
	},
	menuEditTrialDuration : function(){
		Properties.loadInDetails('#trial_duration');
	},
	saveTrialDuration: function(){
		var duration = $('.details-panel input[name="duration"]').val();
		duration = parseFloat(duration);
		if(isNaN(duration)){
			alert("Entered duration is not a number");
		} else if(!Durations.checkAgainstTrialDuration(protocol.intervals,duration)) {
			alert('The sum of all interval durations cannot exceed trial duration');
		}
		 else {
			// end to db
			$.post('/edit/protocol/'+protocol.id+'/set_trial_duration',{'duration':duration},
			function(data){
				if(!data.success){
					alert(data.errors[0]);
				}
			});
			protocol.trial_duration = duration;
			// set graph
			Durations.setPixelsPerSecond(duration);
			Protocols.redrawAll();	
			Properties.clearInDetails();
		}
	},
	setPixelsPerSecond : function(duration){
		d3.select('#timeline').remove();
		var w = $('#flow').width();
		sysvars.pps = w / duration;
		var sc = d3.time.scale().domain([0,duration*1000]).range([0,w-sysvars.paddingRight]);
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
};

var Properties = {
	matchIdsWithNames: function(props,map){
		var len = props.length
		for(var i=0; i<len; i++){
			var name = props[i]['name'];
			props[i]['id'] = map[name];
		}
		return props;
	},
	loadInDetails : function(selector){
	$('div.details-panel>div').hide();
	$(selector).show();
	},
	clearInDetails : function(){
	$('div.details-panel>div').hide();
	},
	populatePanel : function(props,parentSelector){
		var panel = $(parentSelector).children('div.prop_details').first();
		panel.html('');
		var propslen = props.length;
		for(var i=0; i<propslen; i++){
			var div = $('<div class="prop-row"></div>')
			var obj = props[i];
			var label = $('<label>'+obj.name+'</label>');
			var ftype = "text";
			if(obj.type==="BOO"){
				ftype = "checkbox";
			}
			var useSpinner = false;
			if(obj.type==="INT"){
				useSpinner = obj.step!==undefined;
				if(useSpinner){
					ftype="number";
				}
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
			if(useSpinner){
				input.attr('step', obj['step']);
				var min = obj.min;
				var max = obj.max;
				if(min!==undefined){
					input.attr('min',min);
				}
				if(max!==undefined){
					input.attr('max',max);
				}
			}
			div.append(label);
			input.insertAfter(label);
			panel.append(div);
		}
	},
	applyChanges : function(delta){
		for(var key in delta){
			if(key==='id'){continue; }
			else if (key==='props'){
				var props = $.parseJSON(delta['props']);
				var len = props.length;
				for(var i=0; i<len; i++){
					var p = findByKey.call(this.props, 'name', props[i].name);
					p.value = props[i].value;
				}
			} else {
				this[key] = delta[key];
			}
		}
	},
};

var Intervals = {
	btnNew : function(){
	Properties.loadInDetails('#interval_details');
	$('#interval_details button[name="go"]').unbind('click')
											.text('Make')
											.click(Intervals.saveNew);
	},
	delSelected : function(){
		$.get('/edit/interval/'+toolbox.selected_intervalId+'/delete?pps='+sysvars.pps, function(data){
			Intervals.erase(toolbox.selected_intervalId);
			Intervals.redrawIntervalsAfter(data.content.graphOffsets);
			removeByKey.call(protocol.intervals,'id',toolbox.selected_intervalId);
			toolbox.selected_intervalId = -1;
			Intervals.clearPanel();
		});
	},
	selectType : function(e){
		var item = e.item;
	    var text = item.text();
	    Properties.populatePanel(sysvars.paradigm_types.intervals[text].props,'#interval_details');
	    $('#interval_details div.color-field').show();
	    var c = kendo.parseColor('#'+sysvars.paradigm_types.intervals[text].color);
	    toolbox.interval_colorpicker.value(c); 
	},
	make_ClickListener : function(id){
		return function(data){
			toolbox.selected_intervalId = id;
			var stuff = findByKey.call(protocol.intervals,'id',id);
			toolbox.interval_typeselect.value(stuff.type);
			toolbox.interval_typeselect.enable(false);
			$('#interval_name').val(stuff.name);
			$('#interval_duration').val(stuff.duration);
			toolbox.interval_colorpicker.value(stuff.color);
			Properties.populatePanel(stuff.props,'#interval_details');
			$('#interval_details button[name="go"]').unbind('click')
												.text('Save')
												.click(Intervals.save);
			$('#interval_details').show();
		}
	},
	save: function(evt){
		var stuff = clone(findByKey.call(protocol.intervals,'id',toolbox.selected_intervalId));
		
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
			var varybyObj = findByKey.call(stuff.props,'name',name);
			if ($(this).val() !== varybyObj.value) {
				varybyObj.value = $(this).val();
				if (name === 'varyby') {
					timesChanged = true;
				}
			} else {
				if (name === 'varyby') {
					varyByKeep = true;
				 } else{
					var ind = findIndexByKey.call(stuff.props, 'name' ,name);
					stuff.props.splice(ind, 1);
				}
			}
		});
		
		var timesOkay = true;
		if (timesChanged){
			var intervals = clone(protocol.intervals);
			intervals[stuff.id] = stuff;
			timesOkay = Durations.checkAgainstTrialDuration(intervals, protocol.trial_duration);
			if(varyByKeep){
				var ind = findIndexByKey.call(stuff.props, 'name', 'varyby');
				stuff.props.splice(ind, 1);
			}
			if(durationKeep){
				delete stuff.duration;
			}
		}

		if (timesOkay) {
			delete stuff.type;
			// do post
			stuff.props = JSON.stringify(stuff.props);
			stuff.pps = sysvars.pps;
			$.post('/edit/interval/'+stuff.id+'/edit',stuff,function(data){
				if(data.success){
					var ival = findByKey.call(protocol.intervals,'id',toolbox.selected_intervalId);
					Properties.applyChanges.call(ival,stuff);
					Intervals.clearPanel();
					Intervals.redraw(stuff,data.content.graphOffsets);
					toolbox.selected_intervalId = -1;
				} else {
					alert(data.errors[0]);		
				}
			});
		} else {
			alert('The sum of all interval durations cannot exceed trial duration');
		}		
	},
	saveNew : function(evt){
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
		if(Durations.checkAgainstTrialDuration(intervals, protocol.trial_duration)){
			postbody.props = JSON.stringify(postbody.props);
			$.post('/edit/protocol/'+protocol.id+'/new_interval',postbody, function(data){
					if(data.success){
						var stuff = postbody;
						stuff.id = data.content.interval_id
						var ival = Intervals.draw(stuff);
						stuff.props = Properties.matchIdsWithNames(props,data.content.prop_ids);
						protocol.intervals.push(stuff);
						var ilisten = Intervals.make_ClickListener(stuff.id);
						ival.on('click',ilisten);
						ival.attr('id','rect'+stuff.id);
						Intervals.clearPanel();
					} else {
						alert(data.errors[0]);
					}
				});
		} else {
			alert('The sum of all interval durations cannot exceed trial duration');
		}
	},
	clearPanel : function(){
		toolbox.interval_typeselect.text('');
		toolbox.interval_typeselect.enable(true);
		$('#interval_name').val('');
		$('#interval_duration').val('');
		toolbox.interval_colorpicker.value('#FFFFFF');
		$('#interval_details div.prop_details').html('');
		$('#interval_details').hide();
	},
	draw : function(properties){
		var duration = parseFloat(properties.duration);
		var offset = sysvars.paddingLeft+sysvars.pps*toolbox.timeOffset;
		var result = d3.select('#flow').append('rect')
			.attr('width',sysvars.pps*duration)
			.attr('height',100)
			.attr('transform','translate('+offset+','+sysvars.paddingTop+')' )
			.attr('fill',properties.color);
		toolbox.timeOffset += duration;
		return result;
	},
	redraw : function(properties,moveMap){
		var rect = d3.select('#rect'+properties.id);
		if(properties.color!==undefined){
			rect.attr('fill',properties.color);
		}
		if(properties.duration!==undefined){
			var duration = parseFloat(properties.duration);
			rect.attr('width',sysvars.pps*duration);
			Intervals.redrawIntervalsAfter(moveMap);
		}
	}, 
	redrawIntervalsAfter : function(moveMap){
		for(var keyid in moveMap){
			var sibling = $('#'+keyid);
			var offset = sysvars.paddingLeft+parseFloat(moveMap[keyid]);
			sibling.attr('transform', 'translate('+offset+','+sysvars.paddingTop+')')
		}
	},
	erase : function(id){
		var intervalDetails = findByKey.call(protocol.intervals,'id',id);
		toolbox.timeOffset -= intervalDetails.duration;
		d3.select('#rect'+id).remove();
	}
};

var Events = {
	btnNew : function(){
		Properties.loadInDetails('#event_details');
		$('#event_details button[name="go"]').unbind('click')
											.text('Make')
											.click(Events.saveNew);
	},
	selectType : function(e){
		var item = e.item;
	    var text = item.text();
	    Properties.populatePanel(sysvars.paradigm_types.events[text].props,'#event_details');
	    $('#event_details div.color-field').show();
	    var c = kendo.parseColor('#'+sysvars.paradigm_types.events[text].color);
	    toolbox.event_colorpicker.value(c); 
	},
	saveNew : function(evt){
		var type = toolbox.event_typeselect.value();	
	},
};

window.onload = function() {
	Protocols.saveNewProtocol();
	
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