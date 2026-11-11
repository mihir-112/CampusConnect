// File picker used inside the publisher's announcement form. Owner: notice-details.
//
// Integration contract (used by members/mihir/frontend/pages/AnnouncementFormPage.jsx):
//   <AttachmentUploader kind="poster" current={attachment|undefined} file={File|null} remove={bool}
//                       onFile={(File|null) => ...} onRemove={(bool) => ...} />
// Nothing is uploaded here; the form uploads after the announcement itself is saved.
import { useState } from "react";
import { checkFile, FILE_RULES } from "../fileRules";

export default function AttachmentUploader({ kind, current, file, remove, onFile, onRemove }) {
  const rules = FILE_RULES[kind];
  const [error, setError] = useState("");
  const id = `upload-${kind}`;

  function onChange(event) {
    const chosen = event.target.files?.[0] || null;
    if (!chosen) {
      setError("");
      onFile(null);
      return;
    }
    const problem = checkFile(kind, chosen);
    setError(problem);
    if (problem) {
      event.target.value = "";
      onFile(null);
    } else {
      onFile(chosen);
      onRemove(false);
    }
  }

  return (
    <div className="form-row">
      <label htmlFor={id}>{rules.label}</label>
      {current && (
        <p className="current-file">
          Current {rules.label.toLowerCase()}: {current.original_filename}
          {current.available === false && " (file missing on the server)"}
        </p>
      )}
      {current && (
        <p className="form-check">
          <input id={`${id}-remove`} type="checkbox" checked={remove} onChange={(e) => onRemove(e.target.checked)} disabled={Boolean(file)} />
          <label htmlFor={`${id}-remove`}>Remove current {rules.label.toLowerCase()}</label>
        </p>
      )}
      <input id={id} type="file" accept={rules.accept} onChange={onChange} aria-invalid={Boolean(error)} aria-describedby={`${id}-hint`} />
      <p className="hint" id={`${id}-hint`}>
        {current ? "Uploading a new file replaces the current one. " : ""}
        {rules.extensions.join(", ")} up to {rules.maxBytes / (1024 * 1024)} MB.
      </p>
      {error && (
        <p className="field-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
