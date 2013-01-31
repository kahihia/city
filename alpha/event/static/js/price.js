(function($) {
	$.widget("ui.price", {
		_create: function() {
			var that = this,
				free = $("#id_price_free");
			free.on("change", function() {
				if(this.checked) {
					$(that.element).val("Free");
					$(that.element).prop('disabled', true);
					that.addFreeTag();
				} else {
					$(that.element).prop('disabled', false);
					$(that.element).val("");
					that.removeFreeTag();
				}
			});
			free.on("changeFromTags", function(){
				if(this.checked) {
					$(that.element).val("Free");
					$(that.element).prop('disabled', true);					
				} else {
					$(that.element).prop('disabled', false);
					$(that.element).val("");
					
				}
			})
			$(this.element).on("change", function() {
				var price = $(that.element).val().trim();
				if(!(/^\d*(?:\.\d{0,2})?$/.test(price))) {
					$(that.element).val("");
					that.showError("Please enter a valid price");
				} else {
					that.hideError();
				}
			});
		},
		showError: function(message) {
			this.error = $("<div>").addClass("error").html(message);
			$(this.element).before(this.error);
		},
		hideError: function() {
			if(this.error) {
				$(this.error).remove();
			}
			this.error = null;
		},
		addFreeTag: function() {
			var e;
			$("#id_tags__tagautosuggest").val("Free")
			e = jQuery.Event("keydown");
			e.keyCode = 9;
			$("#id_tags__tagautosuggest").trigger(e);
		},
		removeFreeTag: function() {
			var button = $(".as-selections [data-value=Free] a");
			$('.tags-popup').css("opacity", 0);
			$(button).trigger("click");			
			$(".modal-bg").hide();
			setTimeout(function(){
				$("#id_tags__tagautosuggest").blur();
				$('.tags-popup').hide();
				$('.tags-popup').css("opacity", 1);
			});
            $(".as-selections").removeClass("active");
		}
	});

	$(document).ready(function() {
		setTimeout(function(){
			$("#id_price").price();
		},100);		
	});
})(jQuery);