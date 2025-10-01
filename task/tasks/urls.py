from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    TaskViewSet, UserCreateView,
    custom_login, dashboard,
    user_dashboard, admin_dashboard, superadmin_dashboard,
    complete_task,
)
from django.contrib.auth.views import LogoutView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('login/', custom_login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/user/', user_dashboard, name='user-dashboard'),
    path('dashboard/admin/', admin_dashboard, name='admin-dashboard'),
    path('dashboard/superadmin/', superadmin_dashboard, name='superadmin-dashboard'),
    path('task/<int:task_id>/complete/', complete_task, name='task-complete'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

]

