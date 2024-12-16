from rest_framework import serializers
from .models import HabitStacking, PredefinedHabit, HabitStackingLog, StreakAndMilestoneTracker

class HabitStackingSerializer(serializers.ModelSerializer):
    """
    Serializer for the HabitStacking model.
    Handles validation and ensures that users can only define unique habits
    """
    user = serializers.ReadOnlyField(source='user.username')
    predefined_habit1 = serializers.PrimaryKeyRelatedField(
        queryset=PredefinedHabit.objects.all(),
        required=False,
        allow_null=True
    )
    predefined_habit2 = serializers.PrimaryKeyRelatedField(
        queryset=PredefinedHabit.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = HabitStacking
        fields = ['id', 'user', 'predefined_habit1', 'custom_habit1', 'predefined_habit2', 'custom_habit2', 'goal', 'created_at']

    def validate(self, data):
        """
        Custom validation logic for the HabitStacking model.
        """
        user = self.context['request'].user
        predefined_habit1 = data.get('predefined_habit1')
        custom_habit1 = data.get('custom_habit1')
        predefined_habit2 = data.get('predefined_habit2')
        custom_habit2 = data.get('custom_habit2')
        goal = data.get('goal')

        # Validation for habit1 and habit2
        if predefined_habit1 and custom_habit1:
            raise serializers.ValidationError("You can only choose either a predefined habit or a custom habit for Habit 1, not both.")
        if predefined_habit2 and custom_habit2:
            raise serializers.ValidationError("You can only choose either a predefined habit or a custom habit for Habit 2, not both.")
        if not (predefined_habit1 or custom_habit1):
            raise serializers.ValidationError("You must provide either a predefined habit or a custom habit for Habit 1.")
        if not (predefined_habit2 or custom_habit2):
            raise serializers.ValidationError("You must provide either a predefined habit or a custom habit for Habit 2.")

        # Ensure habit1 and habit2 are not the same
        if (predefined_habit1 and predefined_habit2 and predefined_habit1 == predefined_habit2) or \
           (custom_habit1 and custom_habit2 and custom_habit1 == custom_habit2) or \
           (predefined_habit1 and custom_habit2 and predefined_habit1.name == custom_habit2) or \
           (predefined_habit2 and custom_habit1 and predefined_habit2.name == custom_habit1):
            raise serializers.ValidationError("Habit1 and Habit2 cannot be the same.")

        # Ensure that either predefined habit or custom habit is provided, but not both empty
        if not ((predefined_habit1 or custom_habit1) and (predefined_habit2 or custom_habit2)):
            raise serializers.ValidationError("Both habit fields cannot be empty. Provide either predefined or custom habits.")

        # Get the current instance if updating
        instance = getattr(self, 'instance', None)

        # Ensure no duplicate habit stacks for the same user, but allow for different goals
        if instance:
            existing_habit_stacks = HabitStacking.objects.filter(
                user=user,
                predefined_habit1=predefined_habit1,
                custom_habit1=custom_habit1,
                predefined_habit2=predefined_habit2,
                custom_habit2=custom_habit2
            ).exclude(id=instance.id)
        else:
            existing_habit_stacks = HabitStacking.objects.filter(
                user=user,
                predefined_habit1=predefined_habit1,
                custom_habit1=custom_habit1,
                predefined_habit2=predefined_habit2,
                custom_habit2=custom_habit2
            )

        if existing_habit_stacks.exists():
            raise serializers.ValidationError("A habit stack with these details already exists.")

        # Validate goal value
        if goal not in ['DAILY', 'NO_GOAL']:
            raise serializers.ValidationError("Invalid goal value.")

        return data

class HabitStackingLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the HabitStackingLog model.
    Provides additional fields for streak and milestone messages.
    """
    user = serializers.ReadOnlyField(source='user.username')
    habit_stack = HabitStackingSerializer()
    streak_message = serializers.SerializerMethodField()
    milestone_message = serializers.SerializerMethodField()

    class Meta:
        model = HabitStackingLog
        fields = ['id', 'habit_stack', 'user', 'date', 'completed', 'streak_message', 'milestone_message']

    def get_streak_message(self, obj):
        """
        Returns a message if the user is on a streak of at least 2 days.
        """
        tracker = StreakAndMilestoneTracker.objects.filter(user=obj.user, habit_stack=obj.habit_stack).first()
        if tracker and tracker.current_streak >= 2:
            return f"You're on a {tracker.current_streak}-day streak! Keep it up!"
        return None

    def get_milestone_message(self, obj):
        """
        Returns a milestone message if today is a milestone day.
        """
        tracker = StreakAndMilestoneTracker.objects.filter(user=obj.user, habit_stack=obj.habit_stack).first()
        if tracker and str(obj.date) in tracker.milestone_dates:
            return f"Milestone achieved on this date: {obj.date}!"
        return None

# Serializer for HabitStackingLogEdit
class HabitStackingLogEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitStackingLog
        fields = ['completed']