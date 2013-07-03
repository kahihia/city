;(function($, window, document, undefined) {

    'use strict';

    var SearchPadPopup = function(){
        var that=this;
        this.openButton = $(".search-pad-popup-open-button");
        this.popup = $(".search-pad-popup");

        this.openButton.on("click", function(){            
            that.open();
        });

        this.loadSearchPadPage("/events/search");
        
    };

    SearchPadPopup.prototype = {
        open: function(){
            $.fancybox($(this.popup), {                
                closeBtn: true,
                hideOnOverlayClick: false,
                width: 1024,
                padding: 5
            });

        },
        ajaxifyLinks: function(){
            var links = $("a.ajax", this.popup),
                that = this;
            console.log(links);
            links.on("click", function(e){
                var href = $(this).attr("href");               

                e.preventDefault();
                that.loadSearchPadPage(href)
                return false;
            });
        },
        loadSearchPadPage: function(query){
            var that=this;
            query = query.replace(/\s/g, function(s){ 
                return encodeURIComponent(s) 
            });

            this.popup.load(query, function() {
                that.updateUI();
            });
        },
        updateUI: function(){
            this.ajaxifyLinks();
            this.initSearchTags();
            new window.JumpToDate(this.popup);
            if(typeof FB !== "undefined" && FB !== null){
                FB.XFBML.parse()  
            }

            this.eventActions = new window.EventActions($(".event-details", this.popup));
        },
        initSearchTags: function(){
            var that=this;
            $("#searchTags ").tagit({
                afterTagRemoved: function(e, ui){
                    that.loadSearchPadPage(
                        "/events/search/" + $(ui.tag).data("remove-url")
                    );
                }
            });
        }
    };

    $(document).on("ready page:load", function(){
        window.searchPadPopup = new SearchPadPopup();
    });

})(jQuery, window, document);