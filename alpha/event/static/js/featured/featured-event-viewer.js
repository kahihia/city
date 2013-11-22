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

        this.prev.on("click", this.scrollPrevPage.bind(this));
        this.next.on("click", this.scrollNextPage.bind(this));

        $("#featured-events-total").html(this.pages);
    };

    FeaturedEventsViewer.prototype = {
        _scroll: function(){
            $(this.content).animate({
                "left": -1002*(this.currentPage-1) + "px"
            });
            this.pageNo.html(this.currentPage);
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
        }
    };

    window.FeaturedEventsViewer = FeaturedEventsViewer;

})(jQuery, window, document);