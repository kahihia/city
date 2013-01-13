(function($) {
	$.widget("ui.price", {
		_create: function() {
			var that = this,
				free = $("#id_price_free");
			free.on("change", function() {
				if(this.checked) {
					$(that.element).val("");
					$(that.element).prop('disabled', true);
					that.addFreeTag();
				} else {
					$(that.element).prop('disabled', false);
					that.removeFreeTag();
				}
			});
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
			$(button).trigger("click");
			$("#id_tags__tagautosuggest").blur();
			$('.tags-popup').hide();
		}
	});

	$(document).ready(function() {
		$("#id_price").price();
	});
})(jQuery);