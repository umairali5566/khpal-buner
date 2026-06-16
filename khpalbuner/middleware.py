class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "font-src 'self' https://cdnjs.cloudflare.com data:",
            "img-src 'self' data: https:",
            "frame-src https://www.google.com https://maps.google.com",
            "connect-src 'self'",
            "base-uri 'self'",
            "form-action 'self'",
            "object-src 'none'",
            "frame-ancestors 'self'",
            "trusted-types default",
            "require-trusted-types-for 'script'",
        ]

        response.setdefault('Content-Security-Policy', '; '.join(csp_directives))
        response.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        return response
