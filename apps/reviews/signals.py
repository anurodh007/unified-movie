from django.db.models import Avg, Count
from django.db.models.functions import Coalesce
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reviews.models import Review
from movies.models import Movie


"""
Function to update movie stats with one database round-trip
"""
def update_movie_stats(movie_id):
    if not movie_id:
        return
    
    stats = Review.objects.filter(movie_id=movie_id).aggregate(
        new_count=Count('id'),
        new_avg=Coalesce(Avg('rating'), 0.0)
    )
    
    Movie.objects.filter(id=movie_id).update(
        vote_count=stats['new_count'],
        average_rating=stats['new_avg']
    )


"""
Signal fired on review create, update, delete
"""
@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def on_review_save(sender, instance, **kwargs):
    update_movie_stats(instance.movie_id)