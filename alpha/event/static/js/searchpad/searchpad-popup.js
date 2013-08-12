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

        this.initAuthRequired();
        
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

            links.on("click", function(e){
                var link=this;
                // Jump to Date link change should trigger befor links will be loaded
                setTimeout(function(){
                    var href = $(link).attr("href");
                    that.loadSearchPadPage(href);
                }, 10);

                e.preventDefault();
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
            var that=this;
            this.ajaxifyLinks();
            this.initSearchTags();
            new window.JumpToDate(this.popup);
            if(typeof FB !== "undefined" && FB !== null){
                FB.XFBML.parse()  
            }

            this.eventActions = new window.EventActions($(".event-details", this.popup));

            if($(".auth-required-popup").length>0){
                $(".auth-required").on("click", function(e){
                    $(that.dialogContainer).dialog('open');
                    e.stopPropagation();
                });
            }

                
        },
        initSearchTags: function(){
            var that=this;
            $(".search-pad-content .searchTags").tagit({
                afterTagRemoved: function(e, ui){
                    that.loadSearchPadPage(
                        "/events/search/" + $(ui.tag).data("remove-url")
                    );
                }
            });
        },
        initAuthRequired: function(){
            if($(".auth-required-popup").length>0){
                this.dialogContainer = $(".auth-required-popup").dialog({
                    dialogClass: "event-action-ui-dialog",
                    resizable: false,
                    width: 390,
                    autoOpen: false
                });
            }
        }
    };

    $(document).on("ready page:load", function(){
        window.searchPadPopup = new SearchPadPopup();
    });

})(jQuery, window, document);