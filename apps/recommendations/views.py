from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    RecommendationSerializer,
    CollaborativeSerializer
)
from .services.content_based import get_recommendations_content
from .services.collaborative import get_recommendations_collab


class RecommendationAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        recommendations = get_recommendations_content(request.user, limit=50)
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(recommendations, request, view=self)

        if page is not None:
            serializer = RecommendationSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    

class CollaborativeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        recommendations = get_recommendations_collab(request.user, limit=50)
        
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(recommendations, request, view=self)

        if page is not None:
            serializer = CollaborativeSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CollaborativeSerializer(recommendations, many=True)
        return Response(serializer.data)