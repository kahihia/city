;(function($, window, document, undefined) {
    'use strict';    

    function Dropdown(element, options){
        var that=this;
        element = $(element);
        this.element = element;
        this.itemPosition = jQuery(element).offset();
        this.dropdownClass = jQuery(element).data("dropdown-class");

        this.select = element.children('select');
        this.build();

        this.element.on('click', this.open.bind(this));

        if(that.element.data("value")){
            $("[value='"+ this.element.data("value") +"']", this.content).click();
        }

        if(options) {
            this.onChange = options.onChange;
        }
        
    }

    Dropdown.prototype = {
        checkEmptiness: function(){
            if (this.select.val().length === 0) {
                this.label.addClass('empty');
            } else {
                this.label.removeClass('empty');
            }
        },
        empty: function(){
            this.label.remove();
            this.spanner.remove();
        },
        refresh: function(){
            this.empty();
            this.content.empty();
            this.select = this.element.children('select');
            this.build();
        },
        buildBasicElements: function(){
            this.label = $('<label class="dropdown-label"></label>');
            this.content = $('<div class="dropdown-content">').addClass(this.dropdownClass);
            this.spanner = $('<label class="dropdown-spanner"></label>');
            this.element.append(this.spanner);
            this.element.append(this.label);

            $(this.content).css('left', (this.itemPosition.left) + 'px').css('top', (this.itemPosition.top + jQuery(this.element).outerHeight())).appendTo($("body"));

            this.emptyElement = (typeof(this.select.children('[val=""]').html()) == 'undefined' || this.select.children('[val=""]').html().empty()) ? this.select.children().first() : this.select.children('[val=""]');
            this.selectedElement = this.select.children(':selected').first();
            this.selectedHTML = this.selectedElement.html();

            if (this.selectedElement.attr('data-source')) {
                $.ajax({
                    url: this.selectedElement.attr('data-source'),
                    async: false,
                    success: function (data) {
                        that.selectedHTML = data;
                    }
                });
            }

            this.label.attr('for', this.element.attr('id'));
            this.label.html(this.selectedHTML || this.emptyElement.html());
        },
        buildOptions: function(){
            var that = this;
            this.select.children('option').each(function (i, option) {
                var child, html, value;
                option = $(option);

                child = $('<div class="dropdown-child"></div>');
                html = option.html();
                value = option.val();

                if (option.attr('data-source')) {
                    $.ajax({
                        url: option.attr('data-source'),
                        async:false,
                        success:function (data) {
                            html = data;
                        }
                    });
                }

                child.html(html);
                child.attr('value', value);

                that.content.append(child);

                child.click(function (e) {
                    e.stopPropagation();
                    that.select.children('[selected]').removeAttr('selected');
                    $(this).attr('selected', 'selected');

                    that.select.val($(this).attr('value'));
                    that.select.change();
                    that.label.html($(this).html());

                    that.checkEmptiness();
                    $('.dropdown.toggled').removeClass('toggled');
                    $('.dropdown-content.toggled').removeClass('toggled');

                    that.onChange && that.onChange(value, html);

                    $(that.element).trigger("dropdown.change");
                });
            });
        },
        open: function(e){
            var alreadyToggled;
            if(this.element.attr("disabled")) return;
            this.itemPosition = jQuery(this.element).offset();

            $(this.content).css('left', (this.itemPosition.left) + 'px').css('top', (this.itemPosition.top + jQuery(this.element).outerHeight()));
            e.stopPropagation();

            alreadyToggled = $('.dropdown.toggled');

            if (alreadyToggled.length > 0 && this.element.hasClass('toggled') !== true){
                alreadyToggled.removeClass('toggled');
                $('.dropdown-content.toggled').removeClass('toggled');
            }

            this.element.toggleClass('toggled');
            this.content.toggleClass('toggled');
        },
        build: function(){
            this.buildBasicElements();
            this.checkEmptiness();
            this.buildOptions();
        }
    }

    $.fn.qap_dropdown = function () {
        var objects = [];
        this.each(function () {
            objects.push(new Dropdown(this));
        });

        return objects;
    };

    $(document).on("ready page:load", function(){
        $(document).click(function () {
            $('.dropdown.toggled').removeClass('toggled');
            $('.dropdown-content.toggled').removeClass('toggled');
        });

        $(document).keydown(function (e) {
            e = e || window.event;

            if (e.keyCode == 27) {
                $('.dropdown.toggled').removeClass('toggled');
                $('.dropdown-content.toggled').removeClass('toggled');
            }
        });
    });

    window.Dropdown = Dropdown;

})(jQuery, window, document);
