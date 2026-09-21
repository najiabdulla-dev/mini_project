import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.apps import apps
from django.db import models

def dump_schema():
    print("# Database Schema for Skill Swap")
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('apps.'):
            print(f"\n## App: {app_config.verbose_name.title()} ({app_config.name})")
            for model in app_config.get_models():
                print(f"\n### Table: `{model._meta.db_table}` (Model: `{model.__name__}`)")
                print("| Field Name | Type | Properties |")
                print("|---|---|---|")
                for field in model._meta.get_fields():
                    if hasattr(field, 'get_internal_type'):
                        field_type = field.get_internal_type()
                    else:
                        field_type = type(field).__name__
                    
                    props = []
                    if getattr(field, 'primary_key', False): props.append("PK")
                    if getattr(field, 'unique', False): props.append("Unique")
                    if getattr(field, 'null', False): props.append("Null")
                    if getattr(field, 'blank', False): props.append("Blank")
                    
                    if hasattr(field, 'remote_field') and field.remote_field and getattr(field.remote_field, 'model', None):
                        try:
                            rel_model = field.remote_field.model
                            rel_name = rel_model._meta.object_name if hasattr(rel_model, '_meta') else str(rel_model)
                            props.append(f"FK -> {rel_name}")
                        except Exception:
                            pass
                    
                    prop_str = ", ".join(props) if props else "-"
                    print(f"| `{field.name}` | {field_type} | {prop_str} |")

if __name__ == '__main__':
    dump_schema()
