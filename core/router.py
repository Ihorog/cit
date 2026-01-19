import re
import json
from typing import Callable, List, Optional, Pattern
from http.server import BaseHTTPRequestHandler
from dataclasses import dataclass

@dataclass
class Route:
    pattern: str
    handler: Callable
    regex: Optional[Pattern] = None
    is_regex: bool = False

class Router:
    def __init__(self):
        self.routes: List[Route] = []
    def register(self, path, handler, regex=False):
        route = Route(pattern=path, handler=handler, is_regex=regex)
        if regex: route.regex = re.compile(path)
        self.routes.append(route)
    def route(self, path, regex=False):
        def wrapper(func):
            self.register(path, func, regex=regex)
            return func
        return wrapper
    def dispatch(self, handler, method="POST"):
        path = handler.path.split('?')[0]
        for route in self.routes:
            if not route.is_regex and route.pattern == path:
                return route.handler(handler)
            if route.is_regex and route.regex and route.regex.match(path):
                match = route.regex.match(path)
                return route.handler(handler, **match.groupdict())
        handler.send_response(404)
        handler.end_headers()
        handler.wfile.write(json.dumps({"ok": False, "error": "not_found"}).encode())

_router = Router()
def get_router(): return _router
