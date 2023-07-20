# Create your views here.
from django.urls import path

# app_name will help us do a reverse look-up latter.
from api.event.views import EventAPIView, EventDeleteAPIView, EventJoinAPIView, EventStatisticsAPIView, \
    EventRatingAPIView, EventSendInvitationAPIView

urlpatterns = [

    path("", EventAPIView.as_view(), name="event"),
    path("<int:pk>", EventAPIView.as_view(), name="event"),

    path("delete", EventDeleteAPIView.as_view(), name="event_delete"),
    path("delete/<int:pk>", EventDeleteAPIView.as_view(), name="event_delete"),

    path("join_event", EventJoinAPIView.as_view(), name="event_join"),
    path("<int:event_id>/join_event/<int:user_id>", EventJoinAPIView.as_view(), name="event_join"),

    path("rate-event", EventRatingAPIView.as_view(), name="event_rate"),
    path("<int:event_id>/rate-event/<int:rating>", EventRatingAPIView.as_view(), name="event_rate"),

    path("send-invitation", EventSendInvitationAPIView.as_view(), name="event_invitation"),

    path("statistics", EventStatisticsAPIView.as_view(), name="event_stats"),

]
