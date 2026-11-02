"""What `import django_crudlink` loads."""

import subprocess
import sys

from django.test import SimpleTestCase


class PackageTest(SimpleTestCase):
    def test_import_is_light(self) -> None:
        # `column` comes from the package without the shared props and inertia (reading __version__ loads it too)
        code = "import sys, django_crudlink; print(sorted({'inertia', 'django_crudlink.shared'} & set(sys.modules)))"
        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)  # noqa: S603
        self.assertEqual(result.stdout.strip(), "[]")
