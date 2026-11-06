"""Seed the CampusConnect database with realistic demo announcements, events, and attachments.
Can be run via: python -m scripts.seed_demo_data or python scripts/seed_demo_data.py
"""
import io
import sys
from datetime import date, time
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.core.config import load_settings
from backend.database import Database
from backend.shared.models import import_all_models
from features.publisher_auth.backend.models.publisher import Publisher
from features.publisher_auth.backend.services import auth_service
from features.core_announcement_engine.backend.models.announcement import Announcement
from features.core_announcement_engine.backend.schemas.announcement import AnnouncementCreate
from features.core_announcement_engine.backend.services import announcement_service
from features.notice_details.backend.services import attachment_service
import features.search_notifications.backend.services.notification_service  # registers event listener

# Sample 1x1 valid PNG bytes
SAMPLE_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    b"\x00\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xa76\x81\x04\x00\x00\x00\x00IEND\xaeB`\x82"
)

# Sample valid PDF bytes
SAMPLE_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
    b"xref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n"
    b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n188\n%%EOF"
)

DEMO_ANNOUNCEMENTS = [
    {
        "title": "End-Semester Examination Schedule — Winter 2026",
        "category": "Examinations",
        "description": "The final timetable for B.Tech, M.Tech, and MCA Winter 2026 examinations has been released by the Controller of Examinations. All students must check their respective branch schedules and report any clashes by November 15.",
        "is_published": True,
        "event_date": date(2026, 11, 20),
        "event_time": time(9, 30),
        "venue": "Main Academic Blocks A & B",
        "registration_link": None,
        "attachments": [("pdf", "Winter_2026_Exam_Timetable.pdf", SAMPLE_PDF)],
    },
    {
        "title": "HackCampus 2026: 36-Hour National Level Hackathon",
        "category": "Events",
        "description": "Join over 500 developers, designers, and innovators for the annual HackCampus Hackathon. Tracks include AI/ML, Web3, Smart Cities, and Open Innovation with an attractive cash prize pool of INR 2,50,000. Food and mentorship provided.",
        "is_published": True,
        "event_date": date(2026, 12, 5),
        "event_time": time(9, 0),
        "venue": "Main Campus Auditorium & Innovation Hub",
        "registration_link": "https://hackcampus2026.devpost.com",
        "attachments": [
            ("poster", "HackCampus_Poster.png", SAMPLE_PNG),
            ("pdf", "Hackathon_Rulebook_and_Guidelines.pdf", SAMPLE_PDF),
        ],
    },
    {
        "title": "Robotics & AI Society: Annual Induction & Hands-on Workshop",
        "category": "Clubs",
        "description": "Hands-on induction workshop covering ROS2, Computer Vision with OpenCV, and autonomous mobile robotics. Open to all engineering branches. No prior hardware experience required.",
        "is_published": True,
        "event_date": date(2026, 11, 18),
        "event_time": time(16, 30),
        "venue": "Mechanical Seminar Hall, Ground Floor",
        "registration_link": "https://forms.gle/robotics2026induction",
        "attachments": [("poster", "Robotics_Club_Induction.png", SAMPLE_PNG)],
    },
    {
        "title": "Central Library Extended Reading Room Hours for Exam Season",
        "category": "General",
        "description": "In view of upcoming mid-term evaluations and final project submissions, the Central Library reading halls will remain open until 11:00 PM on all weekdays and Saturdays. ID cards must be displayed at all times.",
        "is_published": True,
        "event_date": None,
        "event_time": None,
        "venue": "Central Library Complex, Floors 1 & 2",
        "registration_link": None,
        "attachments": [("pdf", "Library_Extended_Hours_Circular.pdf", SAMPLE_PDF)],
    },
    {
        "title": "ACM Student Chapter: Competitive Programming & DSA Bootcamp",
        "category": "Clubs",
        "description": "Four-week intensive sprint on Graph Algorithms, Dynamic Programming, and System Design led by senior alumni from top tech firms. Weekly contests on Codeforces with detailed editorial discussions.",
        "is_published": True,
        "event_date": date(2026, 11, 25),
        "event_time": time(17, 0),
        "venue": "Computer Center Lab 3",
        "registration_link": "https://campusconnect.acm.org/bootcamp",
        "attachments": [],
    },
    {
        "title": "Supplementary & Backlog Examination Form Submission",
        "category": "Examinations",
        "description": "Eligible students must submit their backlog examination registration forms along with fee challan receipts to the Dean of Academic Affairs before November 12, 5:00 PM. Late forms will not be accepted.",
        "is_published": True,
        "event_date": date(2026, 11, 12),
        "event_time": time(17, 0),
        "venue": "Examination Cell, Admin Block, Room 104",
        "registration_link": None,
        "attachments": [("pdf", "Backlog_Registration_Form_Instructions.pdf", SAMPLE_PDF)],
    },
    {
        "title": "Annual Inter-College Cultural Fest: 'Sanskriti 2026'",
        "category": "Events",
        "description": "Registrations are now open for music, dance, theater, and fine arts competitions. Grand celebrity night passes will be issued to college students next week. College ID card mandatory.",
        "is_published": True,
        "event_date": date(2026, 12, 18),
        "event_time": time(10, 0),
        "venue": "Open Air Amphitheatre",
        "registration_link": "https://sanskriti2026.in",
        "attachments": [("poster", "Sanskriti_Fest_Banner.png", SAMPLE_PNG)],
    },
    {
        "title": "Upcoming Campus Recruitment Drives: Eligibility & Registration (Draft)",
        "category": "General",
        "description": "Notice for final year students regarding Tier-1 IT services and product company visit schedules. Resume submission portal opens next Monday.",
        "is_published": False,  # Draft: only visible in Publisher Dashboard
        "event_date": None,
        "event_time": None,
        "venue": "Placement Cell, Admin Block",
        "registration_link": None,
        "attachments": [],
    },
]


def seed_database():
    import_all_models()
    settings = load_settings()
    db_manager = Database(settings.database_url)
    db_manager.create_tables()

    with db_manager.session_factory() as db:
        # 1. Ensure publisher exists
        pub = db.query(Publisher).filter_by(username="editor").first()
        if not pub:
            pub = auth_service.create_publisher(db, "editor", "editor@example.com", "password123")
            print("[+] Created publisher: editor (password123)")
        else:
            print("[*] Found existing publisher: editor")

        # 2. Check existing announcements
        existing_count = db.query(Announcement).count()
        if existing_count > 1:
            print(f"[*] Database already contains {existing_count} announcements. Skipping duplicate seed.")
            return

        # 3. Create demo announcements
        print(f"[*] Seeding {len(DEMO_ANNOUNCEMENTS)} demo announcements...")
        for item in DEMO_ANNOUNCEMENTS:
            attachments = item.pop("attachments", [])
            payload = AnnouncementCreate(**item)
            announcement = announcement_service.create(db, pub, payload, settings)
            status_label = "PUBLISHED" if announcement.is_published else "DRAFT"
            print(f"  -> Created [{status_label}] #{announcement.id}: {announcement.title}")

            # Attach sample poster or PDF
            for kind, filename, content in attachments:
                att = attachment_service.save_attachment(
                    db, settings, announcement, kind, filename, io.BytesIO(content)
                )
                print(f"     + Attached {kind.upper()}: {filename} (#{att.id})")

    db_manager.dispose()
    print("\n[SUCCESS] CampusConnect demo database seeded successfully!")


if __name__ == "__main__":
    seed_database()
