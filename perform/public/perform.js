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

function makeActionEmu(id,type){
	return function(){
		console.log(type+" emulated");
		return false;
	};
}

function generateActionButtons(){
	
	var url = '/edit/paradigm/'+sysvars.paradigm_id+'/actions';
	$.get(url,function(data){
		var len = data.length;
		for(var i=0; i<len; i++){
			var act = data[0];
			var act_id = act.pk;
			var act_type = act.fields.type;
			var btn = $('<button class="k-button">'+act_type+'</button>');
			$('#div_acts').append(btn);
			var onclick = makeActionEmu(act_id,act_type);
			btn.click(onclick);
			/* do something with props if it has any */
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
};

// add stuff to page console: kendoConsole.log(str);
// color red kendoConsole.error(str);