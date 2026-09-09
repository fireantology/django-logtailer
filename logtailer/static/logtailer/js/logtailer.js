/*
 * Logtailer object
 */

var LogTailer = {
	timeout_id: null,
	timeout: 2000,
	scroll: true,
	file_id: 0,
	first_read: true,
}

LogTailer.getFilterParams = function (){
	// Filtering is done server-side (Python re.search on the raw line).
	var params = {};
	if(django.jQuery("#apply-filter").is(':checked')){
		var pattern = django.jQuery("#filter").val();
		if(django.jQuery('#filter-select').val()!="custom"){
			pattern = django.jQuery('#filter-select').val();
		}
		if(pattern){
			params.filter = pattern;
		}
	}
	return params;
}

LogTailer.getLines = function (){
	LogTailer.currentScrollPosition = django.jQuery("#log-window").scrollTop();
	django.jQuery.ajax({
	  url: LOGTAILER_URL_GETLOGLINE,
	  data: LogTailer.getFilterParams(),
	  success: function(result){
	  				LogTailer.printLines(result);
	  		   },
	  dataType: "json"
	});

}

LogTailer.getHistory = function (callback, lines){
	LogTailer.currentScrollPosition = django.jQuery("#log-window").scrollTop();
	var data = LogTailer.getFilterParams();
	data.history = lines;
	django.jQuery.ajax({
	  url: LOGTAILER_URL_GETLOGLINE,
	  type: "get",
	  data: data,
	  success: function(result){
	  				LogTailer.printLines(result);
                    callback && callback();
	  		   },
	  dataType: "json"
	});

}

LogTailer.printLines = function(result){
	for(var i=0;i<result.length;i++){
		if(result[i].length>0){
			django.jQuery("#log-window").append(result[i]);
		}
	}
	if(LogTailer.scroll && result.length){
		django.jQuery("#log-window").scrollTop(django.jQuery("#log-window")[0].scrollHeight - django.jQuery("#log-window").height());
	}
	else{
		django.jQuery("#log-window").scrollTop(LogTailer.currentScrollPosition);
	}
	window.clearTimeout(LogTailer.timeout_id);
	LogTailer.timeout_id = window.setTimeout("LogTailer.getLines("+LogTailer.file_id+")", LogTailer.timeout);
}

LogTailer.setFilterControlsDisabled = function (disabled){
	// The filter is applied server-side on each poll, so it is locked
	// while reading; a visible hint explains why.
	django.jQuery('#filter-select, #filter, #apply-filter').prop('disabled', disabled);
	django.jQuery('#filter-locked-hint').toggleClass('hide', !disabled);
}

LogTailer.startReading = function (){
    if (LogTailer.first_read) {
        var lines = django.jQuery('#history_lines').val();
        if(!isInt(lines)){
        	alert("Last lines parameter is not an integer");
        	return;
		}
        LogTailer.first_read = false;
        django.jQuery('#history_lines').prop("disabled", true);
        LogTailer.getHistory( function(){
            LogTailer.timeout_id = window.setTimeout("LogTailer.getLines("+LogTailer.file_id+")", LogTailer.timeout);
        }, lines);
    } else {
        LogTailer.timeout_id = window.setTimeout("LogTailer.getLines("+LogTailer.file_id+")", LogTailer.timeout);
    }
	LogTailer.setFilterControlsDisabled(true);
	django.jQuery("#start-button").hide();
	django.jQuery("#stop-button").show();
}

LogTailer.stopReading = function (){
	window.clearTimeout(LogTailer.timeout_id);
	LogTailer.setFilterControlsDisabled(false);
	django.jQuery("#stop-button").hide();
	django.jQuery("#start-button").show();
}


LogTailer.changeAutoScroll = function(){
	if(LogTailer.scroll){
      	LogTailer.scroll = false;
      	django.jQuery('#auto-scroll').val("OFF");
    }
    else{
      	LogTailer.scroll = true;
      	django.jQuery('#auto-scroll').val("ON");
    }
}

LogTailer.customFilter = function(){
	if(django.jQuery('#filter-select').val()=="custom"){
	    django.jQuery('#filter').show();
	}
	else{
		django.jQuery('#filter').hide();
	}
}