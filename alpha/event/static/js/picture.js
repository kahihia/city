(function($) {

    var screen_height;

    function getClientHeight() {
        if(window.innerHeight) {
            return window.innerHeight;
        } else {
            if(document.documentElement.clientHeight) {
                return document.documentElement.clientHeight;
            } else {
                document.body.offsetHeight;
            }
        }
    }
    screen_height = getClientHeight();
    $(window).load(function() {
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
                $(that.popup).hide();
                $(".modal-bg").hide();
                that.saveThumbnail();
            });
            
            this.uploader = new qq.FileUploader({
                action: "/events/ajax-upload",
                element: this.element[0],
                multiple: false,
                allowedExtensions: ['jpg', 'jpeg', 'png', 'gif'],
                onComplete: function(id, fileName, responseJSON) {
                    if(responseJSON.success) {
                        that.changeImage(responseJSON.path);
                        
                        // User must not see how jcrop widget rewriting itself when new image coming
                        setTimeout(function(){
                            $(that.popup).show();
                        },500);
                    } else {
                        console.log("upload failed!");
                    }
                },
                onSubmit: function(id, fileName, input) {
                    var picture = $("#id_picture");
                    setTimeout(function() {
                        picture.after(input);
                        picture.remove();
                    }, 10);
                    $(input).attr("id", "id_picture");
                    $(input).attr("name", "picture");
                    $(".modal-bg").show();
                },
                params: {
                    'csrf_token': crsf_token,
                    'csrf_name': 'csrfmiddlewaretoken',
                    'csrf_xname': 'X-CSRFToken',
                },
            });
        },
        initJcrop: function() {
            var that = this,
                style_img_warning = 'div.jcrop-image.size-warning .jcrop-vline{border:1px solid red; background: none;}' + 'div.jcrop-image.size-warning .jcrop-hline{border:1px solid red; background: none;}';
            $("<style type='text/css'>" + style_img_warning + "</style>").appendTo('head');

            $(this.cropping_image).Jcrop({
                aspectRatio: 1,
                minSize: [50, 50],
                boxWidth: 800,
                boxHeight: 500,
                setSelect: [0, 0, $(this.popup).data("thumb-height"), $(this.popup).data("thumb-width")],                
                onSelect: function(selected) {
                    that.selected = selected;
                    that.update_selection(selected);
                    that.jcrop && that.showPreview(selected, that.jcrop.getWidgetSize());
                },
                onChange: function(selected) {
                    that.jcrop && that.showPreview(selected, that.jcrop.getWidgetSize());
                }
            }, function() {
                that.jcrop = this;
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
            this.cropping.val(new Array(
            selected.x, selected.y, selected.x2, selected.y2).join(','));
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
        $("#file-uploader").picture();
    });
})(jQuery);