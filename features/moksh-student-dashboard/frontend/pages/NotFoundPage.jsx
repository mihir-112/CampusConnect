import { Link } from "react-router-dom";
import { usePageTitle } from "@/utils/usePageTitle";
import StateMessage from "../components/StateMessage";

export default function NotFoundPage() {
  usePageTitle("Page not found");
  return <StateMessage kind="empty" title="Page not found" message="We couldn't find that page. It may have been moved or removed." action={<Link className="btn btn-primary" to="/">Go to announcements</Link>} />;
}
