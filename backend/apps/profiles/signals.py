from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.authentication.models import User
from .models import UserSkill, Experience
from .ai_utils import update_user_embedding

@receiver(post_save, sender=User)
def user_saved(sender, instance, created, **kwargs):
    # If the user is just created, the bio/skills might be empty, 
    # but we still generate a base embedding.
    update_user_embedding(instance)

@receiver(post_save, sender=UserSkill)
@receiver(post_delete, sender=UserSkill)
def user_skill_changed(sender, instance, **kwargs):
    update_user_embedding(instance.user)

@receiver(post_save, sender=Experience)
@receiver(post_delete, sender=Experience)
def experience_changed(sender, instance, **kwargs):
    update_user_embedding(instance.user)
