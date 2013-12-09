var sysvars ={'protocol_id':1, 'paradigm_id':1}

function cssExpandHeightUntilEnd(selector){
	var element = $(selector);
	element.height($(window).height() - (element.offset().top));
}

function startExperiment(){
	if(sysvars.protocol_id==undefined){
		alert('protocol id is undefined');
	}
	else {
		var url="/perform/protocol/"+sysvars.protocol_id+"/experiment/start";
		$.get(url).done(function(data){
			sysvars['experiment_id'] = data.pk;
			var exp_name = data.fields.name;
			$('#div_experiment_name i').text(exp_name);
			sysvars['haps_check'] = setInterval(checkHappenings,1000);
		});
	}
}

function stopExperiment(){
	clearInterval(sysvars['haps_check']);
	var url = "/perform/experiment/"+sysvars.experiment_id+"/stop";
	$.get(url).done(function(data){
		logHappenings(data.happenings);
		kendoConsole.error('- Stop Experiment -');
	});	
}

function logHappenings(haps){
	var len = haps.length;
	for(var i=0; i<len; i++){
		var details = haps[i].fields;
		if(details.type==='TRL'){
			kendoConsole.attn(details.time_occurred+" : "+details.description);
		} else {
			kendoConsole.log(details.time_occurred+" : "+details.description);
		}
	}
}

function checkHappenings(){
	var url = '/perform/experiment/'+sysvars.experiment_id+"/happenings";
	$.get(url).done(function(data){
		logHappenings(data.happenings);
	});
}

function markTime(){
	var url = '/perform/experiment/'+sysvars.experiment_id+"/mark";
	$.get(url);
}

function makeActionEmu(id){
	return function(){
		if(sysvars.experiment_id!==undefined){
			$.post('/perform/experiment/'+sysvars.experiment_id+'/emulate',
				{'action_id':id});
		} else {
			alert('experiment not yet started');
		}
		return false;
	};
}

function generateActionButtons(){
	
	var url = '/edit/paradigm/'+sysvars.paradigm_id+'/actions';
	$.get(url,function(data){
		var len = data.length;
		for(var i=0; i<len; i++){
			var act = data[i];
			var act_id = act.pk;
			var act_type = act.fields.type;
			var btn = $('<button class="k-button">'+act_type+'</button>');
			$('#div_acts').append(btn);
			var onclick = makeActionEmu(act_id);
			btn.click(onclick);
			/* do something with props if it has any */
		}
	
	});
}

function makeEventSim(id){
	return function(){
		if(sysvars.experiment_id!==undefined){
			$.post('/perform/experiment/'+sysvars.experiment_id+'/simulate',
				{'event_id':id});
		} else {
			alert('experiment not yet started');
		}
		return false;
	};
}

function generateEventButtons(){
	var url = '/edit/protocol/'+sysvars.protocol_id+'/events';
	$.get(url,function(data){
		var len = data.length;
		for(var i=0; i<len; i++){
			var evt = data[i];
			var evt_id = evt.pk;
			var evt_name = evt.fields.name;
			var btn = $('<button class="k-button">'+evt_name+'</button>');
			$('#div_evts').append(btn);
			var onclick = makeEventSim(evt_id);
			btn.click(onclick);
		}
	});
	
}

window.onload = function(){
	cssExpandHeightUntilEnd('.leftside');
	cssExpandHeightUntilEnd('.console');
	cssExpandHeightUntilEnd('.rightside');
		
	$("#menu").kendoMenu();
	$('#btn_start').click(startExperiment);
	$('#btn_stop').click(stopExperiment);
	$('#btn_mark').click(markTime);
	generateActionButtons();
	generateEventButtons();
};

// add stuff to page console: kendoConsole.log(str);
// color red kendoConsole.error(str);