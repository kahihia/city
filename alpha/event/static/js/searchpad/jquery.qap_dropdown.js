(function ($) {
    $.fn.qap_dropdown = function () {
        this.each(function () {
            if(this.isDropdown) return;
            this.isDropdown = true;
            var element = $(this),
                item_pos = jQuery(this).offset(),
                dropdownClass = jQuery(this).data("dropdown-class");

            // hasChild() workaround
            if (element.children('label.dropdown-label').length > 0 && element.children('label.dropdown-spanner').length > 0 && element.children('div.dropdown-content').length > 0) {
                return false;
            }

            var select = element.children('select');
            var label = $('<label class="dropdown-label"></label>');
            var content = $('<div class="dropdown-content">').addClass(dropdownClass);
            var spanner = $('<label class="dropdown-spanner"></label>');

            element.append(spanner);
            //element.append(content);
            element.append(label);

            $(content).css('left', (item_pos.left) + 'px').css('top', (item_pos.top + jQuery(this).outerHeight())).appendTo($("body"));

            var empty_element = (typeof(select.children('[val=""]').html()) == 'undefined' || select.children('[val=""]').html().empty()) ? select.children().first() : select.children('[val=""]');
            var selected_element = select.children(':selected').first(), selected_html = selected_element.html();

            var checkEmptiness = function () {
                if (select.val().length === 0) {
                    label.addClass('empty');
                } else {
                    label.removeClass('empty');
                }
            };

            if (selected_element.attr('data-source')) {
                $.ajax({
                    url:selected_element.attr('data-source'),
                    async:false,
                    success:function (data) {
                        selected_html = data;
                    }
                });
            }

            label.attr('for', element.attr('id'));
            label.html(selected_html || empty_element.html());

            checkEmptiness();

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

            element.on('click', function (e) {
                if($(this).attr("disabled")) return;
                item_pos = jQuery(this).offset();
                $(content).css('left', (item_pos.left) + 'px').css('top', (item_pos.top + jQuery(this).outerHeight()));
                e.stopPropagation();

                var already_toggled = $('.dropdown.toggled');

                if (already_toggled.length > 0 && element.hasClass('toggled') !== true){
                    already_toggled.removeClass('toggled');
                    $('.dropdown-content.toggled').removeClass('toggled');
                }

                element.toggleClass('toggled');
                content.toggleClass('toggled');
            });

            select.children('option').each(function (i, option) {
                option = $(option);

                var child = $('<div class="dropdown-child"></div>');
                var html = option.html(), val = option.val();

                if (option.attr('data-source')) {
                    $.ajax({
                        url:option.attr('data-source'),
                        async:false,
                        success:function (data) {
                            html = data;
                        }
                    });
                }

                child.html(html);
                child.attr('value', val);

                content.append(child);

                child.click(function (e) {
                    e.stopPropagation();
                    select.children('[selected]').removeAttr('selected');
                    $(this).attr('selected', 'selected');

                    select.val($(this).attr('value'));
                    label.html($(this).html());

                    checkEmptiness();
                    $('.dropdown.toggled').removeClass('toggled');
                    $('.dropdown-content.toggled').removeClass('toggled');

                    $(element).trigger("dropdown.change");
                });
            });

            if(element.data("value")){
                $("[value='"+ element.data("value") +"']", content).click();
            }
        });
    };
})(jQuery);