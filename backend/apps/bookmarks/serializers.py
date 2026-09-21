"""
Bookmark serializers for Skill Swap.
"""

from rest_framework import serializers
from .models import Bookmark


class BookmarkSerializer(serializers.ModelSerializer):
    """Read serializer for bookmarks with bookmarked user info."""

    bookmarked_user_name = serializers.CharField(
        source='bookmarked_user.get_full_name', read_only=True,
    )
    bookmarked_user_email = serializers.EmailField(
        source='bookmarked_user.email', read_only=True,
    )
    bookmarked_user_photo = serializers.ImageField(
        source='bookmarked_user.profile_photo', read_only=True,
    )
    bookmarked_user_bio = serializers.CharField(
        source='bookmarked_user.bio', read_only=True,
    )
    bookmarked_user_location = serializers.CharField(
        source='bookmarked_user.location', read_only=True,
    )

    class Meta:
        model = Bookmark
        fields = [
            'id', 'user', 'bookmarked_user',
            'bookmarked_user_name', 'bookmarked_user_email',
            'bookmarked_user_photo', 'bookmarked_user_bio',
            'bookmarked_user_location',
            'created_at',
        ]
        read_only_fields = [
            'id', 'user', 'bookmarked_user_name', 'bookmarked_user_email',
            'bookmarked_user_photo', 'bookmarked_user_bio',
            'bookmarked_user_location', 'created_at',
        ]


class BookmarkCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating bookmarks."""

    class Meta:
        model = Bookmark
        fields = ['id', 'bookmarked_user']
        read_only_fields = ['id']

    def validate_bookmarked_user(self, value):
        user = self.context['request'].user
        if value == user:
            raise serializers.ValidationError('You cannot bookmark your own profile.')
        if Bookmark.objects.filter(user=user, bookmarked_user=value).exists():
            raise serializers.ValidationError('You have already bookmarked this user.')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
