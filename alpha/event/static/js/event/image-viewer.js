;(function($, window, document, undefined) {

    'use strict';

    var ImageViewer = function(){
        this.viewer = $(".image-viewer");
        this.content = $(".image-viewer-content", this.viewer);
        this.next = $(".next", this.viewer);
        this.prev = $(".prev", this.viewer);
        this.pages = $("a", this.viewer).length;
        this.pageNo = $(".page-no", this.viewer);
        this.currentPage = 1;

        this.prev.on("click", this.scrollPrevPage.bind(this));
        this.next.on("click", this.scrollNextPage.bind(this));
    };

    ImageViewer.prototype = {
        _scroll: function(){
            $(this.content).animate({
                "left": -265*(this.currentPage-1) + "px"
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

    window.ImageViewer = ImageViewer;

})(jQuery, window, document);