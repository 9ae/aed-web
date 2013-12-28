var sysvars = {
	'protocol_id' : 1,
	'paradigm_id' : 1,
	'haps_ready' : false,
	'graph_ready' : false,
	'trials' : 0,
	'trial_start_time': 0.0
};

function startExperiment() {
	if (sysvars.protocol_id == undefined) {
		alert('protocol id is undefined');
	} else {
		var url = "/perform/protocol/" + sysvars.protocol_id + "/experiment/start";
		var postdata = {
			'change' : 0,
			'data' : null
		};
		if (sysvars.interval_adjustments != undefined) {
			postdata.data = JSON.stringify(sysvars.interval_adjustments);
			postdata.change = 1;
		}
		$.post(url, postdata).done(function(data) {
			sysvars['experiment_id'] = data.pk;
			var exp_name = data.fields.name;
			$('#div_experiment_name i').text(exp_name);
			sysvars['haps_check'] = setInterval(checkHappenings, 1000);
			sysvars.haps_ready = true;
		});
		$('#btn_start').prop('disabled',true);
		$('#btn_start').addClass('disabled');
	}
}

function stopExperiment() {
	clearInterval(sysvars['haps_check']);
	var url = "/perform/experiment/" + sysvars.experiment_id + "/stop";
	$.get(url).done(function(data) {
		logHappenings(data.happenings);
		kendoConsole.error('- Stop Experiment -');
	});
}

function extractDuration(idescript) {
	var regex = /^\[(\d+\.*\d*)\]\s.+$/g;
	var match = regex.exec(idescript);
	if (match != null && match.length === 2) {
		return match[1];
	} else {
		return 0;
	}
}

function logHappenings(haps) {
	var len = haps.length;
	for (var i = 0; i < len; i++) {
		var details = haps[i].fields;
		if (details.type === 'TRL') {
			kendoConsole.attn(details.time_occurred + " : " + details.description);
			sysvars.trial_start_time = details.time_occurred;
			if (sysvars.trials > 0) {
				Graphine.nextRow();
			}
			sysvars.trials++;
		} else {
			kendoConsole.log(details.time_occurred + " : " + details.description);
		}
		if (details.type === 'ITL') {
			var o = {
				'name' : details.keyname,
				'duration' : 0
			};
			o['duration'] = extractDuration(details.description);
			if(sysvars.trials>1){
				Graphine.addInterval(o);
			}
		} else if (details.type === 'ACT') {
			var o = {
				'name' : details.keyname,
				'time_occurred' : details.time_occurred - sysvars.trial_start_time
			};
			Graphine.addAction(o);
		} else if (details.type === 'EVT') {
			var o = {
				'name' : details.keyname,
				'time_occurred' : details.time_occurred - sysvars.trial_start_time
			};
			Graphine.addEvent(o);
		} else if (details.type === 'MRK') {
			Graphine.addMark(details.time_occurred - sysvars.trial_start_time);
		} else {
		}
	}
}

function checkHappenings() {
	if (!sysvars.haps_ready)
		return;
	sysvars.haps_ready = false;
	var url = '/perform/experiment/' + sysvars.experiment_id + "/happenings";
	$.get(url).done(function(data) {
		logHappenings(data.happenings);
		sysvars.haps_ready = true;
	});
}

function markTime() {
	var url = '/perform/experiment/' + sysvars.experiment_id + "/mark";
	$.get(url);
}

function makeActionEmu(id) {
	return function() {
		if (sysvars.experiment_id !== undefined) {
			$.post('/perform/experiment/' + sysvars.experiment_id + '/emulate', {
				'action_id' : id
			});
		} else {
			alert('experiment not yet started');
		}
		return false;
	};
}

function generateActionButtons() {

	var url = '/edit/paradigm/' + sysvars.paradigm_id + '/actions';
	$.get(url, function(data) {
		var len = data.length;
		for (var i = 0; i < len; i++) {
			var act = data[i];
			var act_id = act.pk;
			var act_type = act.fields.type;
			var btn = $('<button class="k-button">' + act_type + '</button>');
			$('#div_acts').append(btn);
			var onclick = makeActionEmu(act_id);
			btn.click(onclick);
			/* do something with props if it has any */
		}

	});
}

function makeEventSim(id) {
	return function() {
		if (sysvars.experiment_id !== undefined) {
			$.post('/perform/experiment/' + sysvars.experiment_id + '/simulate', {
				'event_id' : id
			});
		} else {
			alert('experiment not yet started');
		}
		return false;
	};
}

function generateEventButtons() {
	var url = '/edit/protocol/' + sysvars.protocol_id + '/events';
	$.get(url, function(data) {
		var len = data.length;
		for (var i = 0; i < len; i++) {
			var evt = data[i];
			var evt_id = evt.pk;
			var evt_name = evt.fields.name;
			var btn = $('<button class="k-button">' + evt_name + '</button>');
			$('#div_evts').append(btn);
			var onclick = makeEventSim(evt_id);
			btn.click(onclick);
		}
	});

}

function openIntervalsEditor() {
	var url = '/edit/protocol/' + sysvars.protocol_id + '/intervals/view';
	var win = $("#kWindow").data("kendoWindow");
	if (win != undefined) {
		win.center();
		win.open();
	} else {
		$("#kWindow").kendoWindow({
			actions : ['Close'],
			content : url,
			modal : true,
			title : 'Intervals',
			position : {
				top : 20,
				left : 100
			},
			visible : false
		});
		win = $("#kWindow").data("kendoWindow");
		win.open();
	}
}

function initGraph() {
	$('#graph').load('/perform/graph', function(response, status, xhr) {
		$.get('/edit/protocol/' + sysvars['protocol_id'] + '?context=graph', initGraph);
		if (status === "success") {
			sysvars.graph_ready = true;
		}
	});
}

window.onload = function() {
	cssExpandHeightUntilEnd('.leftside');
	cssExpandHeightUntilEnd('.console');
	cssExpandHeightUntilEnd('.rightside');

	$("#menu").kendoMenu();
	$('#btn_start').click(startExperiment);
	$('#btn_stop').click(stopExperiment);
	$('#btn_mark').click(markTime);
	generateActionButtons();
	generateEventButtons();
	initGraph();
};

// add stuff to page console: kendoConsole.log(str);
// color red kendoConsole.error(str);