from __future__ import unicode_literals

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed, Rss201rev2Feed, rfc2822_date
from django.utils.html import strip_tags

from mezzanine.core.templatetags.mezzanine_tags import richtext_filters
from mezzanine_agenda.models import Event, EventLocation
from mezzanine.generic.models import Keyword
from mezzanine.pages.models import Page
from mezzanine.conf import settings
from mezzanine.utils.models import get_user_model


User = get_user_model()

class ExtendedRSSFeed(Rss201rev2Feed):
    """
    Create a type of RSS feed that has content:encoded elements.
    """
    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        # Because I'm adding a <content:encoded> field, I first need to declare
        # the content namespace. For more information on how this works, check
        # out: http://validator.w3.org/feed/docs/howto/declare_namespaces.html
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
    
        # 'content_encoded' is added to the item below, in item_extra_kwargs()
        # It's populated in item_your_custom_field(). Here we're creating
        # the <content:encoded> element and adding it to our feed xml
        if item['start_date'] is not None:
            #handler.addQuickElement(u'start_date', item['start_date'])
            handler.addQuickElement(u'start_date', rfc2822_date(item['start_date']))


class EventsRSSExt(Feed):
    """
    RSS feed for all events, extended with start_date field added
    """

    feed_type = ExtendedRSSFeed

    def __init__(self, *args, **kwargs):
        """
        Use the title and description of the Events page for the feed's
        title and description. If the events page has somehow been
        removed, fall back to the ``SITE_TITLE`` and ``SITE_TAGLINE``
        settings.
        """
        self.tag = kwargs.pop("tag", None)
        self.location = kwargs.pop("location", None)
        self.username = kwargs.pop("username", None)
        super(EventsRSSExt, self).__init__(*args, **kwargs)
        self._public = True
        try:
            page = Page.objects.published().get(slug=settings.EVENT_SLUG)
        except Page.DoesNotExist:
            page = None
        else:
            self._public = not page.login_required
        if self._public:
            settings.use_editable()
            if page is not None:
                self._title = "%s | %s" % (page.title, settings.SITE_TITLE)
                self._description = strip_tags(page.description)
            else:
                self._title = settings.SITE_TITLE
                self._description = settings.SITE_TAGLINE

    def title(self):
        return self._title

    def description(self):
        return self._description

    def link(self):
        return reverse("event_list")

    def items(self):
        if not self._public:
            return []
        events = Event.objects.published().select_related("user")
        if self.tag:
            tag = get_object_or_404(Keyword, slug=self.tag)
            events = events.filter(keywords__keyword=tag)
        if self.location:
            location = get_object_or_404(EventLocation, slug=self.location)
            events = events.filter(location=location)
        if self.username:
            author = get_object_or_404(User, username=self.username)
            events = events.filter(user=author)
        limit = settings.EVENT_RSS_LIMIT
        if limit is not None:
            events = events[:settings.EVENT_RSS_LIMIT]
        return events

    def item_description(self, item):
        return richtext_filters(item.content)

    def locations(self):
        if not self._public:
            return []
        return EventLocations.objects.all()

    def item_author_name(self, item):
        return item.user.get_full_name() or item.user.username

    def item_author_link(self, item):
        username = item.user.username
        return reverse("event_list_author", kwargs={"username": username})

    def item_pubdate(self, item):
        return item.publish_date

    def item_location(self, item):
        return item.location

    def item_extra_kwargs(self, item):
        # This is probably the first place you'll add a reference to the new
        # content. Start by superclassing the method, then append your
        # extra field and call the method you'll use to populate it.
        extra = super(EventsRSSExt, self).item_extra_kwargs(item)
        extra.update({'start_date': self.item_startdate(item)})
        return extra
    
    def item_startdate(self, item):
        # This is your custom method for populating the field.
        # Name it whatever you want, so long as it matches what
        # you're calling from item_extra_kwargs().
        # What you do here is entirely dependent on what your
        # system looks like. I'm using a simple queryset example,
        # but this is not to be taken literally.
        #obj_id = 1 #item['my_item_id']
        #query_obj = MyStoryModel.objects.get(pk=obj_id)
        #print "start date is ",item.start
        #full_text = "here's some text" #query_obj['full_story_content']
        #return full_text
        return item.start


class EventsRSS(Feed):
    """
    RSS feed for all events.
    """

    def __init__(self, *args, **kwargs):
        """
        Use the title and description of the Events page for the feed's
        title and description. If the events page has somehow been
        removed, fall back to the ``SITE_TITLE`` and ``SITE_TAGLINE``
        settings.
        """
        self.tag = kwargs.pop("tag", None)
        self.location = kwargs.pop("location", None)
        self.username = kwargs.pop("username", None)
        super(EventsRSS, self).__init__(*args, **kwargs)
        self._public = True
        try:
            page = Page.objects.published().get(slug=settings.EVENT_SLUG)
        except Page.DoesNotExist:
            page = None
        else:
            self._public = not page.login_required
        if self._public:
            settings.use_editable()
            if page is not None:
                self._title = "%s | %s" % (page.title, settings.SITE_TITLE)
                self._description = strip_tags(page.description)
            else:
                self._title = settings.SITE_TITLE
                self._description = settings.SITE_TAGLINE

    def get_context_data(self, **kwargs):
        context = super(EventsRSS, self).get_context_data(**kwargs)
        context['start'] = "START VALUE"
        return context 

    def title(self):
        return self._title

    def description(self):
        return self._description

    def link(self):
        return reverse("event_list")

    def items(self):
        if not self._public:
            return []
        events = Event.objects.published().select_related("user")
        if self.tag:
            tag = get_object_or_404(Keyword, slug=self.tag)
            events = events.filter(keywords__keyword=tag)
        if self.location:
            location = get_object_or_404(EventLocation, slug=self.location)
            events = events.filter(location=location)
        if self.username:
            author = get_object_or_404(User, username=self.username)
            events = events.filter(user=author)
        limit = settings.EVENT_RSS_LIMIT
        if limit is not None:
            events = events[:settings.EVENT_RSS_LIMIT]
        return events

    def item_description(self, item):
        return richtext_filters(item.content)

    def locations(self):
        if not self._public:
            return []
        return EventLocations.objects.all()

    def item_author_name(self, item):
        return item.user.get_full_name() or item.user.username

    def item_author_link(self, item):
        username = item.user.username
        return reverse("event_list_author", kwargs={"username": username})

    def item_pubdate(self, item):
        return item.publish_date

    def item_location(self, item):
        return item.location


class EventsAtom(EventsRSSExt):
    """
    Atom feed for all events.
    """

    feed_type = Atom1Feed

    def subtitle(self):
        return self.description()
