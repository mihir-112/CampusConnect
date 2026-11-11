// Poster image and PDF viewer on the notice page. Owner: notice-details.
import { useState } from "react";
import { formatFileSize } from "@/utils/format";

function Unavailable({ what }) {
  return <p className="state-inline">The {what} is currently unavailable. Please contact the publisher.</p>;
}

function Poster({ attachment, title }) {
  const [broken, setBroken] = useState(false);
  return (
    <section className="attachment" aria-labelledby="poster-heading">
      <h2 id="poster-heading">Poster</h2>
      {attachment.available && !broken ? (
        <img className="poster" src={attachment.url} alt={`Poster for ${title}`} onError={() => setBroken(true)} />
      ) : (
        <Unavailable what="poster" />
      )}
    </section>
  );
}

function PdfNotice({ attachment, title }) {
  const [preview, setPreview] = useState(false);
  return (
    <section className="attachment" aria-labelledby="pdf-heading">
      <h2 id="pdf-heading">PDF notice</h2>
      {attachment.available ? (
        <>
          <p className="file-name">
            {attachment.original_filename} ({formatFileSize(attachment.size_bytes)})
          </p>
          <p className="attachment-actions">
            <button type="button" className="btn btn-secondary" aria-expanded={preview} onClick={() => setPreview((v) => !v)}>
              {preview ? "Hide preview" : "Preview PDF"}
            </button>
            <a className="btn btn-secondary" href={attachment.url} target="_blank" rel="noopener noreferrer">
              View PDF
            </a>
            <a className="btn btn-secondary" href={attachment.download_url} download>
              Download PDF
            </a>
          </p>
          {preview && <iframe className="pdf-frame" src={attachment.url} title={`PDF preview: ${title}`} />}
        </>
      ) : (
        <Unavailable what="PDF" />
      )}
    </section>
  );
}

export default function AttachmentSection({ attachments, title }) {
  const poster = attachments.find((a) => a.kind === "poster");
  const pdf = attachments.find((a) => a.kind === "pdf");
  return (
    <>
      {poster && <Poster attachment={poster} title={title} />}
      {pdf && <PdfNotice attachment={pdf} title={title} />}
    </>
  );
}
