from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return global categories (user is null) and user's custom categories
        return Category.objects.filter(Q(user__isnull=True) | Q(user=self.request.user))

    def perform_create(self, serializer):
        # Automatically assign the logged-in user to the new category
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        # Prevent users from deleting global/system categories
        instance = self.get_object()
        if instance.user is None:
            return Response(
                {"detail": "Cannot delete global categories."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
