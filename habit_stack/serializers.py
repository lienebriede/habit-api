from rest_framework import serializers
from .models import HabitStacking

class HabitStackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitStacking
        fields = ['id', 'user', 'habit1', 'habit2', 'goal', 'created_at']

    def validate(self, data):
        if HabitStacking.objects.filter(user=data['user'], habit1=data['habit1'], habit2=data['habit2'], goal=data['goal']).exists():
            raise serializers.ValidationError('This habit stack already exists for the user.')
        return data