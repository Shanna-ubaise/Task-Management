from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Task, Profile
from .serializers import TaskSerializer, TaskUpdateSerializer, UserSerializer
from .permissions import IsSuperAdmin

class TaskViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        user = self.request.user
        profile = Profile.objects.get(user=user)
        if profile.role == "superadmin":
            return Task.objects.all()  
        elif profile.role == "admin":
            return Task.objects.filter(created_by=user)  
        else:
            return Task.objects.filter(assigned_to=user) 

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)  


    def get_object(self):
        task = super().get_object()
        user = self.request.user
        profile = Profile.objects.get(user=user)

        if profile.role == "superadmin":
            return task
        elif profile.role == "admin" and task.created_by == user:
            return task
        elif task.assigned_to != user:
            raise PermissionDenied("You cannot access this task")
        return task

    @action(detail=True, methods=["get"], url_path="report")
    def report(self, request, pk=None):
        task = self.get_object()
        if task.status != "Completed":
            return Response({"error": "Task is not completed yet"}, status=400)
        return Response({
            "title": task.title,
            "assigned_to": task.assigned_to.username,
            "completion_report": task.completion_report,
            "worked_hours": task.worked_hours,
        })

    @action(detail=False, methods=["get"], url_path="completed-reports")
    def completed_reports(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)

        if profile.role != "superadmin":
            return Response({"error": "Only superadmin can access all reports"}, status=403)

        tasks = Task.objects.filter(status="Completed")
        data = [
            {
                "id": t.id,
                "title": t.title,
                "assigned_to": t.assigned_to.username,
                "completion_report": t.completion_report,
                "worked_hours": t.worked_hours,
            }
            for t in tasks
        ]
        return Response(data)
    
class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSuperAdmin]


def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "tasks/login.html", {"error": "Invalid credentials"})
    return render(request, "tasks/login.html")

@login_required
def dashboard(request):
    role = request.user.profile.role
    if role == "superadmin":
        return redirect("superadmin-dashboard")
    elif role == "admin":
        return redirect("admin-dashboard")
    else:
        return redirect("user-dashboard")

@login_required
def user_dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, "tasks/user_dashboard.html", {"tasks": tasks})


@login_required
def admin_dashboard(request):
    admin_user = request.user
    tasks = Task.objects.filter(created_by=admin_user)
    return render(request, "tasks/admin_dashboard.html", {"tasks": tasks})


@login_required
def superadmin_dashboard(request):
    tasks = Task.objects.all()
    users = Profile.objects.all()
    return render(request, "tasks/superadmin_dashboard.html", {"tasks": tasks, "users": users})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    if request.method == "POST":
        report = request.POST.get("completion_report")
        hours = request.POST.get("worked_hours")
        task.completion_report = report
        task.worked_hours = hours
        task.status = "Completed"
        task.save()
        return HttpResponseRedirect(reverse('user-dashboard'))
