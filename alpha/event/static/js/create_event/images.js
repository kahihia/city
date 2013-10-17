;(function($, window, document, undefined) {
    'use strict';

    function ImageUploader(callback){
        var that = this;
        this.uploader = new qq.FileUploader({
            action: "/events/ajax-upload",
            multiple: false,
            element: document.getElementById("images-uploader"),
            allowedExtensions: ['jpg', 'jpeg', 'png', 'gif'],
            sizeLimit: 33554432,
            onComplete: function(id, filename, responseJSON) {
                if(responseJSON.success) {
                    callback(filename, responseJSON);
                    that.hideProgressBar();
                } else {
                    this.failed = true;
                }
            },
            onSubmit: function(id, fileName) {
                that.showProgressBar();
                $(".image-upload-cancel").attr("data-file-id", id);
            },
            params: {
                'csrf_token': crsf_token,
                'csrf_name': 'csrfmiddlewaretoken',
                'csrf_xname': 'X-CSRFToken'
            },
            template: '<div class="qq-uploader">' +
                '<div class="qq-upload-button">Upload a file</div>' +
                '<div class="qq-upload-indicator-block image-upload-progress-bar inv" data-id="upload_indicator_block">' +
                    '<img src="/static/images/mini-ajax-loader.gif" alt="" />' +
                    '<a class="qq-uploading-cancel image-upload-cancel" data-id="uploading_cancel" href="javascript:void(0);">' +
                        'Cancel' +
                    '</a>' +
                '</div>' +
                '<ul class="qq-upload-list"></ul>' +
             '</div>'
        });

        $("images-uploader .image-upload-cancel").on("click", this.cancelUpload.bind(this))
    }

    ImageUploader.prototype = {
        showProgressBar: function(){
            $(".image-upload-progress-bar").removeClass("inv");
        },
        hideProgressBar: function(){
            $(".image-upload-progress-bar").addClass("inv");
        },
        cancelUpload: function(){
            var fileId = $("images-uploader .image-upload-cancel").data("file-id");
            this.uploader._handler.cancel(fileId);
            this.hideProgressBar();

        }
    }

    function CroppingImageWidget(filename, filepath, cropping, imagesWidget){
        var that = this;
        this.imagesWidget = imagesWidget;
        this.filepath = filepath;
        this.selected = {
            x: cropping[0],
            y: cropping[1],
            x2: cropping[2],
            y2: cropping[3],
            w: cropping[2]-cropping[0], 
            h: cropping[3]-cropping[1]
        };

        this.cropping = cropping;

        this.element = dom("div", {"class": "attachment"}, [
            dom("span", {"innerHTML": filename}),
            this.removeButton = dom("i", {"class": "icon-remove"}),
            this.editButton = dom("i", {"class": "icon-pencil"}),
            dom("div", {"class": "picture-thumb result"}, [
                this.preview = dom("img", {
                    "src": filepath,
                    "class": "preview"
                })
            ])
        ]);

        this.initPopup();

        setInterval(function(){
            that.showPreview();
        }, 500);

        $(this.removeButton).on("click", function(){
            that.remove();
        });

        $(this.editButton).on("click", function(){
            that.edit();
        });

        $(this.preview).on("click", function(){
            that.edit();
        });
    }

    CroppingImageWidget.prototype = {        
        remove: function(){
            this.imagesWidget.removeCroppedImage(this);
        },
        edit: function(){
            this.openPopup();
        },
        setSelected: function(selected){
            this.selected = selected;
        },
        getValue: function(){
            return this.filepath + "!" + [this.selected.x, this.selected.y, this.selected.x2, this.selected.y2].join(",");
        },
        initPopup: function(){
             this.popup = dom("div", {
                "class": "full-screen-popup",
                "data-thumb-width": "180",
                "data-thumb-height": "180"
            }, [
                this.image = dom("img", {
                    "class": "cropping-image",
                    "src": this.filepath
                }),
                this.saveButton = dom("div", {"class": "save-button", "innerHTML": "Save image"}),
                this.cancelButton = dom("div", {"class": "cancel-button", "innerHTML": "Cancel"})
            ]);

            this.initJcrop();

            $(document.body).append(this.popup);

            $(this.cancelButton).on('click', function() {
                $.fancybox.close();
            });

            $(this.saveButton).on('click', function() {
                $.fancybox.close();
                // that.saveThumbnail();
            });

        },
        openPopup: function(){
            $.fancybox($(this.popup), {
                autoSize: true,
                closeBtn: false,
                hideOnOverlayClick: false
            });
        },
        showPreview: function(){
            var rx, ry;            

            rx = 180 / this.selected.w;
            ry = 180 / this.selected.h;

            $(this.preview).css({
                width: Math.round(rx * $(this.image).width()) + 'px',
                height: Math.round(ry * $(this.image).height()) + 'px',
                marginLeft: '-' + Math.round(rx * this.selected.x) + 'px',
                marginTop: '-' + Math.round(ry * this.selected.y) + 'px'  
            });
        },
        initJcrop: function(){
            var that = this;
            $(this.image).Jcrop({
                aspectRatio: 1,
                minSize: [50, 50],
                boxWidth: 800,
                boxHeight: 500,
                element: this.image,
                setSelect: this.cropping,
                onSelect: this.onSelect.bind(this),
                onChange: this.onSelect.bind(this)
            }, function(){
                that.jcrop = this;
            });
        },
        onSelect: function(selected){
            if(this.jcrop) {
                this.selected = selected;
                this.showPreview(selected, this.jcrop.getWidgetSize());
                this.imagesWidget.saveValue();
            }

        }
    }    

    function CroppedImages(input){
        var that = this;

        this.input = input;
        this.images = [];
        this.element = dom("div", {"class": "attachment-list"});

        $(input).after(this.element);        

        
        this.uploader = new ImageUploader(function(filename, responseJSON){
            var widget = that.addCroppedImage(
                filename,
                responseJSON.path,
                [0, 0, $(that.popup).data("thumb-height"), $(that.popup).data("thumb-width")]
            );

            widget.edit();
        });

        this.loadImages();
    }

    CroppedImages.prototype = {        
        addCroppedImage: function(filename, filepath, cropping){
            var widget = new CroppingImageWidget(filename, filepath, cropping, this);
            this.images.push(widget);
            $(this.element).append(widget.element);

            this.saveValue();

            return widget;
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
                images = value.split(";");

                images.forEach(function(cropped_image){
                    var data = cropped_image.split("!"),
                        image = data[0],
                        cropping = _.map(data[1].split(","), function(val){
                            return parseInt(val);
                        });

                    this.addCroppedImage(image.replace(/^.*(\\|\/|\:)/, ''), image, cropping);
                }, this);
            }
        },
        saveValue: function(){
            var value = this.images.map(function(imageWidget){
                return imageWidget.getValue();
            }).join(";");

            $(this.input).val(value);
        }
    }

    $(document).on("ready page:load", function(){
        new CroppedImages(
            document.getElementById("id_images")
        );
    });

})(jQuery, window, document);
    