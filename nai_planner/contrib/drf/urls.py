from rest_framework.routers import DefaultRouter

from nai_planner.contrib.drf.views import PlannerItemViewSet

router = DefaultRouter()
router.register(r"planner", PlannerItemViewSet, basename="planner-item")

urlpatterns = router.urls
