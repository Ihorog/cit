# ci_stability_system — dormant plugin
# Активується через plugin_loader при наявності manifest.json status="active"
PLUGIN_ID = "ci_stability_system"
PLUGIN_STATUS = "dormant"


def activate():
    from .api import router
    return router
