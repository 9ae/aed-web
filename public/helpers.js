
function cssExpandHeightUntilEnd(selector) {
	var element = $(selector);
	element.height($(window).height() - (element.offset().top));
}

function cssExpandWidthUntilEnd(selector){
	var element = $(selector);
	element.width($(window).width() - (element.offset().left) - 20);
}

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

function findByKey(key,value){
	var len = this.length;
	var result = null;
	for(var i=0; i<len; i++){
        if(this[i][key]===value){
            result = this[i];
            break;
        }
    }
    return result;
}

function findIndexByKey(key,value){
    var len = this.length;
    var result = -1;
    for(var i=0; i<len; i++){
        if(this[i][key]===value){
            result = i;
            break;
        }
    }
    return result;
}

function removeByKey(key,value){
    var len = this.length;
    var result = -1;
    for(var i=0; i<len; i++){
        if(this[i][key]===value){
            result = i;
            break;
        }
    }
    if(result>=0){
    	this.splice(result,1);
    }
}