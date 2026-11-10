// Loading, empty and error boxes used on every page. Owner: Moksh.
export default function StateMessage({ kind = "empty", title, message, action }) {
  if (kind === "loading") {
    return (
      <div className="state state-loading" role="status" aria-live="polite">
        <div className="spinner" aria-hidden="true" />
        <p>{title || "Loading..."}</p>
      </div>
    );
  }
  return (
    <div className={`state ${kind === "error" ? "state-error" : ""}`} role={kind === "error" ? "alert" : undefined}>
      <h2>{title}</h2>
      {message && <p>{message}</p>}
      {action}
    </div>
  );
}
