// Create or edit an announcement, with poster and PDF. Owner: Mihir.
import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import AttachmentUploader from "@features/notice-details/frontend/components/AttachmentUploader";
import { deleteAttachment, uploadAttachment } from "@features/notice-details/frontend/attachmentsApi";
import StateMessage from "@features/student-dashboard/frontend/components/StateMessage";
import { CATEGORIES, LINK_MAX, TITLE_MAX, VENUE_MAX } from "@/utils/constants";
import { usePageTitle } from "@/utils/usePageTitle";
import { createAnnouncement, getAnnouncement, updateAnnouncement } from "../announcementsApi";
import "../publisher.css";

const EMPTY = { title: "", category: "", description: "", event_date: "", event_time: "", venue: "", registration_link: "", is_published: false };

export function validate(values) {
  const errors = {};
  if (!values.title.trim()) errors.title = "Title is required.";
  else if (values.title.trim().length > TITLE_MAX) errors.title = `Title must be ${TITLE_MAX} characters or fewer.`;
  if (!CATEGORIES.includes(values.category)) errors.category = "Choose a category.";
  if (!values.description.trim()) errors.description = "Description is required.";
  if (values.venue.trim().length > VENUE_MAX) errors.venue = `Venue must be ${VENUE_MAX} characters or fewer.`;
  const link = values.registration_link.trim();
  if (link && (link.length > LINK_MAX || !/^https?:\/\/\S+$/i.test(link))) errors.registration_link = "Registration link must start with http:// or https://.";
  return errors;
}

function Field({ id, label, error, hint, children }) {
  return (
    <div className="form-row">
      <label htmlFor={id}>{label}</label>
      {children}
      {hint && <p className="hint">{hint}</p>}
      {error && (
        <p className="field-error" id={`${id}-error`}>
          {error}
        </p>
      )}
    </div>
  );
}

