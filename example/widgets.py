from datetime import datetime

from starlette_admin.widgets import BaseWidget


class Today(BaseWidget):
    def get_context(self):
        return {
            "icon": "fa fa-calendar",
            "value": datetime.utcnow().strftime("%d %B %Y"),
            "text": "Today",
            "description": "The date as at UTC time"
        }


class Time(BaseWidget):
    def get_context(self):
        return {
            "icon": "fa fa-clock",
            "value": datetime.utcnow().strftime("%H:%M"),
            "text": "Time",
            "description": "The time as at UTC time"
        }


class DayOfYear(BaseWidget):
    def get_context(self):
        return {
            "icon": "fa fa-calendar-day",
            "value": datetime.utcnow().strftime("%-j"),
            "text": "Day of year",
            "description": "The day of the year as at UTC time"
        }
