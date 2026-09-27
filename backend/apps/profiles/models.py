"""
Profile-related models for Skill Swap.

These extend the User model with professional information:
skills, experience, education, certificates, and portfolio.
"""

from django.db import models
from django.conf import settings
from utils.models import TimestampedModel


class UserSkill(TimestampedModel):
    """
    A user's declared skill with proficiency level and pricing.
    Links a User to a Skill with additional metadata.
    """

    class Proficiency(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'
        EXPERT = 'expert', 'Expert'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_skills',
    )
    skill = models.ForeignKey(
        'skills.Skill',
        on_delete=models.CASCADE,
        related_name='user_skills',
    )
    proficiency = models.CharField(
        max_length=20,
        choices=Proficiency.choices,
        default=Proficiency.BEGINNER,
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Price for this specific skill (overrides user hourly rate)',
    )
    description = models.TextField(
        blank=True, default='',
        help_text='Description of experience with this skill',
    )
    years_experience = models.PositiveIntegerField(
        default=0,
        help_text='Years of experience with this skill',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_skills'
        verbose_name = 'User Skill'
        verbose_name_plural = 'User Skills'
        unique_together = ['user', 'skill']
        indexes = [
            models.Index(fields=['user', 'is_active'], name='idx_userskill_user'),
            models.Index(fields=['skill', 'proficiency'], name='idx_userskill_skill'),
        ]

    def __str__(self):
        return f'{self.user.email} — {self.skill.name} ({self.proficiency})'


class Experience(TimestampedModel):
    """Work experience entry on a user's profile."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='experiences',
    )
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, default='')
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = 'experiences'
        verbose_name = 'Experience'
        verbose_name_plural = 'Experiences'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', '-start_date'], name='idx_experience_user'),
        ]

    def __str__(self):
        return f'{self.title} at {self.company}'


class Education(TimestampedModel):
    """Education entry on a user's profile."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='education_entries',
    )
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True, default='')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'education'
        verbose_name = 'Education'
        verbose_name_plural = 'Education Entries'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['user', '-start_date'], name='idx_education_user'),
        ]

    def __str__(self):
        return f'{self.degree} — {self.institution}'


class Certificate(TimestampedModel):
    """Professional certificate on a user's profile."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
    )
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    credential_url = models.URLField(blank=True, default='')
    credential_id = models.CharField(max_length=200, blank=True, default='')
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='certificates/', blank=True, null=True)

    class Meta:
        db_table = 'certificates'
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['user', '-issue_date'], name='idx_certificate_user'),
        ]

    def __str__(self):
        return f'{self.name} — {self.issuer}'


class Portfolio(TimestampedModel):
    """Portfolio item showcasing a user's work."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio_items',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    url = models.URLField(blank=True, default='', help_text='Link to the project')
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    skill = models.ForeignKey(
        'skills.Skill',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='portfolio_items',
        help_text='Related skill for this portfolio item',
    )

    class Meta:
        db_table = 'portfolio'
        verbose_name = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user'], name='idx_portfolio_user'),
        ]

    def __str__(self):
        return self.title


class RecommendationHistory(models.Model):
    """Tracks which users have been recommended to a viewer to ensure rotation."""
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='viewed_recommendations'
    )
    shown_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shown_in_recommendations'
    )
    shown_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendation_history'
        verbose_name = 'Recommendation History'
        verbose_name_plural = 'Recommendation Histories'
        indexes = [
            models.Index(fields=['viewer', 'shown_user']),
            models.Index(fields=['viewer', '-shown_at']),
        ]

    def __str__(self):
        return f"{self.viewer.email} saw {self.shown_user.email} at {self.shown_at}"
