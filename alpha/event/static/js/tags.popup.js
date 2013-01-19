(function($) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", crsf_token);            
        }
    });
    $.widget("ui.tagspopup", {
        _create: function() {
            var that = this;
            this.element[0].tagspopup = this;
            this.tags = [];
            this.popup = $('.tags-popup');
            this.tagsContainer = $('.tags-container', this.popup);
            this.closeButton = $('.close-button', this.popup);
            $(this.element).on("focus", function() {
                if(that.tags.length>0){
                    $(that.popup).show();
                    $(".modal-bg").show();
                    $(".as-selections").addClass("active");
                }                
            });
            $(this.closeButton).on("click", function() {
                $(that.popup).hide();
                $(".modal-bg").hide();
                $(".as-selections").removeClass("active");
            });            
        },
        forCity: function(city){
            var data = {},that=this;
            if(typeof city==="string"){
                data.geo_city = city;
            } else if(typeof city === "number"){
                data.city_identifier = city;
            }
            $.post("/events/ctags", data, function(data){
                tags = data.tags.map(function(tag){ return tag.name });
                that.loadTags(tags);
            });

        },
        loadTags: function(tags) {
            var that = this;
            this.tags = tags;
            $(this.popup).hide();
            $(".modal-bg").hide();
            $(".as-selections").removeClass("active");
            
            this.tagsContainer.html("");
            for(var i in tags) if(tags.hasOwnProperty(i)) {
                var tag = tags[i],
                    tagWidget;
                tagWidget = $("<div>").addClass("tag").html(tag);
                tagWidget.tag = tag;
                $(this.tagsContainer).append(tagWidget);
                $(tagWidget).on("click", function() {
                    that.addTag($(this).text());
                });
            }
        },
        addTag: function(tag) {
            if($(".as-selection-item[data-value='"+tag+"']").length>0) return
            var e;
            $("#id_tags__tagautosuggest").val(tag);
            e = jQuery.Event("keydown");
            e.keyCode = 9;
            $("#id_tags__tagautosuggest").trigger(e);
        }
    });
    $(document).ready(function() {
        $("#id_tags__tagautosuggest").tagspopup();
    });
})(jQuery);