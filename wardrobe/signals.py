from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Customer, Store

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

        default_store = Store.objects.first()
        if default_store:
            Customer.objects.get_or_create(
                user=instance,
                store=default_store,
                defaults={
                    'first_name': instance.first_name or instance.username,
                    'last_name': instance.last_name or '',
                    'email': instance.email or '',
                }
            )
