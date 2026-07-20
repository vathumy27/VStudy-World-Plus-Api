"""Seeder to import Grade 10/11 lessons from official e-Thaksalawa."""

from __future__ import annotations

import html
import re
import urllib.request
from dataclasses import dataclass
from typing import Any

from app.extensions import db
from app.models.lesson import Lesson
from app.models.subject import Subject

BASE = "https://e-thaksalawa.moe.gov.lk/lcms"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

COURSES = {
    10: {
        "Mathematics": 842,
        "Science": 844,
        "History": 846,
        "Geography": 863,
    },
    11: {
        "Mathematics": 799,
        "Science": 800,
        "History": 802,
        "Geography": 805,
    },
}

SUBJECT_DESCRIPTIONS = {
    "History": "Grade 10 and 11 History content from e-Thaksalawa.",
    "Geography": "Grade 10 and 11 Geography content from e-Thaksalawa.",
    "Mathematics": "Grade 10 and 11 Mathematics content from e-Thaksalawa.",
    "Science": "Grade 10 and 11 Science content from e-Thaksalawa.",
}


@dataclass
class ResourceLink:
    title: str
    url: str
    kind: str


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=12) as response:
        return response.read().decode("utf-8", errors="ignore")


def _clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(" ".join(text.split()))
    return text.strip()


def _kind_from_resource(title: str, url: str) -> str:
    t = title.lower()
    u = url.lower()
    if "youtube" in u or "vimeo" in u or "video" in t:
        return "video"
    if u.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")) or "image" in t:
        return "image"
    if u.endswith(".pdf") or "pdf" in t or "syllabus" in t or "teacher" in t:
        return "pdf"
    if "download" in t or "redirect=1" in u:
        return "download"
    return "resource"


def _extract_section_links(course_html: str) -> list[tuple[str, str]]:
    pattern = re.compile(
        r"<a[^>]+href=\"(https://e-thaksalawa\.moe\.gov\.lk/lcms/course/section\.php\?id=\d+[^\"]*)\"[^>]*>(.*?)</a>",
        re.IGNORECASE | re.DOTALL,
    )
    seen = set()
    sections: list[tuple[str, str]] = []
    for href, label_html in pattern.findall(course_html):
        label = _clean_text(label_html)
        if not label:
            continue
        key = href.split("&")[0]
        if key in seen:
            continue
        seen.add(key)
        sections.append((label, href))
    return sections


def _extract_resources(section_html: str) -> list[ResourceLink]:
    pattern = re.compile(r"<a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)
    resources: list[ResourceLink] = []
    seen = set()

    for href, title_html in pattern.findall(section_html):
        if not href.startswith("http"):
            continue
        if "e-thaksalawa.moe.gov.lk/lcms/mod/" not in href and "pluginfile.php" not in href:
            continue

        title = _clean_text(title_html)
        if not title:
            continue

        key = (href, title)
        if key in seen:
            continue
        seen.add(key)

        kind = _kind_from_resource(title, href)
        resources.append(ResourceLink(title=title, url=href, kind=kind))

    return resources


def _extract_unit_number(section_title: str) -> str | None:
    match = re.match(r"^\s*(\d+(?:\.\d+)?)", section_title)
    return match.group(1) if match else None


def _ensure_subject(name: str) -> Subject:
    subject = Subject.query.filter(Subject.name.ilike(name)).first()
    if subject:
        return subject
    subject = Subject(
        name=name,
        description=SUBJECT_DESCRIPTIONS.get(name),
        image=None,
    )
    db.session.add(subject)
    db.session.flush()
    return subject


def import_ethaksalawa_grade_10_11() -> dict[str, Any]:
    summary = {
        "subjects_created": 0,
        "lessons_created": 0,
        "lessons_updated": 0,
        "courses_processed": 0,
        "errors": [],
    }

    created_subject_ids = set()

    for grade, subject_map in COURSES.items():
        for subject_name, course_id in subject_map.items():
            summary["courses_processed"] += 1

            subject = _ensure_subject(subject_name)
            if subject.id not in created_subject_ids:
                created_subject_ids.add(subject.id)
                if subject.description == SUBJECT_DESCRIPTIONS.get(subject_name):
                    summary["subjects_created"] += 1

            course_url = f"{BASE}/course/view.php?id={course_id}&lang=en"
            try:
                course_html = _fetch(course_url)
                sections = _extract_section_links(course_html)
            except Exception as exc:  # pragma: no cover
                summary["errors"].append(f"course {course_id}: {exc}")
                continue

            for idx, (section_title, section_url) in enumerate(sections, start=1):
                if section_title.lower() in {"general", "announcements forum"}:
                    continue

                unit_number = _extract_unit_number(section_title)
                try:
                    section_html = _fetch(section_url + "&lang=en")
                    resources = _extract_resources(section_html)
                    if idx % 10 == 0:
                        print(f"[seed][course {course_id}] processed section {idx}/{len(sections)}")
                except Exception as exc:  # pragma: no cover
                    summary["errors"].append(f"section {section_url}: {exc}")
                    resources = []

                pdf_url = next((r.url for r in resources if r.kind == "pdf"), None)
                video_url = next((r.url for r in resources if r.kind == "video"), None)
                image_url = next((r.url for r in resources if r.kind == "image"), None)
                download_url = next((r.url for r in resources if r.kind == "download"), None)
                resource_url = next((r.url for r in resources if r.kind == "resource"), None)

                lesson = (
                    Lesson.query.filter_by(
                        subject_id=subject.id,
                        grade=grade,
                        title=section_title,
                        source_url=section_url,
                    ).first()
                )

                resource_payload = [
                    {"title": r.title, "url": r.url, "type": r.kind} for r in resources
                ]

                if lesson:
                    lesson.unit_number = unit_number
                    lesson.language = "English"
                    lesson.description = lesson.description or (
                        f"Official e-Thaksalawa Grade {grade} {subject_name} learning resources for {section_title}."
                    )
                    lesson.video_url = video_url or lesson.video_url
                    lesson.pdf_url = pdf_url or lesson.pdf_url
                    lesson.image_url = image_url or lesson.image_url
                    lesson.download_url = download_url or lesson.download_url
                    lesson.resource_url = resource_url or lesson.resource_url
                    lesson.source_provider = "e-thaksalawa"
                    lesson.resource_links = resource_payload
                    if not lesson.content:
                        lesson.content = (
                            f"Official e-Thaksalawa section: {section_title}. "
                            f"Use the linked resources (PDF/Video/Notes) for learning."
                        )
                    summary["lessons_updated"] += 1
                else:
                    lesson = Lesson(
                        subject_id=subject.id,
                        title=section_title,
                        description=(
                            f"Official e-Thaksalawa Grade {grade} {subject_name} learning resources for {section_title}."
                        ),
                        content=(
                            f"Official e-Thaksalawa section: {section_title}. "
                            "Use the linked resources (PDF/Video/Notes) for learning."
                        ),
                        summary=None,
                        video_url=video_url,
                        grade=grade,
                        unit_number=unit_number,
                        language="English",
                        pdf_url=pdf_url,
                        image_url=image_url,
                        resource_url=resource_url,
                        download_url=download_url,
                        source_url=section_url,
                        source_provider="e-thaksalawa",
                        resource_links=resource_payload,
                    )
                    db.session.add(lesson)
                    summary["lessons_created"] += 1

    db.session.commit()
    return summary
