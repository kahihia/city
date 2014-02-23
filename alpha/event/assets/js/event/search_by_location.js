;(function($, window, document, undefined) {
    'use strict';

    var _ = window._,
        Cityfusion = window.Cityfusion;

    var SearchByLocation = function(){
        var that = this, request,
            currentSearchValue = $(".location-text-box input").val();

        this.widget = $(".location-selection-wrapper");

        this.searchListPopup = $(".search-lists");

        this.searchList = $(".search-lists ul");
        this.searchInput = $(".location-text-box input");

        this.searchUrl = "/events/locations?search=";

        this.initLocationLinks();

        setInterval(function(){
            if(that.searchInput.val() !== currentSearchValue) {
                if(request) request.abort();

                currentSearchValue = that.searchInput.val();
                request = $.ajax({
                    url: that.searchUrl + currentSearchValue,
                    success: function(data) {
                        that.refreshLocationList(data);
                    }
                });
            }
        }, 500);

        request = $.ajax({
            url: that.searchUrl + currentSearchValue,
            success: function(data) {
                that.refreshLocationList(data);
            }
        });

        this.searchInput.on("hover", this.showList.bind(this));
        this.searchInput.on("keydown", this.inputKeyPressed.bind(this))
        this.widget.on("mouseout", this.hideWithTimeout.bind(this));
        $(document).on("click", this.hideIfNotPopup.bind(this));
    };

    SearchByLocation.prototype = {
        initLocationLinks: function(){
            var that=this;
            $("li.item a", this.searchList).each(function(){
                $(this).on("click", function(){
                    that.findByLocation(
                        $(this).data("location-id"),
                        $(this).data("location-type")
                    );
                });
            });
        },
        findByLocation: function(id, type, text){
            window.location = window.filters.removeFilter("page").setFilter("location", type+"|"+id).getURL();
        },

        refreshLocationList: function(data){
            $("li.item", this.searchList).remove();

            _.forEach(data.locations, function(location) {
                this.searchList.append(this.appendLink(location));
            }, this);

            this.initLocationLinks();
        },

        appendLink: function(data) {
            var link, link_text, li,
                currentLocationId = this.searchInput.attr("data-location-id");

            link_text = data.name;
            if(data.count) {
                link_text += " (" + data.count + ")";
            }

            link = $("<a href='javascript:void(0);'></a>").html(link_text);
            link.attr("data-location-id", data.id);
            link.attr("data-location-type", data.type);

            li = $("<li />", {"class": "item"}).append(link);
            if(data.id == currentLocationId) {
               li.addClass("selected");
            }

            return li;
        },
        showList: function(){
            this.searchInput.focus();
            this.searchListPopup.show();
            this.widget.addClass("active");
        },
        hideList: function(){
            this.searchListPopup.hide();
            this.widget.removeClass("active");
        },
        hideIfNotPopup: function(e){
            if($(e.target).hasClass("location-selection-wrapper") || $(e.target).parents(".location-selection-wrapper").length>0){

            } else {
                this.hideList();
            }
        },
        hideWithTimeout: function(){
            var timeout = setTimeout(this.hideList.bind(this), 1000);

            this.widget.on("mouseover", function(){
                clearTimeout(timeout);
            });
        },
        inputKeyPressed: function(e){
            var keyCode = $.ui.keyCode;
            switch (e.keyCode ) { 
                case keyCode.DOWN:
                   this.selectNextLink();
                   break;
                case keyCode.UP:
                   this.selectPrevLink();
                   break;
 
                case keyCode.ENTER:
                    this.triggerActiveLink();
                    break;
            }
        },
        selectNextLink: function(){
            var selectedLink = $("a.selected", this.searchListPopup);
            selectedLink.removeClass("selected");
            if(selectedLink.length > 0) {
                var nextLink = selectedLink.parent().next("li").find("a");
                if(nextLink.length>0) {
                    nextLink.addClass("selected");
                } else {
                    $("a:first", this.searchListPopup).addClass("selected");
                }
            } else {
                $("a:first", this.searchListPopup).addClass("selected");
            }
        },
        selectPrevLink: function(){
            var selectedLink = $("a.selected", this.searchListPopup);
            selectedLink.removeClass("selected");
            if(selectedLink.length > 0) {
                var prevLink = selectedLink.parent().prev("li").find("a");
                if(prevLink.length>0) {
                    prevLink.addClass("selected");
                } else {
                    $("a:last", this.searchListPopup).addClass("selected");
                }
            } else {
                $("a:last", this.searchListPopup).addClass("selected");
            }
        },
        triggerActiveLink: function(){
            $("a.selected", this.searchListPopup).trigger("click");
        }
    };

    window.SearchByLocation = SearchByLocation;

})(jQuery, window, document);