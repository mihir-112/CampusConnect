import { Component } from "react";

/** Catches an unexpected crash in any page so the visitor sees a message instead of a blank screen. */
export default class ErrorBoundary extends Component {
  state = { failed: false };

  static getDerivedStateFromError() {
    return { failed: true };
  }

  componentDidCatch(error) {
    console.error(error);
  }

  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <div className="state state-error" role="alert">
        <h2>Something went wrong</h2>
        <p>An unexpected error occurred. Refresh the page to try again.</p>
        <button type="button" className="btn btn-primary" onClick={() => window.location.reload()}>
          Refresh the page
        </button>
      </div>
    );
  }
}
