$(document).ready(function() {
    $('ul.tabs').each(function() {
        $(this).find('li').each(function(i) {
            $(this).click(function(){
                $(this).addClass('current').siblings().removeClass('current')
                    .parents('div.tabs-container').find('div.box').eq(i).fadeIn(150).siblings('div.box').hide();
            });
        });
    });
});