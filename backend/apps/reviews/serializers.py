"""
Review serializers for Skill Swap.
"""

from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Read serializer for reviews."""

    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    reviewer_photo = serializers.ImageField(source='reviewer.profile_photo', read_only=True)
    reviewee_name = serializers.CharField(source='reviewee.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'reviewer_name', 'reviewer_photo',
            'reviewee', 'reviewee_name',
            'hire_request', 'rating', 'comment', 'screenshot',
            'is_reported', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'reviewer', 'reviewer_name', 'reviewer_photo',
            'reviewee_name', 'is_reported', 'created_at', 'updated_at',
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating reviews."""

    class Meta:
        model = Review
        fields = ['id', 'reviewee', 'hire_request', 'rating', 'comment', 'screenshot']
        read_only_fields = ['id']

    def validate_hire_request(self, value):
        from apps.hiring.models import HireRequest
        if value.status != HireRequest.Status.COMPLETED:
            raise serializers.ValidationError(
                'You can only review completed hire requests.'
            )
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        reviewee = attrs.get('reviewee')
        hire_request = attrs.get('hire_request')

        if reviewee == user:
            raise serializers.ValidationError(
                {'reviewee': 'You cannot review yourself.'}
            )

        # Ensure user is a party to the hire request
        if user not in (hire_request.client, hire_request.provider):
            raise serializers.ValidationError(
                {'hire_request': 'You are not a party to this hire request.'}
            )

        # Ensure reviewee is the other party
        if reviewee not in (hire_request.client, hire_request.provider):
            raise serializers.ValidationError(
                {'reviewee': 'Reviewee must be the other party in the hire request.'}
            )

        # Check for duplicate review
        if Review.objects.filter(
            reviewer=user, reviewee=reviewee, hire_request=hire_request,
        ).exists():
            raise serializers.ValidationError(
                'You have already reviewed this user for this hire request.'
            )

        return attrs

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)
