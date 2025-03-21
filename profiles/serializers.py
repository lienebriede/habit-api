from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    is_owner = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.user

    class Meta:
        model = Profile
        fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
            'name',
            'is_owner',
            'image'
        ]
