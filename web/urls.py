from django.urls import path

from .views.home import HomeView, EventView, StatsView

# from api.propertycontent.views import PropertyContentView

urlpatterns = [
    # Visitor Website
    path("", view=HomeView.as_view('login'), name="visitor_login"),
    path("register", view=HomeView.as_view('register'), name="visitor_register"),
    path("dashboard", view=HomeView.as_view('dashboard'), name="visitor-home"),
    path("user", view=HomeView.as_view('user'), name="visitor-user"),
    path("event", view=EventView.as_view('index'), name="visitor-event"),
    path("event-detail/<int:pk>", view=EventView.as_view('detail'), name="visitor-event-detail"),
    path("statistics", view=StatsView.as_view('index'), name="visitor-stats"),

    path('set-auth-cookie/', HomeView.as_view('auth_cookie'), name="set-auth-cookie"),
    path('set-auth-cookie/<str:access_tokenFsirm>', HomeView.as_view('auth_cookie'), name="set-auth-cookie"),

]
