"""Jinja filters shared by all templates. Owner: Moksh."""
from datetime import date, datetime, time

from .constants import CATEGORIES


def register_template_helpers(app):
    @app.template_filter("date_fmt")
    def date_fmt(value):
        if isinstance(value, (date, datetime)):
            return value.strftime("%d %b %Y")
        return ""

    @app.template_filter("time_fmt")
    def time_fmt(value):
        if isinstance(value, (time, datetime)):
            return value.strftime("%I:%M %p").lstrip("0")
        return ""

    @app.template_filter("cat_class")
    def cat_class(category):
        return "cat-" + str(category).lower()

    @app.context_processor
    def inject_constants():
        return {"CATEGORIES": CATEGORIES}
