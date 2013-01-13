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
            $(button).trigger("click");
            $("#id_tags__tagautosuggest").blur();
            $('.tags-popup').hide();
        }
    });
    $(document).ready(function() {
        $("#id_wheelchair_0").wheelchair();
    });
})(jQuery);