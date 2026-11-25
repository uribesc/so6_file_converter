"""Convert SO6 flight traffic files into pandas DataFrames."""

from .reader import add_country_flow, so6_to_df, so6_to_df_simple, so6_to_df_waypoints, time_to_seconds

__version__ = "0.1.1"

__all__ = ["add_country_flow", "so6_to_df", "so6_to_df_simple", "so6_to_df_waypoints", "time_to_seconds", "__version__"]
