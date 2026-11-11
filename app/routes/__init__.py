"""Registers every blueprint."""


def register_blueprints(app):
    from . import announcements, auth, dashboard, notices, notifications

    app.register_blueprint(dashboard.bp)
    app.register_blueprint(announcements.admin_bp)
    app.register_blueprint(announcements.api_bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(notices.bp)
    app.register_blueprint(notifications.bp)
