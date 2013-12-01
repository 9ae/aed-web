var sysvars ={'protocol_id':1}

function cssExpandHeightUntilEnd(selector){
	var element = $(selector);
	element.height($(window).height() - (element.offset().top));
}

function startExperiment(){
	if(sysvars.protocol_id==undefined){
		alert('protocol id is undefined');
	}
	else {
		var url="/perform/experiment/start?protocol="+sysvars.protocol_id;
		$.get(url).done(function(data){
			sysvars['experiment_id'] = data.pk;
			var exp_name = data.fields.name;
			$('#div_experiment_name i').text(exp_name);
		});
	}
}

function stopExperiment(){
	clearInterval(sysvars['haps_check']);
	var url = "/perform/experiment/stop";
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
	var url = '/perform/happenings';
	$.get(url).done(function(data){
		logHappenings(data.happenings);
	});
}

function markTime(){
	var url = '/perform/mark';
	$.get(url);
}

window.onload = function(){
	cssExpandHeightUntilEnd('.leftside');
	cssExpandHeightUntilEnd('.console');
	cssExpandHeightUntilEnd('.rightside');
		
	$("#menu").kendoMenu();
	$('#btn_start').click(startExperiment);
	$('#btn_stop').click(stopExperiment);
	$('#btn_mark').click(markTime);
	sysvars['haps_check'] = setInterval(checkHappenings,1000);
};

// add stuff to page console: kendoConsole.log(str);
// color red kendoConsole.error(str);