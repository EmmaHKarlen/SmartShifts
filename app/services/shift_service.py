from app.db import session
from app.models.shift import BaseShift
from app.models.time import Time


def create_shift(db: session, user_id: int, start: Time, end: Time): # user_id?
    if start >= end:
        raise ValueError("Start time must be before end time")
    new_shift = BaseShift(user_id=user_id, start_time=start, end_time=end)