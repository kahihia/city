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
            var that = this, closing=false;
            this.element[0].tagspopup = this;
            this.tags = [];
            this.autoTags = [];
            this.popup = $('.tags-popup');
            this.tagsContainer = $('.tags-container', this.popup);
            this.closeButton = $('.close-button', this.popup);
            $(this.element).on("focus", function() {
                if(that.tags.length>0 && !closing){
                    $(that.popup).show();
                    $(".modal-bg").show();
                    $(".as-selections").addClass("active");
                } else {
                    closing = false;
                    $(that.element).blur();
                }
                
            });
            $(this.closeButton).on("click", function() {
                $(that.popup).hide();
                $(".modal-bg").hide();
                $(".as-selections").removeClass("active");
            });

            $("#id_tags__tagautosuggest").on("keydown", function(e){
                that.setFree();
            });
            $("#id_tags__tagautosuggest").on("focus", function(e){
                that.setFree();
            });

            $(".as-selections .as-close").live("mousedown", function(){
                closing = true;
            });

            if($("#id_geo_city").val()){
                this.forCity($("#id_geo_city").val());
            } else {
                $.post("/events/ctags", {}, function(data){
                    tags = _.map(data.tags, function(tag){ return tag.name; });
                    that.loadTags(tags);
                });

            }
        },
        setFree: function(){
            var tags = $("#as-values-id_tags__tagautosuggest").val().split(",");
            tags = _.filter(tags, function(tag){ return tag; });
            if(tags.indexOf("Free")!==-1){
                $("#id_price_free").attr('checked', true);
            } else {
                $("#id_price_free").attr('checked', false);
            }
            setTimeout(function(){
                $("#id_price_free").trigger("changeFromTags");
            },10);
        },
        forCity: function(city){
            var data = {},that=this;
            if(typeof city==="string"){
                data.geo_city = city;
            } else if(typeof city === "number"){
                data.city_identifier = city;
            }
            $.post("/events/ctags", data, function(data){
                tags = _.map(data.tags, function(tag){ return tag.name; });
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
            var e;
            var tags = _.map($("#as-values-id_tags__tagautosuggest").val().split(","), function(tag){
                return tag.trim();
            });

            tags = _.filter(tags, function(tag){ return tag; });

            if(tags.indexOf(tag)===-1){
                $("#id_tags__tagautosuggest").val(tag);
                e = $.Event("keydown");
                e.keyCode = 9;
                $("#id_tags__tagautosuggest").trigger(e);
            }
        },
        removeTag: function(tag) {
            var button = $(".as-selections [data-value='"+tag+"'] a");
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
        },
        autoTagsDetect: function(description){
            var that=this,
                idescription = description.toLowerCase();
            _.each(this.tags, function(tag){
                var itag = tag.toLowerCase();
                if(idescription.indexOf(itag)!==-1){
                    that.addAutoTag(tag);
                } else {
                    that.removeAutoTag(tag);
                }

            });
        },
        addAutoTag: function(tag){
            if(tag==='Free') return;
            if($(".as-selection-item[data-value='"+tag+"']").length>0) return;
            if(this.autoTags.indexOf(tag)===-1){
                this.autoTags.push(tag);
                this.addTag(tag);
            }
        },
        removeAutoTag: function(tag){
            if(this.autoTags.indexOf(tag)!==-1){
                this.autoTags = _.without(this.autoTags, tag);
                this.removeTag(tag);
            }

        }
    });

    $(document).ready(function() {
        setTimeout(function(){
            $("#id_tags__tagautosuggest").tagspopup();
        },100);
    });
})(jQuery);