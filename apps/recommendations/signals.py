from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from reviews.models import Review


@receiver([post_save, post_delete], sender=Review)
def on_review_modify(sender, instance, **kwargs):
    user = instance.user

    key0 = f'user_vector_{user.id}'
    key1 = f'similarity_scores_{user.id}'
    key2 = 'user_movie_matrix'
    key3 = f'user_similarity_{user.id}'
    key4 = f'predicted_ratings_{user.id}'

    cache.delete_many([key0, key1, key2, key3, key4])