from django.contrib import admin
from reviews.models import Review, ReviewLike, ReviewComment


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    ...

@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    ...

@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    ...
