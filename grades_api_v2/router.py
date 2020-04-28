from rest_framework_extensions.routers import (
    ExtendedSimpleRouter,
    ExtendedDefaultRouter,
)


class SharedAPIRootRouter(ExtendedSimpleRouter):
    shared_router = ExtendedDefaultRouter()

    def register(self, *args, **kwargs):
        self.shared_router.register(*args, **kwargs)
        return super().register(*args, **kwargs)
