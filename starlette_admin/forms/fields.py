import json

from wtforms import fields, widgets

from .widgets import TagsInput


class JSONField(fields.StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = json.loads(valuelist[0])
            except ValueError:
                raise ValueError("This field contains invalid JSON")
        else:
            self.data = []

    def _value(self):
        return json.dumps(self.data) if self.data else ""

    def pre_validate(self, form):
        super().pre_validate(form)
        if self.data:
            try:
                json.dumps(self.data)
            except TypeError:
                raise ValueError("This field contains invalid JSON")


class TagsField(JSONField):
    widget = TagsInput()