function AnnouncementForm({ id }) {
  const editing = Boolean(id);
  usePageTitle(editing ? "Edit announcement" : "New announcement");
  const navigate = useNavigate();
  const location = useLocation();

  const [values, setValues] = useState(EMPTY);
  const [loaded, setLoaded] = useState(editing ? null : { attachments: [] });
  const [loadError, setLoadError] = useState(null);
  const [files, setFiles] = useState({ poster: null, pdf: null });
  const [removed, setRemoved] = useState({ poster: false, pdf: false });
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState(location.state?.notice || "");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!editing) return undefined;
    const controller = new AbortController();
    getAnnouncement(id, controller.signal)
      .then((a) => {
        setLoaded(a);
        setValues({
          title: a.title,
          category: a.category,
          description: a.description,
          event_date: a.event_date || "",
          event_time: (a.event_time || "").slice(0, 5),
          venue: a.venue || "",
          registration_link: a.registration_link || "",
          is_published: a.is_published,
        });
      })
      .catch((error) => error.name !== "AbortError" && setLoadError(error));
    return () => controller.abort();
  }, [id, editing]);

  const set = (name) => (event) => setValues((v) => ({ ...v, [name]: event.target.type === "checkbox" ? event.target.checked : event.target.value }));
  const attachmentOf = (kind) => loaded?.attachments.find((a) => a.kind === kind);

  async function onSubmit(event) {
    event.preventDefault();
    const found = validate(values);
    setErrors(found);
    setMessage("");
    if (Object.keys(found).length) return;

    setBusy(true);
    const body = {
      title: values.title.trim(),
      description: values.description.trim(),
      category: values.category,
      venue: values.venue.trim() || null,
      event_date: values.event_date || null,
      event_time: values.event_time || null,
      registration_link: values.registration_link.trim() || null,
      is_published: values.is_published,
    };

    let saved;
    try {
      saved = editing ? await updateAnnouncement(id, body) : await createAnnouncement(body);
    } catch (error) {
      setErrors(error.fields || {});
      setMessage(error.message);
      setBusy(false);
      return;
    }

    // The announcement is saved; now apply the file changes.
    const problems = [];
    for (const kind of ["poster", "pdf"]) {
      try {
        if (files[kind]) await uploadAttachment(saved.id, kind, files[kind]);
        else if (removed[kind] && attachmentOf(kind)) await deleteAttachment(attachmentOf(kind).id);
      } catch (error) {
        problems.push(`the ${kind === "pdf" ? "PDF" : "poster"} could not be saved (${error.fields?.file || error.message})`);
      }
    }
    setBusy(false);

    if (problems.length) {
      navigate(`/publisher/announcements/${saved.id}/edit`, { replace: true, state: { notice: `Announcement saved, but ${problems.join(", and ")}.` } });
      return;
    }
    navigate("/publisher", { state: { notice: editing ? "Changes saved." : `Announcement saved.${saved.is_published ? " It is now live." : " It is saved as a draft."}` } });
  }

  if (loadError) {
    return <StateMessage kind={loadError.status === 404 ? "empty" : "error"} title={loadError.status === 404 ? "Announcement not found" : "We couldn't load this announcement"} message={loadError.message} action={<Link className="btn btn-secondary" to="/publisher">Back to your announcements</Link>} />;
  }
  if (!loaded) return <StateMessage kind="loading" title="Loading announcement" />;

  const errorList = Object.values(errors);
  const aria = (name) => ({ "aria-invalid": Boolean(errors[name]), "aria-describedby": errors[name] ? `${name}-error` : undefined });

  return (
    <section>
      <div className="page-head">
        <h1>{editing ? "Edit announcement" : "New announcement"}</h1>
      </div>

      {(message || errorList.length > 0) && (
        <div className="flash flash-error" role="alert">
          {message && <strong>{message}</strong>}
          {errorList.length > 0 && (
            <ul>
              {errorList.map((text, i) => (
                <li key={i}>{text}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      <form className="form-card" onSubmit={onSubmit} noValidate>
        <Field id="title" label="Title" error={errors.title}>
          <input id="title" type="text" maxLength={TITLE_MAX} value={values.title} onChange={set("title")} {...aria("title")} />
        </Field>
        <Field id="category" label="Category" error={errors.category}>
          <select id="category" value={values.category} onChange={set("category")} {...aria("category")}>
            <option value="">Choose a category</option>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </Field>
        <Field id="description" label="Description" error={errors.description}>
          <textarea id="description" rows={7} value={values.description} onChange={set("description")} {...aria("description")} />
        </Field>
        <div className="form-grid">
          <Field id="event_date" label="Event date (optional)" error={errors.event_date}>
            <input id="event_date" type="date" value={values.event_date} onChange={set("event_date")} {...aria("event_date")} />
          </Field>
          <Field id="event_time" label="Event time (optional)" error={errors.event_time}>
            <input id="event_time" type="time" value={values.event_time} onChange={set("event_time")} {...aria("event_time")} />
          </Field>
        </div>
        <Field id="venue" label="Venue (optional)" error={errors.venue}>
          <input id="venue" type="text" maxLength={VENUE_MAX} value={values.venue} onChange={set("venue")} {...aria("venue")} />
        </Field>
        <Field id="registration_link" label="Registration link (optional)" error={errors.registration_link} hint="Start with https://">
          <input id="registration_link" type="text" inputMode="url" value={values.registration_link} onChange={set("registration_link")} {...aria("registration_link")} />
        </Field>

        <fieldset className="form-fieldset">
          <legend>Attachments</legend>
          {["poster", "pdf"].map((kind) => (
            <AttachmentUploader
              key={kind}
              kind={kind}
              current={attachmentOf(kind)}
              file={files[kind]}
              remove={removed[kind]}
              onFile={(file) => setFiles((f) => ({ ...f, [kind]: file }))}
              onRemove={(flag) => setRemoved((r) => ({ ...r, [kind]: flag }))}
            />
          ))}
        </fieldset>

        <div className="form-row form-check">
          <input id="is_published" type="checkbox" checked={values.is_published} onChange={set("is_published")} />
          <label htmlFor="is_published">Publish now (students can see it straight away)</label>
        </div>

        <div className="form-actions">
          <button className="btn btn-primary" type="submit" disabled={busy}>
            {busy ? "Saving..." : editing ? "Save changes" : "Save announcement"}
          </button>
          <Link className="btn btn-secondary" to="/publisher">
            Cancel
          </Link>
        </div>
      </form>
    </section>
  );
}

// A fresh form for every announcement (and for "new"), so no old values or files carry over.
export default function AnnouncementFormPage() {
  const { id } = useParams();
  return <AnnouncementForm key={id || "new"} id={id} />;
}
