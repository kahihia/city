;(function($, window, document, undefined) {

    'use strict';

    var SimilarEvents = function(){
        this.viewer = $(".similar-events-wrapper");
        this.content = $(".similar-events-ul", this.viewer);
        this.next = $(".next", this.viewer);
        this.prev = $(".prev", this.viewer);
        this.pages = Math.ceil($("a", this.viewer).length/6);
        this.pageNo = $(".page-no", this.viewer);
        this.currentPage = 1;

        this.prev.on("click", this.scrollPrevPage.bind(this));
        this.next.on("click", this.scrollNextPage.bind(this));

        $("#similar-events-total").html(this.pages);
    };

    SimilarEvents.prototype = {
        _scroll: function(){
            $(this.content).animate({
                "top": -210*(this.currentPage-1) + "px"
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

    window.SimilarEvents = SimilarEvents;

})(jQuery, window, document);