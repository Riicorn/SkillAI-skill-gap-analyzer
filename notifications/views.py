from django.http import JsonResponse
from .models import Notification
from django.utils.timesince import timesince


def get_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({"notifications": []})

    notifs = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    data = [
    {
        "title": n.title,
        "message": n.message,
        "type": n.type,
        "time": timesince(n.created_at) + " ago"
    }
    for n in notifs
]

    return JsonResponse({"notifications": data})

from django.shortcuts import render
from .models import Notification

def notifications_page(request):
    notifs = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'notifications/notifications.html', {
        'notifications': notifs
    })