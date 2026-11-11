"""Publisher login and logout. Owner: Aariz."""
from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db, login_manager
from ..forms.auth_forms import LoginForm
from ..models import Publisher

bp = Blueprint("auth", __name__, url_prefix="/auth")


@login_manager.user_loader
def load_publisher(user_id):
    try:
        return db.session.get(Publisher, int(user_id))
    except (TypeError, ValueError):
        return None


def _safe_next(target):
    """Only follow `next` if it is a path on this site (stops open-redirect attacks)."""
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc or not target.startswith("/") or target.startswith("//"):
        return None
    if "\\" in target:
        return None
    return target


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        publisher = Publisher.query.filter_by(username=form.username.data.strip()).first()
        if publisher is not None and publisher.check_password(form.password.data):
            session.clear()
            login_user(publisher)
            session.permanent = True
            return redirect(_safe_next(request.args.get("next")) or url_for("admin.dashboard"))
        # Same message for unknown user and wrong password, so nobody can probe usernames.
        flash("Invalid username or password.", "error")
    return render_template("login.html", form=form)


@bp.post("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("dashboard.index"))
