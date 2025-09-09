from django.core.management.base import BaseCommand
from payments.api_versioning import FlutterwaveAPIVersion, APIVersionManager
from payments.services import FlutterwaveService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test Flutterwave API versioning functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-version',
            default=None,
            help='API version to test (2024-01-01 or 2023-01-01)',
        )
        parser.add_argument(
            '--list-versions',
            action='store_true',
            help='List all supported API versions',
        )
        parser.add_argument(
            '--test-compatibility',
            action='store_true',
            help='Test version compatibility',
        )
        parser.add_argument(
            '--test-migration',
            action='store_true',
            help='Test migration guides',
        )

    def handle(self, *args, **options):
        version = options['api_version']
        list_versions = options['list_versions']
        test_compatibility = options['test_compatibility']
        test_migration = options['test_migration']
        
        self.stdout.write('Testing Flutterwave API Versioning')
        
        # List versions if requested
        if list_versions:
            self._list_versions()
            return
        
        # Test specific version or run comprehensive tests
        if version:
            self._test_specific_version(version)
        else:
            self._test_comprehensive_versioning()
        
        # Test compatibility
        if test_compatibility:
            self._test_compatibility()
        
        # Test migration
        if test_migration:
            self._test_migration()
    
    def _list_versions(self):
        """List all supported API versions"""
        self.stdout.write('\n=== Supported Flutterwave API Versions ===')
        
        versions = FlutterwaveAPIVersion.get_supported_versions()
        
        for version, info in versions.items():
            self.stdout.write(f'\nVersion: {version}')
            self.stdout.write(f'Name: {info["name"]}')
            self.stdout.write(f'Description: {info["description"]}')
            self.stdout.write(f'Deprecated: {info["deprecated"]}')
            
            self.stdout.write('Features:')
            for feature in info['features']:
                self.stdout.write(f'  ✅ {feature}')
            
            if info['breaking_changes']:
                self.stdout.write('Breaking Changes:')
                for change in info['breaking_changes']:
                    self.stdout.write(f'  ❌ {change}')
            
            self.stdout.write('Base URLs:')
            for env, url in info['base_urls'].items():
                self.stdout.write(f'  {env}: {url}')
    
    def _test_specific_version(self, version):
        """Test a specific API version"""
        self.stdout.write(f'\n=== Testing API Version: {version} ===')
        
        try:
            # Initialize version manager
            version_manager = FlutterwaveAPIVersion(version)
            
            # Get version info
            info = version_manager.get_version_info()
            
            self.stdout.write(f'Version: {info["version"]}')
            self.stdout.write(f'Name: {info["name"]}')
            self.stdout.write(f'Description: {info["description"]}')
            self.stdout.write(f'Deprecated: {info["deprecated"]}')
            
            # Test base URLs
            sandbox_url = version_manager.get_base_url('sandbox')
            production_url = version_manager.get_base_url('production')
            
            self.stdout.write(f'\nBase URLs:')
            self.stdout.write(f'  Sandbox: {sandbox_url}')
            self.stdout.write(f'  Production: {production_url}')
            
            # Test feature support
            self.stdout.write(f'\nFeature Support:')
            self.stdout.write(f'  OAuth 2.0: {info["supports_oauth"]}')
            self.stdout.write(f'  v4 Headers: {info["supports_v4_headers"]}')
            self.stdout.write(f'  Scenarios: {info["supports_scenarios"]}')
            
            # Test headers
            headers = version_manager.get_version_headers()
            self.stdout.write(f'\nVersion Headers:')
            for key, value in headers.items():
                self.stdout.write(f'  {key}: {value}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error testing version {version}: {e}')
            )
    
    def _test_comprehensive_versioning(self):
        """Test comprehensive versioning functionality"""
        self.stdout.write('\n=== Testing Comprehensive API Versioning ===')
        
        # Test all supported versions
        versions = FlutterwaveAPIVersion.get_supported_versions()
        
        for version in versions.keys():
            self.stdout.write(f'\n--- Testing Version: {version} ---')
            self._test_specific_version(version)
    
    def _test_compatibility(self):
        """Test version compatibility"""
        self.stdout.write('\n=== Testing Version Compatibility ===')
        
        # Initialize API version manager
        api_manager = APIVersionManager()
        
        # Test feature compatibility
        features_to_test = ['oauth', 'v4_headers', 'scenarios', 'encryption', 'webhooks']
        
        for feature in features_to_test:
            is_compatible, incompatible = api_manager.validate_version_compatibility([feature])
            status = '✅' if is_compatible else '❌'
            self.stdout.write(f'{status} {feature}: {"Compatible" if is_compatible else "Incompatible"}')
        
        # Test multiple features
        is_compatible, incompatible = api_manager.validate_version_compatibility(features_to_test)
        self.stdout.write(f'\nOverall Compatibility: {"✅ Compatible" if is_compatible else "❌ Incompatible"}')
        
        if incompatible:
            self.stdout.write('Incompatible features:')
            for feature in incompatible:
                self.stdout.write(f'  ❌ {feature}')
    
    def _test_migration(self):
        """Test migration guides"""
        self.stdout.write('\n=== Testing Migration Guides ===')
        
        # Initialize API version manager
        api_manager = APIVersionManager()
        
        # Test migration from v3 to v4
        migration_guide = api_manager.get_migration_guide('2023-01-01', '2024-01-01')
        
        self.stdout.write('\nMigration Guide (v3 → v4):')
        self.stdout.write(f'  From: {migration_guide["from_name"]}')
        self.stdout.write(f'  To: {migration_guide["to_name"]}')
        self.stdout.write(f'  Deprecated: {migration_guide["deprecated"]}')
        
        if migration_guide['breaking_changes']:
            self.stdout.write('  Breaking Changes:')
            for change in migration_guide['breaking_changes']:
                self.stdout.write(f'    ❌ {change}')
        
        if migration_guide['new_features']:
            self.stdout.write('  New Features:')
            for feature in migration_guide['new_features']:
                self.stdout.write(f'    ✅ {feature}')
        
        if migration_guide['recommendations']:
            self.stdout.write('  Recommendations:')
            for rec in migration_guide['recommendations']:
                self.stdout.write(f'    📝 {rec}')
        
        # Test migration from v4 to v3
        reverse_migration = api_manager.get_migration_guide('2024-01-01', '2023-01-01')
        
        self.stdout.write('\nMigration Guide (v4 → v3):')
        self.stdout.write(f'  From: {reverse_migration["from_name"]}')
        self.stdout.write(f'  To: {reverse_migration["to_name"]}')
        self.stdout.write(f'  Deprecated: {reverse_migration["deprecated"]}')
        
        if reverse_migration['breaking_changes']:
            self.stdout.write('  Breaking Changes:')
            for change in reverse_migration['breaking_changes']:
                self.stdout.write(f'    ❌ {change}')
    
    def _test_service_integration(self):
        """Test service integration with versioning"""
        self.stdout.write('\n=== Testing Service Integration ===')
        
        try:
            # Initialize Flutterwave service
            flutterwave_service = FlutterwaveService()
            
            # Get version info
            version_info = flutterwave_service.version_manager.version_manager.get_version_info()
            
            self.stdout.write(f'Service API Version: {version_info["version"]}')
            self.stdout.write(f'Service Name: {version_info["name"]}')
            self.stdout.write(f'Base URL: {flutterwave_service.base_url}')
            
            # Test headers generation
            headers = flutterwave_service._get_headers()
            self.stdout.write(f'\nGenerated Headers:')
            for key, value in headers.items():
                if key == 'Authorization':
                    self.stdout.write(f'  {key}: Bearer {value[:20]}...')
                else:
                    self.stdout.write(f'  {key}: {value}')
            
            self.stdout.write(
                self.style.SUCCESS('✅ Service integration with versioning working')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Service integration test failed: {e}')
            )
        
        self.stdout.write('\nAPI versioning testing completed') 