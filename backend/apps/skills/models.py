"""
Skill and Category models for Skill Swap.

Categories group skills (e.g., "Web Development", "Design", "Music").
Skills are individual competencies (e.g., "Flutter", "Logo Design", "Guitar").
"""

from django.db import models
from utils.models import SoftDeleteModel


class Category(SoftDeleteModel):
    """
    Skill category for organizing skills into groups.

    Examples: Web Development, Mobile Development, Design,
    Music, Photography, Writing, Marketing, etc.
    """

    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(
        max_length=50, blank=True, default='',
        help_text='Icon name or emoji for the category',
    )
    description = models.TextField(blank=True, default='')
    sort_order = models.IntegerField(
        default=0, db_index=True,
        help_text='Display order (lower numbers appear first)',
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class Skill(SoftDeleteModel):
    """
    Individual skill that users can offer.

    Each skill belongs to a category. Users link to skills via UserSkill
    (defined in the profiles app) with additional metadata like
    proficiency level and pricing.
    """

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='skills',
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'skills'
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
        ordering = ['name']
        indexes = [
            models.Index(fields=['category', 'is_active'], name='idx_skill_category'),
            models.Index(fields=['name'], name='idx_skill_name'),
        ]

    def __str__(self):
        return f'{self.name} ({self.category.name})'
