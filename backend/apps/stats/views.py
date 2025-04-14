from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .logic import (
    get_comments_by_classification_counts,
    get_comment_statistics_with_percentages,
    get_classification_timeline
)

class StatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        comments_by_classification = get_comments_by_classification_counts()
        statistics = get_comment_statistics_with_percentages()
        classification_timeline = get_classification_timeline()

        return Response({
            'comments_by_classification': comments_by_classification,
            'statistics': statistics,
            'classification_timeline': classification_timeline
        })
