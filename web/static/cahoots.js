$(document).ready(function() {
	$("#examples .example ul li a").click(function(evt) {
		$("#q").val($(this).text());
		$("#input").submit();
		
		evt.stopPropagation();
		evt.preventDefault();
		
		return false;
	});
	
	$("#q").keydown(function(evt) {
		if(evt.shiftKey || evt.ctrlKey) {
			return;
		}
		
		if(evt.which == 13) {
			$("#input").submit();
			evt.preventDefault();
			evt.stopPropagation();
			return false;
		}
	});
});