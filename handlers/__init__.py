from .sys import register_sys_routes
from .io import register_io_routes
from .api import register_api_routes

def register_all(router):
    register_sys_routes(router)
    register_io_routes(router)
    register_api_routes(router)
