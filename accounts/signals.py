# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# from django.contrib.auth import get_user_model
#
# from accounts.models import User, Student
#
#
# @receiver(post_save, sender=User, dispatch_uid='user.create_user_profile')
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Student.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User, dispatch_uid='user.save_user_profile')
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
