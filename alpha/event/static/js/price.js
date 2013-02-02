(function($) {
	$.widget("ui.price", {
		_create: function() {
			var that = this,
				free = $("#id_price_free"),
				atFirst = true;
			free.on("change", function() {
				if(this.checked) {
					$(that.element).val("Free");
					$(that.element).prop('disabled', true);
					that.addFreeTag();
				} else {
					$(that.element).prop('disabled', false);
					$(that.element).val("$");
					that.removeFreeTag();
				}
			});
			free.on("changeFromTags", function(){
				if(atFirst){
					atFirst = true;
					return;
				}
				if(this.checked) {
					$(that.element).val("Free");
					$(that.element).prop('disabled', true);					
				} else {
					$(that.element).prop('disabled', false);
					$(that.element).val("$");					
				}
			})
			$(this.element).on("keyup", function() {
				$(".price-td .help").html(
					$(that.element).val().length + " of 50 characters left"
				);
			});
			$(".price-td .help").html(
				$(that.element).val().length + " of 50 characters left"
			);
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