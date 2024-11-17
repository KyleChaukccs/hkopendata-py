from pathlib import Path
from typing import Dict, Iterator, Literal, Optional, TypedDict, cast
import requests
from typing_extensions import overload, TypeAlias, assert_never
from datetime import date, datetime
import pandas as pd
from _helper import DataConverter

DAILY_PASSENGERS_TRAFFIC_URL = "https://www.immd.gov.hk/opendata/{locale}/transport/immigration_clearance/statistics_on_daily_passenger_traffic.csv"

Locale: TypeAlias = Literal["eng", "hkt", "hks"]

_direction_locale_map: Dict[Locale, Dict[Literal["Arrival", "Departure"], str]] = {
    "eng": {
        "Arrival": "Arrival",
        "Departure": "Departure",
    },
    "hkt": {
        "Arrival": "入境",
        "Departure": "離境",
    },
    "hks": {
        "Arrival": "入境",
        "Departure": "离境",
    },
}

class DailyPassengersTrafficTypeDef(TypedDict):
    date: date
    control_point: str
    arrival_departure: Literal["Arrival", "Departure"]
    hk_residents_count: int
    mainland_china_residents_count: int
    other_visitors_count: int
    total_count: int

def _get_daily_traffics(
    since: date,
    till: date = date.today(),
    locale: Locale = "eng",
    control_point_filter: Optional[str] = None,
    only_direction: Optional[Literal["Arrival", "Departure"]] = None,
) -> DataConverter:
    url = DAILY_PASSENGERS_TRAFFIC_URL.format(locale=locale)

    session = requests.Session()
    with session.get(url) as r:
        r.raise_for_status()

        line_iter = cast(Iterator[bytes], r.iter_lines())

        #! We need to remove the BOM from the first line
        header = cast(bytes, next(line_iter)).decode("utf-8-sig").split(",")

    def _gen(line_iter: Iterator[bytes]):
        for line in line_iter:
            if not line:
                continue
            line_str = line.decode("utf-8")

            (
                date,
                control_point,
                arrival_departure,
                hk_residents_count,
                mainland_china_residents_count,
                other_visitors_count,
                total_count,
            ) = line_str.rstrip(",").split(",")

            date_dt = datetime.strptime(date, "%d-%m-%Y").date()

            if date_dt < since:
                continue

            if date_dt > till:
                break

            if (
                control_point_filter is not None
                and control_point != control_point_filter
            ):
                continue

            if (
                only_direction is not None
                and arrival_departure != _direction_locale_map[locale][only_direction]
            ):
                continue

            yield cast(
                DailyPassengersTrafficTypeDef,
                {
                    "date": date_dt,
                    "control_point": control_point,
                    "arrival_departure": arrival_departure,
                    "hk_residents_count": int(hk_residents_count),
                    "mainland_china_residents_count": int(
                        mainland_china_residents_count
                    ),
                    "other_visitors_count": int(other_visitors_count),
                    "total_count": int(total_count),
                },
            )

    return DataConverter(_gen(line_iter), header)



@overload
def get_daily_traffics(
    *,
    since: date,
    till: date = date.today(),
    control_point: Optional[str] = None,
    only_direction: Optional[Literal["Arrival", "Departure"]] = None,
    locale: Locale = "eng",
    format: Literal["pd"] = "pd",
) -> pd.DataFrame: ...


@overload
def get_daily_traffics(
    *,
    since: date,
    till: date = date.today(),
    control_point: Optional[str] = None,
    only_direction: Optional[Literal["Arrival", "Departure"]] = None,
    locale: Locale = "eng",
    format: Literal["file"] = "file",
    file_path: Path = None,
) -> None: ...


def get_daily_traffics(
    *,
    since: date,
    till: date = date.today(),
    locale: Locale = "eng",
    format: Literal["pd", "file"] = "pd",
    control_point: Optional[str] = None,
    only_direction: Optional[Literal["Arrival", "Departure"]] = None,
    file_path: Path = None,
):
    container = _get_daily_traffics(
        since=since,
        till=till,
        locale=locale,
        control_point_filter=control_point,
        only_direction=only_direction,
    )
    if format == "pd":
        return container.to_pd()
    if format == "file":
        container.to_file(file_path)
    assert_never(format)