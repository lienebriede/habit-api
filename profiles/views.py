from rest_framework import generics
from habit_api.permissions import IsAuthenticatedAndOwnerOrReadOnly
from .models import Profile
from .serializers import ProfileSerializer


class ProfileList(generics.ListAPIView):
    """
    List all profiles.
    This view should not be exposed for now as profiles are private.
    No create view as profile creation is handled by django signals.
    """
    queryset = Profile.objects.none()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]


class ProfileDetail(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a profile if you're the owner.
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticatedAndOwnerOrReadOnly]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)