;(function($, window, document, undefined) {
    'use strict';

    function AttachmentWidget(filename, filepath, attachmentsWidget){
        var that = this;
        this.attachmentsWidget = attachmentsWidget;
        this.filepath = filepath;

        this.element = dom("div", {"class": "attachment"}, [
            dom("span", {"innerHTML": filename}),
            this.removeButton = dom("div", {"class": "remove-attachment-button"})
        ]);

        $(this.removeButton).on("click", function(){
            that.remove();
        });
    }

    AttachmentWidget.prototype = {
        remove: function(){
            this.attachmentsWidget.removeAttachment(this);
        }
    }

    function Attachments(input){
        var that= this;
        this.input = input;
        this.attachments = [];
        this.element = dom("div", {"class": "attachment-list"});

        $(input).after(this.element);

        this.uploader = new qq.FileUploader({
            action: "/events/ajax-upload",
            element: document.getElementById("attachments-uploader"),
            multiple: true,
            allowedExtensions: ['pdf', 'jpg', 'jpeg', 'png', 'gif'],
            sizeLimit: 33554432,
            onComplete: function(id, fileName, responseJSON) {
                if(responseJSON.success) {
                    that.addAttachment(fileName, responseJSON.path);
                } else {
                    if(console.log) console.log("upload failed!");
                    alert("Something go wrong on server. Please contact administrator.");
                }
            },
            onSubmit: function(id, fileName) {
                
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
            attachments = value.split(";");
        },
        saveValue: function(){
            var value = return this.attachments.map(function(attachment){
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