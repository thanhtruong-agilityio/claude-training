from datetime import date, datetime
from zoneinfo import ZoneInfo

CLINIC_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


def now() -> datetime:
    """Current clinic time as a naive datetime (the format stored in the database)."""
    return datetime.now(CLINIC_TZ).replace(tzinfo=None)


def today() -> date:
    return now().date()
