;(function($, window, document, undefined) {
    'use strict';
    function PriceWidget(element){
        var that = this,
            free = $("#id_price_free"),
            atFirst = true
            this.element = element;
        
        if($(this.element).val()==='Free'){
            $(free).prop('checked', true);
        }

        free.on("change", function() {
            if(this.checked) {
                $(that.element).val("Free");
                $(that.element).prop('readonly', true);
                that.addFreeTag();
            } else {
                $(that.element).prop('readonly', false);
                $(that.element).val("$");
                that.removeFreeTag();
            }
        });

        free.on("changeFromTags", function(){
            if(this.checked) {
                $(that.element).val("Free");
                $(that.element).prop('readonly', true);
            } else {
                $(that.element).prop('readonly', false);
                if($(that.element).val()=="Free"){
                    $(that.element).val("$");    
                }
            }
        });

        if($(that.element).val()=="Free"){
            $(that.element).prop('readonly', true);
        }
    }

    PriceWidget.prototype = {
        addFreeTag: function() {
            var e;
            var tags = _.map($("#as-values-id_tags__tagautosuggest").val().split(","), function(tag){
                return tag.trim();
            });

            tags = _.filter(tags, function(tag){ return tag; });

            if(tags.indexOf("Free")===-1){
                $("#id_tags__tagautosuggest").val("Free");
                e = $.Event("keydown");
                e.keyCode = 9;
                $("#id_tags__tagautosuggest").trigger(e);
            }
        },
        removeFreeTag: function() {
            var button = $(".as-selections [data-value='Free'] a, .as-selections [data-value=' Free'] a");
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
    }

    window.PriceWidget = PriceWidget;
})(jQuery, window, document);
