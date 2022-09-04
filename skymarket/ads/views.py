from django.shortcuts import get_object_or_404
from rest_framework import pagination, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.decorators import action

from ads.models import Ad, Comment
from ads.permissions import IsOwner, IsAdmin
from ads.serializers import AdSerializer, AdDetailSerializer, CommentSerializer


class AdPagination(pagination.PageNumberPagination):
    page_size = 4


class AdMeModelView(viewsets.ModelViewSet):
    pagination_class = AdPagination
    permission_classes = [IsOwner]
    serializer_class = AdSerializer

    def get_queryset(self):
        return Ad.objects.filter(author__exact=self.request.user)


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    pagination_class = AdPagination
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user)

    def get_serializer_class(self):
        if self.action in ["retrieve", "create", "update", "partial_update", "destroy"]:
            return AdDetailSerializer
        return AdSerializer

    def get_permissions(self):
        permission_classes = [AllowAny]
        if self.action in ["retrieve"]:
            permission_classes = [AllowAny]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsOwner | IsAdmin]
        return [permission() for permission in permission_classes]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        ad_id = self.kwargs.get("ad_pk")
        ad_info = get_object_or_404(Ad, id=ad_id)
        user = self.request.user
        serializer.save(author=user, ad=ad_info)

    def get_queryset(self):
        ad_id = self.kwargs.get("ad_pk")
        ad_info = get_object_or_404(Ad, id=ad_id)
        return ad_info.comments.all()

    def get_permissions(self):
        permission_classes = [IsAuthenticated]

        if self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsOwner | IsAdmin]
        return [permission() for permission in permission_classes]
