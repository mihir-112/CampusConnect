"""Command-line helpers.

Create the first publisher:   py -m backend.cli create-publisher
Owner: Aariz (uses the shared database settings).
"""
import argparse
import getpass
import sys

from backend.core.config import load_settings
from backend.core.errors import AppError
from backend.database import Database
from features.publisher_auth.backend.services import auth_service


def create_publisher(args) -> int:
    username = args.username or input("Username: ").strip()
    email = args.email or input("Email: ").strip()
    password = args.password or getpass.getpass("Password (8+ characters): ")
    if not args.password and getpass.getpass("Repeat password: ") != password:
        print("The passwords do not match.", file=sys.stderr)
        return 1

    database = Database(load_settings().database_url)
    database.create_tables()
    try:
        with database.session_factory() as db:
            auth_service.create_publisher(db, username, email, password)
    except AppError as err:
        print("Could not create the publisher: " + (", ".join(err.fields.values()) if err.fields else err.message), file=sys.stderr)
        return 1
    finally:
        database.dispose()
    print(f"Publisher '{username}' created.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="backend.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-publisher", help="Create a publisher account")
    create.add_argument("--username")
    create.add_argument("--email")
    create.add_argument("--password", help="Avoid this on shared machines; you will be asked if you leave it out")
    create.set_defaults(handler=create_publisher)
    args = parser.parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
