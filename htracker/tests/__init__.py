from .test_api_tasks import HabitAPITest
from .test_celery import HabitCeleryTest
from .test_habits import HabitModelTest
from .test_permissions import HabitPermissionsTest
from .test_views import HabitViewSetTests

__all__ = [
    "HabitPermissionsTest",
    "HabitCeleryTest",
    "HabitModelTest",
    "HabitAPITest",
    "HabitViewSetTests",
]
