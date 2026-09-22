"""
Profile serializers for Skill Swap.

Handles: UserSkill, Experience, Education, Certificate, Portfolio.
"""

from rest_framework import serializers
from .models import UserSkill, Experience, Education, Certificate, Portfolio


class UserSkillSerializer(serializers.ModelSerializer):
    """Read serializer for user skills with nested skill info."""

    skill_name = serializers.CharField(source='skill.name', read_only=True)
    category_name = serializers.CharField(source='skill.category.name', read_only=True)

    class Meta:
        model = UserSkill
        fields = [
            'id', 'user', 'skill', 'skill_name', 'category_name',
            'proficiency', 'price', 'description',
            'years_experience', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'skill_name', 'category_name', 'created_at', 'updated_at']


class UserSkillCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating/updating user skills."""
    
    skill = serializers.CharField()

    class Meta:
        model = UserSkill
        fields = [
            'id', 'skill', 'proficiency', 'price',
            'description', 'years_experience', 'is_active',
        ]
        read_only_fields = ['id']

    def validate_skill(self, value):
        from apps.skills.models import Skill, Category
        skill_name = value.strip()
        skill = Skill.objects.filter(name__iexact=skill_name).first()
        if not skill:
            category, _ = Category.objects.get_or_create(
                name='Other',
                defaults={'description': 'Auto-created category for custom skills'}
            )
            # Create a properly capitalized version of the skill name
            skill = Skill.objects.create(name=skill_name.title(), category=category)
            
        if not skill.is_active:
            raise serializers.ValidationError('Cannot add an inactive skill.')
        return skill

    def validate(self, attrs):
        user = self.context['request'].user
        skill = attrs.get('skill')
        if skill and not self.instance:
            if UserSkill.objects.filter(user=user, skill=skill).exists():
                raise serializers.ValidationError(
                    {'skill': 'You have already added this skill.'}
                )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for work experience entries."""

    class Meta:
        model = Experience
        fields = [
            'id', 'user', 'title', 'company',
            'start_date', 'end_date', 'description', 'is_current',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        is_current = attrs.get('is_current', getattr(self.instance, 'is_current', False))

        if end and start and end < start:
            raise serializers.ValidationError(
                {'end_date': 'End date cannot be before start date.'}
            )
        if is_current and end:
            raise serializers.ValidationError(
                {'end_date': 'Current positions should not have an end date.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class EducationSerializer(serializers.ModelSerializer):
    """Serializer for education entries."""

    class Meta:
        model = Education
        fields = [
            'id', 'user', 'degree', 'institution', 'field_of_study',
            'start_date', 'end_date', 'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if end and start and end < start:
            raise serializers.ValidationError(
                {'end_date': 'End date cannot be before start date.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for professional certificates."""

    class Meta:
        model = Certificate
        fields = [
            'id', 'user', 'name', 'issuer',
            'credential_url', 'credential_id',
            'issue_date', 'expiry_date', 'image',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        issue = attrs.get('issue_date', getattr(self.instance, 'issue_date', None))
        expiry = attrs.get('expiry_date', getattr(self.instance, 'expiry_date', None))
        if expiry and issue and expiry < issue:
            raise serializers.ValidationError(
                {'expiry_date': 'Expiry date cannot be before issue date.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for portfolio items."""

    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'title', 'description',
            'url', 'image', 'skill', 'skill_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'skill_name', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserProfileSerializer(serializers.Serializer):
    """
    Aggregated read-only profile serializer for viewing another user's profile.
    Combines user info with all profile sub-resources.
    """

    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    full_name = serializers.SerializerMethodField()
    phone = serializers.CharField()
    profile_photo = serializers.ImageField()
    bio = serializers.CharField()
    location = serializers.CharField()
    github_url = serializers.URLField()
    linkedin_url = serializers.URLField()
    hourly_rate = serializers.DecimalField(max_digits=8, decimal_places=2)
    languages = serializers.JSONField()
    availability = serializers.CharField()
    skills = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    portfolio = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_skills(self, obj):
        return UserSkillSerializer(
            obj.user_skills.filter(is_active=True), many=True
        ).data

    def get_experiences(self, obj):
        return ExperienceSerializer(obj.experiences.all(), many=True).data

    def get_education(self, obj):
        return EducationSerializer(obj.education_entries.all(), many=True).data

    def get_certificates(self, obj):
        return CertificateSerializer(obj.certificates.all(), many=True).data

    def get_portfolio(self, obj):
        return PortfolioSerializer(obj.portfolio_items.all(), many=True).data

    def get_average_rating(self, obj):
        from django.db.models import Avg
        result = obj.reviews_received.aggregate(avg=Avg('rating'))
        return round(result['avg'], 2) if result['avg'] else None

    def get_total_reviews(self, obj):
        return obj.reviews_received.count()
