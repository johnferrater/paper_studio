from .models import Notification


def notify(recipient, message, url=""):
    """Create a notification for a user. No-op when there is no recipient."""
    if recipient is None:
        return None
    return Notification.objects.create(recipient=recipient, message=message, url=url)
