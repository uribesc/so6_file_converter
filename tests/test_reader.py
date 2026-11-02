from pathlib import Path

import pytest

from so6_converter import so6_to_df, so6_to_df_simple, so6_to_df_waypoints

SAMPLE = Path(__file__).parent / "data" / "sample.so6"


def test_so6_to_df():
    df = so6_to_df(SAMPLE)
    assert len(df) == 3
    assert df.loc[0, 'segment_id'] == 'LEMD_BAN'
    assert df.loc[0, 'lat_ini'] == pytest.approx(40.41)
    assert df.loc[0, 'fl_end'] == 100
    assert list(df['flown_distance']) == [100.5, 100.5, 60.0]
    assert list(df['country_flow']) == ['EG_LE', 'EG_LE', 'EG_GC']


def test_so6_to_df_simple():
    df = so6_to_df_simple(SAMPLE)
    assert list(df['flightid']) == ['1001', '2002']
    assert df.loc[0, 'alt'] == [0, 100]
    assert df.loc[0, 'total_distance'] == 100.5
    assert df.loc[1, 'callsign'] == 'RYR100'


def test_so6_to_df_waypoints():
    df = so6_to_df_waypoints(SAMPLE)
    # BAN ends segment 1 and starts segment 2 with the same data, so it is kept only once
    assert list(df['waypoint']) == ['LEMD', 'BAN', 'SIE', 'EIDW', 'ABC']
    assert df.iloc[-1]['lat'] == pytest.approx(52.5)
