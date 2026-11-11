"""Notice detail page and attachment downloads. Owner: Nayeem."""
from flask import Blueprint, abort, render_template, request, send_from_directory

from ..services import announcement_service, attachment_service

bp = Blueprint("notices", __name__, url_prefix="/notices")


@bp.get("/<int:announcement_id>")
def detail(announcement_id):
    announcement = announcement_service.get_announcement(announcement_id)  # 404 for drafts
    attachments = {}
    for kind in attachment_service.KINDS:
        record = announcement.get_attachment(kind)
        if record is not None:
            attachments[kind] = {
                "record": record,
                "available": attachment_service.file_exists(record),
            }
    return render_template("notice_detail.html", announcement=announcement, attachments=attachments)


def _serve(announcement_id, kind, as_attachment=False):
    announcement_service.get_announcement(announcement_id)  # 404 for drafts
    record = attachment_service.get_attachment(announcement_id, kind)
    if record is None or not attachment_service.file_exists(record):
        abort(404)
    response = send_from_directory(
        attachment_service.upload_folder(),
        record.stored_filename,
        mimetype=record.mime_type,
        as_attachment=as_attachment,
        download_name=record.original_filename,
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@bp.get("/<int:announcement_id>/poster")
def poster(announcement_id):
    return _serve(announcement_id, "poster")


@bp.get("/<int:announcement_id>/pdf")
def pdf(announcement_id):
    return _serve(announcement_id, "pdf", as_attachment=request.args.get("download") == "1")
