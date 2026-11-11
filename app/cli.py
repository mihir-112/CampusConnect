"""Command-line helpers. Owner: Aariz.

Create the first publisher with:  flask --app run create-publisher
"""
import click

from .extensions import db
from .models import Publisher


def register_cli(app):
    @app.cli.command("create-publisher")
    @click.option("--username", prompt=True)
    @click.option("--email", prompt=True)
    @click.password_option()
    def create_publisher(username, email, password):
        """Create a publisher account that can log in and manage announcements."""
        username, email = username.strip(), email.strip().lower()
        if len(password) < 8:
            raise click.ClickException("Password must be at least 8 characters.")
        if "@" not in email:
            raise click.ClickException("Enter a valid email address.")
        if Publisher.query.filter((Publisher.username == username) | (Publisher.email == email)).first():
            raise click.ClickException("A publisher with that username or email already exists.")
        publisher = Publisher(username=username, email=email)
        publisher.set_password(password)
        db.session.add(publisher)
        db.session.commit()
        click.echo(f"Publisher '{username}' created.")
