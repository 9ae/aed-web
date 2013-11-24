
function cssExpandHeightUntilEnd(selector){
	var element = $(selector);
	element.height($(window).height() - (element.offset().top));
}

function loadExperiment(){
	
	var exp_name = '';
	$('#div_experiment_name i').text(exp_name);
}

	window.onload = function(){
		cssExpandHeightUntilEnd('.leftside');
		cssExpandHeightUntilEnd('.console');
		cssExpandHeightUntilEnd('.rightside');
		
		$("#menu").kendoMenu();
	};

// add stuff to page console: kendoConsole.log(str);
// color red kendoConsole.error(str);