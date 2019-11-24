from datetime import datetime

from starlette_admin.widgets import BaseWidget


class Today(BaseWidget):
    def get_context(self):
        return {
            "icon": "fa fa-calendar",
            "value": datetime.now().strftime("%d %B %Y"),
            "text": "Today"
        }


class Time(BaseWidget):
    def get_context(self):
        return {
            "icon": "fa fa-clock",
            "value": datetime.now().strftime("%H:%M"),
            "text": "Time"
        }


class DayOfYear(BaseWidget):
    def get_context(self):
        return {
            "icon": "fa fa-calendar-day",
            "value": datetime.now().strftime("%j"),
            "text": "Day of year"
        }
