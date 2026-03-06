"""
Django management command to switch bot configurations

Usage:
  python manage.py switch_bot_config health
  python manage.py switch_bot_config education
  python manage.py switch_bot_config general
  python manage.py switch_bot_config flexible-coursebot
  python manage.py switch_bot_config --list
"""

from django.core.management.base import BaseCommand, CommandError
from health_app.services.bot_config import BotConfigManager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Switch bot configuration (health, education, general, flexible-coursebot)'

    def add_arguments(self, parser):
        parser.add_argument(
            'config',
            nargs='?',
            type=str,
            help='Configuration name to set as active'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available configurations'
        )

    def handle(self, *args, **options):
        if options['list']:
            # List all available configurations
            configs = BotConfigManager.list_configs()
            self.stdout.write(self.style.SUCCESS('Available Bot Configurations:\n'))
            for name, description in configs.items():
                active = ' (ACTIVE)' if BotConfigManager.get_config(name) == BotConfigManager.get_active_config() else ''
                self.stdout.write(f"  • {name:20} - {description}{active}")
            return

        if not options['config']:
            raise CommandError('Please provide a configuration name or use --list to see available options')

        config_name = options['config']
        
        if BotConfigManager.set_active_config(config_name):
            config = BotConfigManager.get_active_config()
            self.stdout.write(self.style.SUCCESS(f'\n✅ Switched to configuration: {config_name}'))
            self.stdout.write(f'\nConfiguration Details:')
            self.stdout.write(f'  Name: {config.name}')
            self.stdout.write(f'  Description: {config.description}')
            self.stdout.write(f'  Data Provider Mode: {config.data_provider_mode}')
            self.stdout.write(f'  Allow Synthetic Data: {config.allow_synthetic_data}')
            self.stdout.write(f'  Visualizations Enabled: {config.visualization_enabled}')
            self.stdout.write(f'  Metadata: {config.metadata}\n')
        else:
            raise CommandError(f'Configuration "{config_name}" not found')
