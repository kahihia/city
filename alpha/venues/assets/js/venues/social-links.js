;(function($, window, document, undefined) {
    'use strict';

    function TitleWidget(socialLink, title){
        this.socialLink = socialLink;
        this.render();
        this.applyLogic(title);
        title && this.setValue(title);
    }

    TitleWidget.prototype = {
        render: function(){
            this.widget = dom("div", { "class": "social-link-title-widget" },[
                this.viewMode = dom("div", { "class": "view-mode" }, [
                    this.titleText = dom("span"),
                    this.editButton = dom("i", { "class": "icon-edit" })
                ]),
                this.editMode = dom("div", { "class": "edit-mode" }, [
                    this.titleInput = dom("input", { "type": "text", placeholder: "Title" }),
                    this.saveButton = dom("i", { "class": "icon-save" })
                ])
            ]);
        },
        applyLogic: function(title){
            var that = this;
            this.switchMode(title?"view":"edit");
            $(this.editButton).on("click", function(){
                that.switchMode("edit");
            });

            $(this.titleText).on("click", function(){
                that.switchMode("edit");
            });

            $(this.titleInput).on("focusout", function(){
                that.saveValue();
            });

            $(this.saveButton).on("click", function(){
                that.saveValue();
            });
        },
        setValue: function(title){
            $(this.titleText).html(title);
            $(this.titleInput).val(title);
        },
        getValue: function(){
            return $(this.titleInput).val();
        },
        switchMode: function(mode){
            $(this.widget).removeClass("view");
            $(this.widget).removeClass("edit");
            $(this.widget).addClass(mode);
        },
        saveValue: function(){
            $(this.titleText).html($(this.titleInput).val());
            this.switchMode("view");
            this.socialLink.saveSocialLinks();
        }
    }

    function SocialLink(socialLinks, title, url){
        this.socialLinks = socialLinks;
        this.title = title || "";
        this.url = url || "";
        this.render();
    }

    SocialLink.prototype = {
        render: function(){
            this.titleWidget = new TitleWidget(this, this.title);
            this.widget = dom("div", { "class": "social-link" }, [
                this.linkTitle = this.titleWidget.widget,
                this.linkUrl = dom("input", { placeholder: "Url", "class": "social-link-url", "type": "text" }),
                this.removeButton = dom("i", { "class": "icon-remove" })
            ]);

            $(this.linkUrl).val(this.url);

            $(this.removeButton).on("click", this.destroy.bind(this));
            $(this.linkTitle).on("keyup", this.saveSocialLinks.bind(this));
            $(this.linkUrl).on("keyup", this.saveSocialLinks.bind(this));
        },
        destroy: function(){
            this.socialLinks.removeSocialLink(this);
            $(this.widget).remove();
        },
        getValue: function() {
            return {
                title: this.titleWidget.getValue(),
                url: $(this.linkUrl).val()
            }
        },
        saveSocialLinks: function(){
            this.socialLinks.saveValue();
        }
    }

    function SocialLinks(){
        var that = this;
        this.input = $("#id_social_links");
        this.links = [];
        this.addMoreButton = $(".add-more-social-link");
        this.linksContainer = $(".social-links-container");

        $(this.addMoreButton).on("click", function(){
            that.addSocialLink();
        });

        this.loadLinks();
    }

    SocialLinks.prototype = {
        addSocialLink: function(title, url){
            var newSocialLink = new SocialLink(this, title, url);
            this.links.push(newSocialLink);
            this.linksContainer.append(newSocialLink.widget);
            this.saveValue();
        },
        removeSocialLink: function(link){
            this.links.splice(this.links.indexOf(link), 1);
            this.saveValue();
        },
        loadLinks: function(){
            var value, links;

            value = $(this.input).val();
            if(value) {
                links = JSON.parse(value).social_links;

                links.forEach(function(link){                    
                    this.addSocialLink(link.title, link.url);
                }, this);
            }
        },
        saveValue: function(){
            var links = this.links.map(function(linkWidget){
                return linkWidget.getValue();
            });

            $(this.input).val(JSON.stringify({
                social_links: links
            }));
        }
    }

    window.SocialLinks = SocialLinks;

})(jQuery, window, document);