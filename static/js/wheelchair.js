(function($) {
    $.widget("ui.wheelchair", {
        _create: function() {
            var that = this,
                no = $("#id_wheelchair_1");
            $(this.element).on("change", function(event) {
                that.removeWheelchairTag();
                if($(that.element)[0].checked) {
                    that.addWheelchairTag();
                }
            });
            no.on("change", function() {
                that.removeWheelchairTag();
                if($(that.element)[0].checked) {
                    that.addWheelchairTag();
                }
            })
        },
        addWheelchairTag: function() {
            var e;
            $("#id_tags__tagautosuggest").val("Wheelchair")
            e = jQuery.Event("keydown");
            e.keyCode = 9;
            $("#id_tags__tagautosuggest").trigger(e);
        },
        removeWheelchairTag: function() {
            var button = $(".as-selections [data-value=Wheelchair] a");
            $('.tags-popup').css("opacity", 0);
            $(button).trigger("click");
            $("#id_tags__tagautosuggest").blur();
            $('.tags-popup').hide();
            $(".modal-bg").hide();
            $(".as-selections").removeClass("active");
            
	    setTimeout(function(){
		$("#id_tags__tagautosuggest").blur();
                $('.tags-popup').hide();
		$('.tags-popup').css("opacity", 1);
            });
        }
    });
    $(document).ready(function() {
        setTimeout(function(){
            $("#id_wheelchair_0").wheelchair();    
        },100);        
    });
})(jQuery);