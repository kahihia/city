from django import template
import settings
register = template.Library()


class ShowGoogleAnalyticsJS(template.Node):
    def render(self, context):
        code =  getattr(settings, "GOOGLE_ANALYTICS_CODE", False)
        if not code:
            return "<!-- Goggle Analytics not included because you haven't set the settings.GOOGLE_ANALYTICS_CODE variable! -->"

        # TODO: uncoment in production
        # if 'user' in context and context['user'] and context['user'].is_staff:
        #   return "<!-- Goggle Analytics not included because you are a staff user! -->"

        # if settings.DEBUG:
        #     return "<!-- Goggle Analytics not included because you are in Debug mode! -->"

        return """
        <script type="text/javascript" data-turbolinks-eval=false>
            var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
            document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'  data-turbolinks-eval=false %3E%3C/script%3E"));
        </script>
        <script type="text/javascript" data-turbolinks-eval=false>
            try {
            var pageTracker = _gat._getTracker('""" + str(code) + """');
            pageTracker._trackPageview();
        } catch(err) {}</script>
        """

@register.tag
def googleanalyticsjs(parser, token):
    return ShowGoogleAnalyticsJS()

class ShowGoogleAnalyticsJSPush(template.Node):
    def render(self, context):
        code =  getattr(settings, "GOOGLE_ANALYTICS_CODE", False)
        if not code:
            return "<!-- Goggle Analytics not included because you haven't set the settings.GOOGLE_ANALYTICS_CODE variable! -->"

        # TODO: uncoment in production
        # if 'user' in context and context['user'] and context['user'].is_staff:
        #   return "<!-- Goggle Analytics not included because you are a staff user! -->"

        # if settings.DEBUG:
        #     return "<!-- Goggle Analytics not included because you are in Debug mode! -->"

        return """
        <script>_gaq && _gaq.push(['_trackPageview']);</script>
        """

@register.tag
def googleanalyticsjs_push(parser, token):
    return ShowGoogleAnalyticsJSPush()        
