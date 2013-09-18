;(function($, window, document, undefined) {
    'use strict';

    var _ = window._;

    function BooleanTag(radioGroupName, tagName){
        var that = this;
        
        this.yes = $("#id_"+radioGroupName+"_0"),
        this.no = $("#id_"+radioGroupName+"_1");

        this.tagName = tagName;

        this.yes.on("change", function() {
            that.removeTag();
            if(that.yes[0].checked) {
                that.addTag();
            }
        });
        this.no.on("change", function() {
            that.removeTag();
            if(that.yes[0].checked) {
                that.addTag();
            }
        });

        window.setInterval(this.updateTag.bind(this), 50);
        this.updateTag();
    }

    BooleanTag.prototype = {
        addTag: function() {
            var e;
            var tags = _.map($("#as-values-id_tags__tagautosuggest").val().split(","), function(tag){
                return tag.trim();
            });

            tags = _.filter(tags, function(tag){ return tag; });

            if(tags.indexOf(this.tagName)===-1){
                $("#id_tags__tagautosuggest").val(this.tagName);
                e = $.Event("keydown");
                e.keyCode = 9;
                $("#id_tags__tagautosuggest").trigger(e);
            }            
        },
        removeTag: function() {
            var button = $(".as-selections [data-value='"+this.tagName+"'] a, .as-selections [data-value=' "+this.tagName+"'] a");
            $('.tags-popup').css("opacity", 0);
            $(button).trigger("click");
            $(".modal-bg").hide();
            window.setTimeout(function(){
                $("#id_tags__tagautosuggest").blur();
                $('.tags-popup').hide();
                $('.tags-popup').css("opacity", 1);
            });
            $(".as-selections").removeClass("active");
        },
        updateTag: function(){
            var tags = _.map($("#as-values-id_tags__tagautosuggest").val().split(","), function(tag){
                return tag.trim();
            });

            tags = _.filter(tags, function(tag){ return tag; });
            if(tags.indexOf(this.tagName)===-1) {
                if(!this.no.prop("checked")) this.no.click();
            } else {
                if(!this.yes.prop("checked")) this.yes.click();
            }
        }
    };
    
    $(document).on("ready page:load", function(){
        new BooleanTag("date_night", "Date Night");
        new BooleanTag("family", "Family");
        new BooleanTag("wheelchair", "Wheelchair");
    });

})(jQuery, window, document);