"""
Skill and Category serializers for Skill Swap.
"""

from rest_framework import serializers
from .models import Category, Skill


class CategorySerializer(serializers.ModelSerializer):
    """Read/write serializer for skill categories."""

    skills_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'icon', 'description',
            'sort_order', 'is_active', 'skills_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'skills_count', 'created_at', 'updated_at']

    def get_skills_count(self, obj):
        return obj.skills.filter(is_active=True).count()


class SkillSerializer(serializers.ModelSerializer):
    """Read serializer for skills — includes nested category."""

    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Skill
        fields = [
            'id', 'name', 'description',
            'category', 'category_name',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'category_name', 'created_at', 'updated_at']


class SkillCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating/updating skills."""

    class Meta:
        model = Skill
        fields = ['id', 'name', 'description', 'category', 'is_active']
        read_only_fields = ['id']

    def validate_category(self, value):
        if not value.is_active:
            raise serializers.ValidationError('Cannot add a skill to an inactive category.')
        return value
