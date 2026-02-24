from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Accounts, UserProfile


@receiver(post_save, sender=Accounts)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Accounts)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()