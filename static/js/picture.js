(function($) {

    var screen_height;

    function getClientHeight() {
        if(window.innerHeight) {
            return window.innerHeight;
        } else {
            if(document.documentElement.clientHeight) {
                return document.documentElement.clientHeight;
            } else {
                return document.body.offsetHeight;
            }
        }
    }
    screen_height = getClientHeight();
    $(document).on("ready page:load", function() {
        screen_height = getClientHeight();
    });
    $(window).resize(function() {
        screen_height = getClientHeight();
    });

    $.widget("ui.picture", {
        _create: function() {
            var that = this;
            this.cropping = $("#id_cropping");
            this.picture = $("#id_picture");
            if($(this.cropping).next().length > 1) {
                this.cropping_image = $(this.cropping).next();
                this.initJcrop();
            }
            this.popup = $(".full-screen-popup");
            this.save_button = $(".save-button", this.popup);
            $(this.save_button).on('click', function() {
                $.fancybox.close();
                that.saveThumbnail();
            });

            $(".picture-thumb").on("click", function(){
                if(that.cropping_image) {
                    $.fancybox($(that.popup), {
                        autoSize: true,
                        closeBtn: false,
                        hideOnOverlayClick: false
                    });
                }
            });
            
            this.uploader = new qq.FileUploader({
                action: "/events/ajax-upload",
                element: this.element[0],
                multiple: false,
                allowedExtensions: ['jpg', 'jpeg', 'png', 'gif'],
                sizeLimit: 33554432,
                onComplete: function(id, fileName, responseJSON) {
                    if(responseJSON.success) {
                        $("#id_picture_src").val(responseJSON.path);
                        that.changeImage(responseJSON.path);
                        $(".modal-bg").hide();                      
                        
                        $.fancybox($(that.popup), {
                            autoSize: true,                     
                            closeBtn: false,                        
                            hideOnOverlayClick: false
                        });                          
                    } else {                        
                        console.log && console.log("upload failed!");
                        alert("Something go wrong on server. Please contact administrator.")
                        $(".modal-bg").hide();
                    }
                }, 
                onSubmit: function(){
                    $(".modal-bg").show();
                },
                params: {
                    'csrf_token': crsf_token,
                    'csrf_name': 'csrfmiddlewaretoken',
                    'csrf_xname': 'X-CSRFToken',
                }
            });
            if($("#id_picture_src").val()){
                this.changeImage(
                    $("#id_picture_src").val()
                );
            }
        },
        initJcrop: function() {
            var that = this, selected,
                style_img_warning = 'div.jcrop-image.size-warning .jcrop-vline{border:1px solid red; background: none;}' + 'div.jcrop-image.size-warning .jcrop-hline{border:1px solid red; background: none;}';
            $("<style type='text/css'>" + style_img_warning + "</style>").appendTo('head');

            if($("#id_cropping").val()){
                selected = _.map($("#id_cropping").val().split(","), function(val){
                    return parseInt(val);
                });                    
            } else {
                selected = [0, 0, $(this.popup).data("thumb-height"), $(this.popup).data("thumb-width")];
            }

            $(this.cropping_image).Jcrop({
                aspectRatio: 1,
                minSize: [50, 50],
                boxWidth: 800,
                boxHeight: 500,
                setSelect: selected,
                onSelect: function(selected) {
                    $(".picture-thumb").addClass("result");
                    that.selected = selected;
                    that.update_selection(selected);
                    that.jcrop && that.showPreview(selected, that.jcrop.getWidgetSize());
                },
                onChange: function(selected) {
                    that.jcrop && that.showPreview(selected, that.jcrop.getWidgetSize());
                }
            }, function() {
                that.jcrop = this;
                that.showPreview({
                    x:selected[0],
                    y:selected[1],
                    w:selected[2]-selected[0],
                    h:selected[3]-selected[1]
                }, that.jcrop.getWidgetSize());
            });            
        },
        changeImage: function(image_path) {
            var that = this;            
            if(this.cropping_image) {
                $(this.cropping_image).attr('src', image_path); 
                this.jcrop.setImage(image_path);
            } else {
                this.cropping_image = $("<img id='id_cropping-image'>");

                this.cropping_image.attr('src', image_path);
                $(this.cropping).after(this.cropping_image);
                that.initJcrop();
            }            
            this.changeImagePosition();
        },
        saveThumbnail: function() {
            $(this.cropping).val(

            );
        },
        changeImagePosition: function() {
            var image_height = $(this.image_cropping).height();

        },
        crop_indication: function(selected) {
            // indicate if cropped area gets smaller than the specified minimal cropping
            var $jcrop_holder = this.cropping.siblings('.jcrop-holder');
            var min_width = $(this.popup).data("thumb-width");
            var min_height = $(this.popup).data("thumb-height");
            if((selected.w < min_width) || (selected.h < min_height)) {
                $jcrop_holder.addClass('size-warning');
            } else {
                $jcrop_holder.removeClass('size-warning');
            }
        },
        update_selection: function(selected) {
            if(this.cropping.data('size-warning')) {
                this.crop_indication(selected);
            }
            this.cropping.val(
                new Array(selected.x, selected.y, selected.x2, selected.y2).join(',')
            );
        },
        showPreview: function(coords, widgetSize) {
            var rx = 180 / coords.w;
            var ry = 180 / coords.h;

            $('.picture-thumb .preview')[0].src = $(this.cropping_image)[0].src;
            $('.picture-thumb .preview').css({
                width: Math.round(rx * $(this.cropping_image)[0].width) + 'px',
                height: Math.round(ry * $(this.cropping_image)[0].height) + 'px',
                marginLeft: '-' + Math.round(rx * coords.x) + 'px',
                marginTop: '-' + Math.round(ry * coords.y) + 'px'
            });
        }
    });
    $(document).ready(function() {
        setTimeout(function(){
            $("#file-uploader").picture();    
        },100);        
    });
})(jQuery);