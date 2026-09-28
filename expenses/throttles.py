from rest_framework.throttling import SimpleRateThrottle, UserRateThrottle

class AuthRateThrottle(SimpleRateThrottle):
    scope = 'auth'

    def get_cache_key(self, request, view):
        # Throttle by IP address for unauthenticated requests
        return self.get_ident(request)

class AnalyticsRateThrottle(UserRateThrottle):
    scope = 'analytics'