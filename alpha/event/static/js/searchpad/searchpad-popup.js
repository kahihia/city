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
        $(document).on("click", this.closeIfNotPopup.bind(this));
        
    };

    SearchPadPopup.prototype = {
        open: function(){
            this.popup.show();
        },
        close: function(){
            this.popup.hide();
        },
        closeIfNotPopup: function(e){
            if(
                $(e.target).hasClass("search-pad-popup-open-button") || $(e.target).parents(".search-pad-popup-open-button").length>0 ||
                $(e.target).hasClass("jump-popup") || $(e.target).parents(".jump-popup").length>0 ||
                
                $(e.target).hasClass("search-pad-popup-content") || $(e.target).parents(".search-pad-popup-content").length>0 || $(e.target).parents("#ui-datepicker-div").length>0 || $(e.target).parents(".ui-datepicker-header").length>0
            ){
                
            } else {
                this.close();
            }
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

                    return false;
                });
            }

            this.initAddThis();
        },
        initSearchTags: function(){
            var that=this;
            $(".search-pad-content .searchtags").tagit({
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
        },
        initAddThis: function() {
            if(window.addthis) {
                var addThisCell = $("[data-id=social_buttons_cell]").empty();
                var toolbox = $("<div/>", {
                    "id": "addthis_toolbox",
                    "class": "addthis_toolbox addthis_default_style addthis_16x16_style"
                });

                var svcs = ["facebook", "twitter", "pinterest_share", "google_plusone_share", "linkedin", "myspace", "blogger", "email", "compact"];

                for(var i in svcs) {
                    toolbox.append("<a class='addthis_button_" + svcs[i] + "'></a>");
                }

                toolbox.append("<a id='addthis_counter' class='addthis_counter addthis_bubble_style'></a>");

                addThisCell.append(toolbox);
                window.addthis.toolbox("#addthis_toolbox");
                window.addthis.counter("#addthis_counter");
            }
        }
    };

    $(document).on("ready page:load", function(){
        window.searchPadPopup = new SearchPadPopup();
    });

})(jQuery, window, document);