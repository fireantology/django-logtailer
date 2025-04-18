django.jQuery('#start-button').click(function() {
    LogTailer.startReading();
});

django.jQuery('#stop-button').click(function() {
    LogTailer.stopReading();
});

django.jQuery('#auto-scroll').click(function() {
    LogTailer.changeAutoScroll();
});	

django.jQuery('#filter-select').change(function() {
	LogTailer.customFilter();
});		



django.jQuery('#log-window').html("")
LogTailer.customFilter();

django.jQuery('#clipboard-form').submit(function() {
  var error = false;
  if(django.jQuery("#clipboard-name").val().length<1){
  	django.jQuery("#clipboard-error").html("Field name is mandatory");
  	error = true;
  }
  if(django.jQuery("#clipboard-logs").val().length<1){
  	django.jQuery("#clipboard-error").html("No log lines selected");
  	error = true;
  }
  
  if(!error){
  	django.jQuery.ajax({type: 'POST',
					   url: clipboard_url,
  	                   data: { 
  	                   	 name: django.jQuery("#clipboard-name").val(),
  	                     notes: django.jQuery("#clipboard-notes").val(),
  	                     logs: django.jQuery("#clipboard-logs").val(),
  	                     file: django.jQuery("#clipboard-file").val(),
                         csrfmiddlewaretoken: django.jQuery("[name=csrfmiddlewaretoken]").val()
  	                   },
  	                   success: function(result){
  	                   	   alert(result);
  	                   	   django.jQuery("#modal-overlay").hide();
  	                   }, 
  	                   dataType: "text"});
  }
  
  return false;
});

const saveRows = document.getElementById("save-rows");
const modal = document.getElementById("modal-overlay");
const closeButton = document.getElementById("close-modal-btn");

function openModal() {
	django.jQuery("#clipboard-logs").val(getSelectedText());
	django.jQuery("#clipboard-name").val("");
	django.jQuery("#clipboard-notes").val("");
	django.jQuery("#clipboard-error").html("");
    modal.classList.remove("hide");
}

function closeModal(e, clickedOutside) {
    if (clickedOutside) {
        if (e.target.classList.contains("modal-overlay"))
            modal.classList.add("hide");
    } else modal.classList.add("hide");
}

saveRows.addEventListener("click", openModal);
modal.addEventListener("click", (e) => closeModal(e, true));
closeButton.addEventListener("click", closeModal);
