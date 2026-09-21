"""
Settings package for Skill Swap.
Defaults to development settings.
"""
import os

environment = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')
