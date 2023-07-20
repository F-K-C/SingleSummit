import datetime
import json
from dateutil import parser
import urllib

from django.db.models import Count
from django.shortcuts import redirect

from api.event.models import Event, EventParticipant
from api.event.serializers import EventSerializer
from api.users.models import AccessLevel, User
from web.base_view import BaseView


class HomeView(BaseView):

    def login(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("/dashboard")
        return self.render('visitor/login.html')

    def register(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("/dashboard")
        return self.render('visitor/register.html')

    def dashboard(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect("/")
        self.users = User.objects.filter(role__code=AccessLevel.CLIENT_CODE).count()
        if self.request.user.role.code == AccessLevel.SUPER_ADMIN_CODE:
            self.events = Event.objects.filter().count()
        else:
            self.events = Event.objects.filter(user_id=self.request.user.id).count()
        return self.render('visitor/dashboard.html')

    def user(self, *args, **kwargs):
        if not self.request.user.is_authenticated and self.request.user.role.code == AccessLevel.SUPER_ADMIN_CODE:
            return redirect("/")
        return self.render('visitor/user.html')


class EventView(BaseView):

    def index(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect("/")
        return self.render('visitor/event.html')

    def detail(self, *args, **kwargs):
        # if not self.request.user.is_authenticated:
        #     return redirect("/")
        event_instance = Event.objects.get(id=kwargs.get("pk"))
        self.event = EventSerializer(event_instance, context={
                    "user_id": self.request.user.id
                }).data
        self.encoded_event_data = urllib.parse.quote(json.dumps(self.event))
        self.show_btn = True if parser.parse(str(event_instance.date)) > datetime.datetime.now(datetime.timezone.utc) else False
        self.participants = EventParticipant.objects.filter(
            event_id=event_instance.id
        ).values("user__first_name", "user__last_name", "grade")
        return self.render('visitor/event-detail.html')


class StatsView(BaseView):

    def index(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect("/")

        self.cities = ([d[0] for d in Event.objects.filter().values_list('city')])
        self.types = (d[0] for d in Event.objects.filter().values_list('type'))
        return self.render('visitor/statistics.html')