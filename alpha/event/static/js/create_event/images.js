;(function($, window, document, undefined) {
    'use strict';

    function ImageUploader(callback){
        var that = this;
        this.uploader = new qq.FileUploader({
            action: "/events/ajax-upload",
            multiple: false,
            element: $("#images-uploader")[0],
            allowedExtensions: ['jpg', 'jpeg', 'png', 'gif'],
            sizeLimit: 33554432,
            onComplete: function(filename, responseJSON) {
                if(responseJSON.success) {
                    callback.call(filename, responseJSON);
                } else {
                    this.failed = true;
                }
            },            
            params: {
                'csrf_token': crsf_token,
                'csrf_name': 'csrfmiddlewaretoken',
                'csrf_xname': 'X-CSRFToken'
            },
            template: '<div class="qq-uploader">' +
                '<div class="qq-upload-drop-area"><span>Drop files here to upload</span></div>' +
                '<div class="qq-upload-button">Upload a file</div>' +
                '<div class="qq-upload-indicator-block inv" data-id="upload_indicator_block">' +
                    '<img src="/static/images/mini-ajax-loader.gif" alt="" />' +
                    '<a class="qq-uploading-cancel" data-id="uploading_cancel" href="javascript:void(0);">' +
                        'Cancel' +
                    '</a>' +
                '</div>' +
                '<ul class="qq-upload-list"></ul>' +
             '</div>'
        });
    }

    function CroppedImageWidget(filename, filepath, cropping, imagesWidget){
        var that = this;
        this.imagesWidget = imagesWidget;
        this.filepath = filepath;
        this.cropping = cropping;

        this.element = dom("div", {"class": "attachment"}, [
            dom("span", {"innerHTML": filename}),
            this.selectButton = dom("div", {"class": "select-image-button"}),
            this.removeButton = dom("div", {"class": "remove-image-button"})
        ]);

        $(this.removeButton).on("click", function(){
            that.remove();
        });

        $(this.selectButton).on("click", function(){
            that.select();
        });
    }

    CroppedImageWidget.prototype = {
        select: function(){
            this.imagesWidget.setActiveCroppedImage(this);
            this.element.addClass("active");
        },
        unselect: function(){
            this.element.removeClass("active");
        },
        remove: function(){
            this.imagesWidget.removeCroppedImage(this);
        },
        preview: function(){
            $.fancybox($(this.previewPopup()), {
                autoSize: true,
                closeBtn: false,
                hideOnOverlayClick: false
            });
        },
        setSelected: function(selected){
            this.selected = selected;
        }

    }

    function ActiveCroppedWidget(){
        var that = this;
        this.activeWidget = null;
        this.image = dom("image", {
            src: "/static/images/default-event.jpg"
        });

        $(this.image).Jcrop({
            aspectRatio: 1,
            minSize: [50, 50],
            boxWidth: 800,
            boxHeight: 500,
            onSelect: function(selected){
                if(that.activeWidget) {
                    that.activeWidget.setSelected(selected);
                    that.showPreview(selected, that.jcrop.getWidgetSize());
                }
            },
            onChange: function(selected){
              if(that.activeWidget) {
                    that.activeWidget.setSelected(selected);
                    that.showPreview(selected, that.jcrop.getWidgetSize());
                }  
            }
        }, function(){
            that.jcrop = this;
        });
    }

    ActiveCroppedWidget.prototype = {
        setActiveWidget: function(croppedImage){
            this.activeWidget = croppedImage;
        },
        createPreview: function(){
            this.previewContainer = dom("div", {"class": "image-thumb"}, [
                this,preview = dom("image", {
                    "class": "preview"
                })
            ]);
        },
        showPreview: function(){
            var rx, ry;
            if(!this.preview) {
                this.createPreview();
            }

            this.preview.src = this.activeWidget.filepath;
            

            rx = 180 / this.activeWidget.selected.w;
            ry = 180 / this.activeWidget.selected.h;

            $(this.preview).css({
                width: Math.round(rx * $(this.image).width()) + 'px',
                height: Math.round(ry * $(this.image).height()) + 'px',
                marginLeft: '-' + Math.round(rx * this.activeWidget.selected.x) + 'px',
                marginTop: '-' + Math.round(ry * this.activeWidget.selected.y) + 'px'  
            });
        }
    }

    function CroppedImages(){
        var that = this;

        this.images = [];
        this.uploader = new ImageUploader(function(filename, responseJSON){
            that.addCroppedImages(filename, responseJSON.filepath);
        });

        this.activeCroppedWidget = new ActiveCroppedWidget();
    }

    CroppedImages.prototype = {
        setActiveCroppedImage: function(croppedImage){
            this.activeCroppedWidget.setActiveWidget(croppedImage);

        },
        addCroppedImage: function(filename, filepath, cropping){
            var widget = new CroppedImageWidget(filename, filepath, cropping, this);
            this.images.push(widget);
            $(this.element).append(widget.element);
        },
        removeCroppedImage: function(widget){
            this.images.splice(this.images.indexOf(widget), 1);
            $(widget.element).remove();

            this.saveValue();
        },
        loadImages: function(){
            var value, images;

            value = $(this.input).val();
            if(value) {
                cropped_images = value.split(";");

                cropped_images.forEach(function(cropped_image){
                    var data = cropped_image.split("!"),
                        image = data[0],
                        cropping = data[1].split(",");

                    this.addCroppedImage(image.replace(/^.*(\\|\/|\:)/, ''), image, cropping);
                }, this);
            }
        }
    }

    $(document).on("ready page:load", function(){
        new CroppedImages(
            document.getElementById("id_cropped_images")
        );
    });

})(jQuery, window, document);
    