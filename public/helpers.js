
function cssExpandHeightUntilEnd(selector) {
	var element = $(selector);
	element.height($(window).height() - (element.offset().top));
}

function cssExpandWidthUntilEnd(selector){
	var element = $(selector);
	element.width($(window).width() - (element.offset().left) - 20);
}
