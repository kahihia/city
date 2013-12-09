;(function($, window, document, undefined) {
    'use strict';

    var SocialLink = function(socialLinks, title, url){
        this.socialLinks = socialLinks;
        this.title = title || "";
        this.url = url || "";
        this.render();
    }

    SocialLink.prototype = {
        render: function(){
            this.widget = dom("div", { "class": "social-link" }, [
                this.linkTitle = dom("input", { placeholder: "Title", "class": "social-link-title", "type": "text" }),
                this.linkUrl = dom("input", { placeholder: "Url", "class": "social-link-url", "type": "text" }),
                this.removeButton = dom("i", { "class": "icon-remove" })
            ]);

            $(this.linkTitle).val(this.title);
            $(this.linkUrl).val(this.url);

            $(this.removeButton).on("click", this.destroy.bind(this))
        },
        destroy: function(){
            this.socialLinks.removeSocialLink(this);
            $(this.widget).remove();
        },
        getValue: function() {
            return {
                title: $(this.linkTitle).val(),
                url: $(this.linkUrl).val()
            }
        }
    }

    var SocialLinks = function(){
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
        },
        removeSocialLink: function(link){
            this.links.splice(this.links.indexOf(link), 1);
            this.saveValue();
        },
        loadLinks: function(){
            var that=this, value, links;

            value = $(this.input).val();
            if(value) {
                links = JSON.parse(value).links;

                links.forEach(function(link){                    
                    this.addSocialLink(that, link.title, link.url);
                }, this);
            }
        },
        saveValue: function(){
            var links = this.links.map(function(linkWidget){
                return linkWidget.getValue();
            });

            $(this.input).val(JSON.stringify({
                links: links
            }));
        }
    }

    window.SocialLinks = SocialLinks;

})(jQuery, window, document);