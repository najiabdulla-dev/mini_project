"""Django admin for Profile models."""
from django.contrib import admin
from .models import UserSkill, Experience, Education, Certificate, Portfolio


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'proficiency', 'price', 'years_experience', 'is_active']
    list_filter = ['proficiency', 'is_active']
    search_fields = ['user__email', 'skill__name']


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'company', 'start_date', 'end_date', 'is_current']
    search_fields = ['user__email', 'title', 'company']


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['user', 'degree', 'institution', 'field_of_study', 'start_date']
    search_fields = ['user__email', 'degree', 'institution']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'issuer', 'issue_date', 'expiry_date']
    search_fields = ['user__email', 'name', 'issuer']


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'skill', 'created_at']
    search_fields = ['user__email', 'title']
    list_filter = ['skill']
