;(function($, window, document, undefined) {
    'use strict';

    function AttachmentUploader(callback){
        var that = this;
        this.uploader = new qq.FileUploader({
            action: "/events/ajax-upload",
            multiple: false,
            element: document.getElementById("attachments-uploader"),
            allowedExtensions: ['jpg', 'jpeg', 'png', 'gif', 'pdf'],
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
                '<div class="qq-upload-indicator-block attachment-upload-progress-bar inv" data-id="upload_indicator_block">' +
                    '<img src="/static/images/mini-ajax-loader.gif" alt="" />' +
                    '<a class="qq-uploading-cancel image-upload-cancel" data-id="uploading_cancel" href="javascript:void(0);">' +
                        'Cancel' +
                    '</a>' +
                '</div>' +
                '<ul class="qq-upload-list"></ul>' +
             '</div>'
        });

        $("#attachments-uploader .attachment-upload-cancel").on("click", this.cancelUpload.bind(this))
    }

    AttachmentUploader.prototype = {
        showProgressBar: function(){
            $(".attachment-upload-progress-bar").removeClass("inv");
        },
        hideProgressBar: function(){
            $(".attachment-upload-progress-bar").addClass("inv");
        },
        cancelUpload: function(){
            var fileId = $("#attachments-uploader .attachment-upload-cancel").data("file-id");
            this.uploader._handler.cancel(fileId);
            this.hideProgressBar();

        }
    }

    function AttachmentWidget(filename, filepath, attachmentsWidget){
        var that = this;
        this.attachmentsWidget = attachmentsWidget;
        this.filename = filename;
        this.filepath = filepath;

        this.element = dom("div", {"class": "attachment"}, [
            dom("span", {"innerHTML": filename}),
            this.removeButton = dom("i", {"class": "icon-remove"}),
            this.previewButton = dom("i", {"class": "icon-eye-open"})
        ]);

        $(this.removeButton).on("click", function(){
            that.remove();
        });

        $(this.previewButton).on("click", function(){
            that.preview();
        });

        if(!/\.(gif|jpg|jpeg|tiff|png)$/i.test(this.filename)){
            $(this.previewButton).hide();                
        }
    }

    AttachmentWidget.prototype = {
        remove: function(){
            this.attachmentsWidget.removeAttachment(this);
        },
        preview: function(){
            $.fancybox(this.filepath, {
                autoSize: true,
                closeBtn: true,
                hideOnOverlayClick: false
            });
        }
    }

    function Attachments(input){
        var that= this;
        this.input = input;
        this.attachments = [];
        this.element = dom("div", {"class": "attachment-list"});

        $(input).after(this.element);

        this.uploader = new AttachmentUploader(function(filename, responseJSON){
            that.addAttachment(filename, responseJSON.path);
        });

        this.loadAttachments();
    }

    Attachments.prototype = {
        addAttachment: function(filename, attachmentPath){
            var attachment = new AttachmentWidget(filename, attachmentPath, this);
            this.attachments.push(attachment);
            $(this.element).append(attachment.element);

            this.saveValue();
        },
        removeAttachment: function(attachment){
            this.attachments.splice(this.attachments.indexOf(attachment), 1);
            $(attachment.element).remove();

            this.saveValue();
        },
        loadAttachments: function(){
            var value, attachments;

            value = $(this.input).val();
            if(value) {
                attachments = value.split(";");

                attachments.forEach(function(attachment){
                    this.addAttachment(attachment.replace(/^.*(\\|\/|\:)/, ''), attachment);
                }, this);
            }
        },
        saveValue: function(){
            var value = this.attachments.map(function(attachment){
                return attachment.filepath;
            }).join(";");

            $(this.input).val(value);
        }
    }
    
    $(document).on("ready page:load", function(){
        new Attachments(
            document.getElementById("id_attachments")
        );
    });

})(jQuery, window, document);