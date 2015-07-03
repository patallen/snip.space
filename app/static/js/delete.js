$(document).ready(function(){
	$('a#delete-snip-btn').click(function(event){
		var $this = $(this)
		var $id = $this.data('id')
		var conf = confirm('Are you sure you want to delete this?');
		if(conf){
			$.ajax({
				url: '/ajaxdelete',
				type: 'POST',
				data: {'snip_uuid': $id }
			}).done(function() {
				$this.closest('tr').remove();
			}).fail(function() {
				alert('Failed to delete snippet.');	
			});
		}
		event.preventDefault();
		event.stopPropagation();
	});
});
