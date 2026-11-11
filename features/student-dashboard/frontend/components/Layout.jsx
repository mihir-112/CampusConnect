// Header, navigation, footer. Owner: student-dashboard.
import { useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "@features/publisher-auth/frontend/auth/AuthContext";
import NotificationBell from "@features/search-notifications/frontend/components/NotificationBell";
import SearchBar from "@features/search-notifications/frontend/components/SearchBar";

export default function Layout() {
  const { status, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const close = () => setMenuOpen(false);

  const headerSearchVal = location.pathname === "/" ? searchParams.get("q") || "" : "";

  function onHeaderSearch(query) {
    const next = new URLSearchParams(location.pathname === "/" ? searchParams : "");
    if (query) next.set("q", query);
    else next.delete("q");
    next.delete("page");
    const qs = next.toString();
    navigate(qs ? `/?${qs}` : "/");
  }

  async function onLogout() {
    close();
    await logout();
    navigate("/");
  }

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <div className="header-container">
          <div className="header-brand-wrap">
            <Link className="brand" to="/" onClick={close}>
              <img src="/nie-logo.png" alt="NIE Crest" className="brand-nie-logo" />
              <div className="brand-text">
                <span className="brand-name">CampusConnect</span>
                <span className="brand-tag">Your campus. One place.</span>
              </div>
            </Link>
          </div>

          <nav className="header-center-nav" aria-label="Quick Links">
            <NavLink to="/" end onClick={close} className={({ isActive }) => `header-nav-link ${isActive && !searchParams.get("category") ? "active" : ""}`}>
              Home
            </NavLink>
            <NavLink to="/?category=Events" onClick={close} className={() => `header-nav-link ${searchParams.get("category") === "Events" ? "active" : ""}`}>
              Events
            </NavLink>
            <NavLink to="/?category=Examinations" onClick={close} className={() => `header-nav-link ${searchParams.get("category") === "Examinations" ? "active" : ""}`}>
              Notices
            </NavLink>
            <NavLink to="/?category=Clubs" onClick={close} className={() => `header-nav-link ${searchParams.get("category") === "Clubs" ? "active" : ""}`}>
              Clubs
            </NavLink>
          </nav>

          <div className="header-right-actions">
            <div className="header-search-wrap">
              <SearchBar value={headerSearchVal} onSearch={onHeaderSearch} />
            </div>

            <NotificationBell />

            <button type="button" className="nav-toggle" aria-expanded={menuOpen} aria-controls="site-nav" onClick={() => setMenuOpen((v) => !v)}>
              <span className="visually-hidden">Menu</span>
              <svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </button>

            <nav id="site-nav" className={`site-nav ${menuOpen ? "open" : ""}`} aria-label="Main">
              {status === "authenticated" ? (
                <>
                  <NavLink to="/publisher" className="nav-link-auth" onClick={close}>
                    Manage
                  </NavLink>
                  <button type="button" className="nav-button" onClick={onLogout}>
                    Log out
                  </button>
                </>
              ) : (
                <NavLink to="/publisher/login" className="nav-link-auth" onClick={close}>
                  Publisher login
                </NavLink>
              )}
            </nav>

            <Link
              to={status === "authenticated" ? "/publisher" : "/publisher/login"}
              className="header-profile-avatar"
              title={status === "authenticated" ? "Publisher Portal" : "Publisher Login"}
              aria-label="Publisher Portal"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
              </svg>
            </Link>
          </div>
        </div>
      </header>

      <main id="main" className="site-main">
        <Outlet />
      </main>

      <footer className="site-footer">
        <div className="container footer-content">
          <span>CampusConnect &middot; Announcements from across campus, in one place.</span>
        </div>
      </footer>
    </>
  );
}
