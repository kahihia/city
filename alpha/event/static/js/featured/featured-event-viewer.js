;(function($, window, document, undefined) {

    'use strict';

    var FeaturedEventsViewer = function(){
        this.viewer = $(".featured-events-viewer");
        this.content = $(".featured-events-viewer-content", this.viewer);
        this.next = $(".features-navigation .next");
        this.prev = $(".features-navigation .prev");
        this.pages = Math.ceil($(".features", this.viewer).length/6);
        this.pageNo = $(".features-navigation .page-no");
        this.currentPage = 1;

        this.initPageButtons();

        this.prev.on("click", this.scrollPrevPage.bind(this));
        this.next.on("click", this.scrollNextPage.bind(this));

        $("#featured-events-total").html(this.pages);
        $(".features-navigation [data-page=1]").addClass("current");
    };

    FeaturedEventsViewer.prototype = {
        _scroll: function(){
            var leftPosition = -1002*(this.currentPage-1);
            if(this.currentPage==this.pages) {
                leftPosition += (6 - $(".features", this.viewer).length % 6) * 167;
            }

            $(this.content).animate({
                "left": leftPosition + "px"
            });
            this.pageNo.html(this.currentPage);
            $(".features-navigation .page.current").removeClass("current");
            $(".features-navigation [data-page="+this.currentPage+"]").addClass("current");
        },
        scrollToPage: function(page){
            if(page>0 && page<=this.pages){
                this.currentPage = page;
                this._scroll();
            }            
        },
        scrollNextPage: function(){
            this.scrollToPage(this.currentPage+1);
        },
        scrollPrevPage: function(){
            this.scrollToPage(this.currentPage-1);
        },
        initPageButtons: function(){
            var that=this;
            for(var i=this.pages; i--; i>0) {
                var pageLink = dom("a", {
                    "class": "page",
                    "href": "javascript: void;",
                    "innerHTML": i+1,
                    "data-page": i+1
                });
                this.prev.after(pageLink);
                $(pageLink).on("click", function(){
                    that.scrollToPage($(this).data("page"));
                });
            }
        }
    };

    window.FeaturedEventsViewer = FeaturedEventsViewer;

})(jQuery, window, document);