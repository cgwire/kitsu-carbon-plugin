from . import resources


routes = [
    ("/factors", resources.CarbonFactorsResource),
    ("/factors/<country_code>", resources.CarbonFactorResource),
    ("/footprint", resources.StudioFootprintResource),
    (
        "/productions/<project_id>/footprint/sequences",
        resources.ProductionSequenceFootprintResource,
    ),
    (
        "/productions/<project_id>/footprint/episodes",
        resources.ProductionEpisodeFootprintResource,
    ),
    (
        "/productions/<project_id>/footprint/assets",
        resources.ProductionAssetFootprintResource,
    ),
    (
        "/productions/<project_id>/footprint/task-types",
        resources.ProductionTaskTypeFootprintResource,
    ),
    (
        "/productions/<project_id>/footprint/summary",
        resources.ProductionFootprintSummaryResource,
    ),
]


def pre_install(manifest):
    """
    Pre install the plugin.
    """
    pass


def post_install(manifest):
    """
    Post install the plugin. Seeds initial carbon factor data.
    """
    from .models import CarbonFactor

    CarbonFactor.seed_initial_data()


def pre_uninstall(manifest):
    """
    Pre uninstall the plugin.
    """
    pass


def post_uninstall(manifest):
    """
    Post uninstall the plugin.
    """
    pass
