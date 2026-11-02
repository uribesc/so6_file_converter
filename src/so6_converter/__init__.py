"""Convert SO6 flight traffic files into pandas DataFrames."""

from .reader import add_country_flow, so6_to_df, so6_to_df_simple, so6_to_df_waypoints

__version__ = "0.1.0"

__all__ = ["add_country_flow", "so6_to_df", "so6_to_df_simple", "so6_to_df_waypoints", "__version__"]
