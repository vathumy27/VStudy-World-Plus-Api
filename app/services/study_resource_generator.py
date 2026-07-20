"""
Original AI study note generator for Sri Lankan O/L (Grade 10–11).

Notes are generated in simple Tamil suitable for students.
Uses lesson titles / syllabus topics as reference only.
Does NOT copy e-Thaksalawa or any third-party website content.
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.utils.openai_client import OpenAIClient
from app.utils.search_utils import expand_query_terms


SYSTEM_PROMPT = (
    "நீங்கள் இலங்கை O/L (தரம் 10, 11) மாணவர்களுக்கான கல்வி உள்ளடக்க ஆசிரியர். "
    "எளிய தமிழில் அசல் படிப்புக் குறிப்புகளை எழுதுங்கள். "
    "எந்த இணையதளம்/பாடநூலையும் அப்படியே நகலெடுக்க வேண்டாம். "
    "ONLY valid JSON திருப்புங்கள். All string values MUST be in Tamil "
    "(formulae expressions may stay in Latin symbols)."
)

SUBJECT_TA = {
    "history": "வரலாறு",
    "geography": "புவியியல்",
    "science": "விஞ்ஞானம்",
    "mathematics": "கணிதம்",
    "maths": "கணிதம்",
    "math": "கணிதம்",
}


def _subject_ta(subject_name: str) -> str:
    key = (subject_name or "").strip().lower()
    for eng, ta in SUBJECT_TA.items():
        if eng in key:
            return ta
    return subject_name or "பாடம்"


def _slug_keywords(title: str) -> list[str]:
    terms = expand_query_terms(title)
    # Keep bilingual keywords for search
    out: list[str] = []
    for t in terms:
        if t not in out:
            out.append(t)
        if len(out) >= 12:
            break
    if not out:
        out = ["பாடம்", "O/L"]
    return out


def _tamil_title(title: str, subject_ta: str) -> str:
    """Prefer a readable Tamil display title; keep original topic if already Tamil."""
    topic = (title or "").strip()
    if re.search(r"[\u0B80-\u0BFF]", topic):
        return topic[:240]
    return f"{subject_ta}: {topic}"[:240]


def _build_mock_notes(
    *,
    title: str,
    subject_name: str,
    grade: int,
    unit_number: str | None,
) -> dict[str, Any]:
    """Deterministic original Tamil notes from topic metadata."""
    subject_key = (subject_name or "").strip().lower()
    subject_ta = _subject_ta(subject_name)
    topic = title.strip() or "இந்தத் தலைப்பு"
    unit = unit_number or "—"
    keywords = _slug_keywords(topic)
    display_title = _tamil_title(topic, subject_ta)

    short_notes = (
        f"「{topic}」 என்பது தரம் {grade} {subject_ta} பாடத்தின் முக்கியப் பகுதி "
        f"(அலகு {unit}). முதலில் அடிப்படைக் கருத்தைப் புரிந்துகொள்ளுங்கள். "
        f"பின்னர் முக்கியப் புள்ளிகள், எளிய விளக்கம், திருத்தக் குறிப்புகளைப் "
        f"பயன்படுத்தி தேர்வுக்குத் தயாராகுங்கள்."
    )

    easy_explanation = (
        f"எளிய விளக்கம்: {topic} பற்றி சிந்திக்கும்போது "
        f"‘இது என்ன?’, ‘ஏன் முக்கியம்?’, ‘ஒரு உதாரணம் என்ன?’ "
        f"என்ற மூன்று கேள்விகளுக்குப் பதில் சொல்லுங்கள். "
        f"வகுப்பறையில் கற்றதை அன்றாட வாழ்க்கையுடன் இணைத்து நினைவில் வையுங்கள்."
    )

    key_points = [
        f"「{topic}」-இன் மையக் கருத்தைத் தெளிவாகப் புரிந்துகொள்ளுங்கள்.",
        f"{subject_ta} பாடத்திற்கான முக்கியச் சொற்களை மனப்பாடம் செய்யுங்கள்.",
        "காரணம் → நிகழ்வு → விளைவு என வரிசைப்படுத்தி எழுதுங்கள்.",
        "வரைபடம் / காலவரிசை / அட்டவணை உதவினால் பயன்படுத்துங்கள்.",
        "தேர்வுக்கு முன் குறுகிய திருத்தக் குறிப்புகளை மட்டும் படியுங்கள்.",
    ]

    definitions = [
        {
            "term": topic.split(":")[-1].strip()[:80] or topic[:80],
            "meaning": (
                f"தரம் {grade} {subject_ta} பாடத்தில் இந்தத் தலைப்பின் முக்கியக் கருத்து. "
                "உங்கள் சொந்த வார்த்தைகளில் வரையறுக்கத் தயாராகுங்கள்."
            ),
        },
        {
            "term": "திருத்தக் குறிப்பு",
            "meaning": "தேர்வில் நினைவில் வைக்க வேண்டிய குறுகிய முக்கியத் தகவல்.",
        },
    ]

    dates: list[dict[str, str]] = []
    maps_locations: list[dict[str, str]] = []
    scientific_concepts: list[dict[str, str]] = []
    formulae: list[dict[str, str]] = []

    if "history" in subject_key:
        dates = [
            {
                "label": "முக்கியக் காலம்",
                "detail": (
                    f"「{topic}」-ஐ காலவரிசையில் வையுங்கள்: "
                    "முன் நிலை → நிகழ்வு → விளைவு. வகுப்பில் சொன்ன ஆண்டுகளை நினைவில் வையுங்கள்."
                ),
            },
            {
                "label": "தேர்வு கவனம்",
                "detail": "ஆண்டுகளை நபர்கள், இடங்கள், விளைவுகளுடன் இணைத்து எழுதுங்கள்.",
            },
        ]
        key_points.insert(1, "காலவரிசை உருவாக்குங்கள்: முன், நடு, பின்.")
    elif "geography" in subject_key:
        maps_locations = [
            {
                "name": "படிப்பு வரைபடம்",
                "detail": (
                    f"「{topic}」 தொடர்பான இடங்களை இலங்கை/உலக வரைபடத்தில் கண்டுபிடியுங்கள். "
                    "காலநிலை அல்லது நிலத்தோற்றத் தொடர்பைக் குறிப்பிடுங்கள்."
                ),
            },
            {
                "name": "உள்ளூர் தொடர்பு",
                "detail": "உங்கள் பகுதியில் காணும் எடுத்துக்காட்டுடன் இணைத்து நினைவில் வையுங்கள்.",
            },
        ]
        key_points.insert(1, "வரைபடம் படித்தல் மற்றும் பெயரிடல் பயிற்சி செய்யுங்கள்.")
    elif "science" in subject_key:
        scientific_concepts = [
            {
                "concept": topic[:100],
                "explanation": (
                    "கருத்தைத் தெளிவாகச் சொல்லுங்கள். பின்னர் ஒரு அன்றாட உதாரணம் "
                    "மற்றும் ஒரு வகுப்பறை/ஆய்வக உதாரணம் கொடுங்கள்."
                ),
            },
            {
                "concept": "காரணம்–விளைவு",
                "explanation": "என்ன நடக்கிறது, ஏன் நடக்கிறது என விளக்குங்கள்.",
            },
        ]
        formulae = [
            {
                "name": "பொதுத் தொடர்பு",
                "expression": "விளைவு ∝ தொடர்புடைய காரணிகள்",
                "note": "பாடநூலில் உள்ள சரியான சூத்திரத்தைப் பயன்படுத்துங்கள்.",
            }
        ]
        key_points.insert(1, "வரையறை, அலகுகள், ஒரு வேலை உதாரணம் தெரிந்திருக்க வேண்டும்.")

    summary = (
        f"தரம் {grade} {subject_ta} பாடத்தில் 「{topic}」-ஐ "
        f"வரையறை → முக்கியப் புள்ளிகள் → உதாரணம் → தேர்வு விடை எனத் திருத்துங்கள். "
        f"முக்கியச் சொற்கள்: {', '.join(keywords[:6])}."
    )

    exam_tips = [
        "கேள்வியை நன்றாகப் படித்து கட்டளைச் சொற்களை (வரையறு, விளக்கு, ஒப்பிடு) அடிக்கோடிடுங்கள்.",
        "குறுகிய தெளிவான வாக்கியங்களில் எழுதுங்கள்; தேவையானால் வரைபடம் வரையுங்கள்.",
        "எளிய கேள்விகளுக்கு முதலில் விடையளித்து நேரத்தைச் சேமியுங்கள்.",
        f"「{topic}」 பற்றி 5–6 வரி விடையைப் பயிற்சி செய்யுங்கள்.",
    ]

    study_tips = [
        "தினம் 15 நிமிடம் குறுகிய திருத்தம் செய்யுங்கள்.",
        "நண்பருக்கு 1 நிமிடத்தில் விளக்க முயலுங்கள்.",
        "தவறான விடைகளைத் தனியே குறித்து மீண்டும் படியுங்கள்.",
    ]

    important_questions = [
        f"「{topic}」 என்றால் என்ன? சுருக்கமாக வரையறுக்கவும்.",
        f"「{topic}」-இன் இரண்டு முக்கிய அம்சங்களை விளக்கவும்.",
        f"「{topic}」 தொடர்பான ஒரு உதாரணம் தந்து விளக்கவும்.",
        "இந்தத் தலைப்பு தேர்வில் எவ்வாறு கேட்கப்படலாம்?",
    ]

    revision_notes = (
        f"• தலைப்பு: {topic}\n"
        f"• தரம் / பாடம் / அலகு: {grade} / {subject_ta} / {unit}\n"
        f"• நினைவில் வைக்க: வரையறை + 3 முக்கிய உண்மைகள் + 1 உதாரணம்\n"
        f"• சுய சோதனை: 1 நிமிடத்தில் விளக்க முடிகிறதா?\n"
        f"• முக்கியச் சொற்கள்: {', '.join(keywords[:8])}"
    )

    resource_links = [
        {
            "label": "பாடக் குறிப்புகள்",
            "url": "",
            "note": "VStudy Plus-இல் உள்ள AI குறுகிய குறிப்புகளையும் திருத்தக் குறிப்புகளையும் பயன்படுத்துங்கள்.",
        },
        {
            "label": "தேர்வுப் பயிற்சி",
            "url": "",
            "note": "முக்கிய வினாக்களுக்குச் சுருக்கமான விடைகளை எழுதிப் பழகுங்கள்.",
        },
    ]

    return {
        "title": display_title,
        "short_notes": short_notes,
        "easy_explanation": easy_explanation,
        "key_points": key_points,
        "definitions": definitions,
        "dates": dates,
        "maps_locations": maps_locations,
        "scientific_concepts": scientific_concepts,
        "formulae": formulae,
        "summary": summary,
        "exam_tips": exam_tips,
        "study_tips": study_tips,
        "important_questions": important_questions,
        "revision_notes": revision_notes,
        "keywords": keywords,
        "resource_links": resource_links,
        "language": "Tamil",
        "generated_by": "vstudy_ai_template_ta",
    }


def _parse_json_payload(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except json.JSONDecodeError:
        return None


def generate_lesson_notes(
    *,
    title: str,
    subject_name: str,
    grade: int,
    unit_number: str | None = None,
) -> dict[str, Any]:
    """Generate original structured Tamil study notes for one lesson topic."""
    mock = _build_mock_notes(
        title=title,
        subject_name=subject_name,
        grade=grade,
        unit_number=unit_number,
    )

    prompt = (
        f"Create original O/L study notes in SIMPLE TAMIL as JSON for:\n"
        f"Title: {title}\n"
        f"Subject: {subject_name}\n"
        f"Grade: {grade}\n"
        f"Unit: {unit_number or 'N/A'}\n\n"
        "JSON keys required (all Tamil strings):\n"
        "title, short_notes, easy_explanation,\n"
        "key_points (array of strings),\n"
        "definitions (array of {term, meaning}),\n"
        "dates (array of {label, detail}) — History only, else [],\n"
        "maps_locations (array of {name, detail}) — Geography only, else [],\n"
        "scientific_concepts (array of {concept, explanation}) — Science only, else [],\n"
        "formulae (array of {name, expression, note}),\n"
        "summary (string),\n"
        "exam_tips (array of strings),\n"
        "study_tips (array of strings),\n"
        "important_questions (array of strings),\n"
        "revision_notes (string),\n"
        "keywords (array of strings, include Tamil + English search terms)."
    )

    raw = OpenAIClient.generate_text(
        prompt,
        system_message=SYSTEM_PROMPT,
        max_tokens=1600,
    )
    parsed = _parse_json_payload(raw)
    if not parsed:
        return mock

    for key in mock:
        if key == "generated_by":
            continue
        if key in parsed and parsed[key] not in (None, "", []):
            mock[key] = parsed[key]
    mock["language"] = "Tamil"
    mock["generated_by"] = "vstudy_ai_openai_ta"
    return mock


def build_math_resources(grade: int) -> list[dict[str, Any]]:
    """Subject-level Mathematics resources only (Tamil)."""
    return [
        {
            "title": f"தரம் {grade} கணிதம் – சூத்திர அட்டை",
            "resource_type": "formula_sheet",
            "short_notes": (
                f"தரம் {grade} கணிதத்திற்கான சுத்தமான சூத்திர அட்டையை வைத்திருங்கள்: "
                "இயற்கணிதம், வடிவியல், அளவியல், புள்ளியியல். ஒவ்வொரு சூத்திரத்தையும், "
                "குறியீடுகளின் பொருளையும், ஒரு உதாரணத்தையும் எழுதுங்கள்."
            ),
            "easy_explanation": (
                "சூத்திரத்தை மனப்பாடம் செய்வதற்கு முன் அது எதைக் கணக்கிடுகிறது எனப் புரிந்துகொள்ளுங்கள்."
            ),
            "key_points": [
                "அத்தியாய வாரியாக சூத்திரங்களைப் பிரியுங்கள்.",
                "அலகுகளையும் பொதுவான தவறுகளையும் குறிக்கவும்.",
                "மதிப்புகளை மாற்றும்போது கவனமாக இருங்கள்.",
            ],
            "definitions": [],
            "dates": [],
            "maps_locations": [],
            "scientific_concepts": [],
            "formulae": [
                {
                    "name": "செவ்வகப் பரப்பளவு",
                    "expression": "A = l × w",
                    "note": "நீளம் × அகலம்",
                },
                {
                    "name": "முக்கோணப் பரப்பளவு",
                    "expression": "A = ½ × b × h",
                    "note": "அடிப்பக்கம் × செங்குத்து உயரம்",
                },
                {
                    "name": "பைதகரஸ்",
                    "expression": "a² + b² = c²",
                    "note": "செங்கோண முக்கோணங்கள்",
                },
                {
                    "name": "எளிய வட்டி",
                    "expression": "I = (P × R × T) / 100",
                    "note": "பாடத்திட்ட அலகில் கற்றபடி",
                },
            ],
            "summary": (
                f"தரம் {grade} கணித வெற்றிக்கு சூத்திர அறிவும் படிப்படியான பயிற்சியும் அவசியம்."
            ),
            "exam_tips": [
                "அனைத்து படிகளையும் காட்டுங்கள்; முறைக்கு மதிப்பெண்கள் உண்டு.",
                "அலகுகளையும் இறுதி விடையின் நியாயத்தையும் சரிபாருங்கள்.",
                "வடிவியல் கேள்விகளுக்கு அழகாக வரைபடம் வரையுங்கள்.",
            ],
            "study_tips": [
                "வாரந்தோறும் முக்கியச் சூத்திரங்களை மீண்டும் எழுதுங்கள்.",
                "தவறுகளின் பட்டியலை வைத்திருங்கள்.",
            ],
            "important_questions": [
                "இந்தச் சூத்திரம் எப்போது பயன்படும்?",
                "குறியீடுகள் எதைக் குறிக்கின்றன?",
            ],
            "revision_notes": (
                f"• தரம் {grade} முக்கியச் சூத்திரங்களை வாரந்தோறும் மனப்பாடம்\n"
                "• பாடநூல் உதாரணங்களைப் பார்க்காமல் மீண்டும் செய்யுங்கள்\n"
                "• இயற்கணிதத் தவறுகளைக் குறித்து வையுங்கள்"
            ),
            "keywords": [
                "சூத்திரம்",
                "formulae",
                "algebra",
                "geometry",
                "கணிதம்",
                f"grade{grade}",
            ],
            "resource_links": [
                {
                    "label": "பாடநூல் பயிற்சி",
                    "url": "",
                    "note": "உங்கள் பள்ளி பாடநூல் பயிற்சிகளைப் பயன்படுத்துங்கள்.",
                }
            ],
            "language": "Tamil",
            "generated_by": "vstudy_ai_template_ta",
        },
        {
            "title": f"தரம் {grade} கணிதம் – பாடநூல் & படிப்புப் பொருட்கள்",
            "resource_type": "textbook",
            "short_notes": (
                f"தரம் {grade} கணிதப் பாடநூலை முதன்மை ஆதாரமாகப் பயன்படுத்துங்கள். "
                "வேலை உதாரணங்களும் தினசரி குறுகிய பயிற்சியும் சேர்த்துக் கொள்ளுங்கள்."
            ),
            "easy_explanation": (
                "ஒவ்வொரு அத்தியாயத்திலும்: எடுத்துக்காட்டு → பயிற்சி → தவறு திருத்தம்."
            ),
            "key_points": [
                "அத்தியாய இறுதிப் பயிற்சிகளை முடியுங்கள்.",
                "கடினக் கேள்விகளை மீண்டும் முயலக் குறிக்கவும்.",
                "வாரப் பயிற்சி அட்டவணை உருவாக்குங்கள்.",
            ],
            "definitions": [],
            "dates": [],
            "maps_locations": [],
            "scientific_concepts": [],
            "formulae": [],
            "summary": (
                "VStudy Plus-இல் கணிதத்திற்கு பாடநூல் மற்றும் பயிற்சி வளங்களே முதன்மை — "
                "பாடம் வாரியான கட்டுரைக் குறிப்புகள் அல்ல."
            ),
            "exam_tips": [
                "கலப்புத் தலைப்புத் தாள்களில் நேரத்தை அளந்து பயிலுங்கள்.",
                "பலவீன அத்தியாயங்களைத் தேர்வுக்கு முன் இருமுறை திருத்துங்கள்.",
            ],
            "study_tips": [
                "குறிப்பேடு, சூத்திர அட்டை, முன் தாள்கள் தயாராக வைத்திருங்கள்.",
            ],
            "important_questions": [
                "இந்த அத்தியாயத்தின் 5 முக்கியப் பயிற்சிகள் யாவை?",
            ],
            "revision_notes": (
                "• பாடநூல் → உதாரணம் → பயிற்சி → முன் தாள்\n"
                "• முறை மதிப்பெண்கள் மற்றும் அழகான அமைப்பில் கவனம்"
            ),
            "keywords": ["பாடநூல்", "textbook", "practice", "கணிதம்", f"grade{grade}"],
            "resource_links": [
                {
                    "label": "படிப்புப் பொருள் பட்டியல்",
                    "url": "",
                    "note": "குறிப்பேடு, சூத்திர அட்டை, முன் தாள்கள்.",
                }
            ],
            "language": "Tamil",
            "generated_by": "vstudy_ai_template_ta",
        },
        {
            "title": f"தரம் {grade} கணிதம் – பயிற்சி & திருத்தத் தொகுப்பு",
            "resource_type": "practice",
            "short_notes": (
                "குறுகிய பயிற்சி (10–15 நிமிடம்) மற்றும் வாராந்திர நீண்ட தாள்களைக் கலக்குங்கள். "
                "தலைப்பு வாரியாகத் துல்லியத்தைக் கண்காணிக்கவும்."
            ),
            "easy_explanation": (
                "தினம் சிறிய பயிற்சி + வாரம் ஒரு நேர அளவுப் பகுதி = தேர்வுத் தயாரிப்பு."
            ),
            "key_points": [
                "இயற்கணிதம் மற்றும் வடிவியல் நாட்களை மாற்றிப் பயிலுங்கள்.",
                "தவறுகளை அதே நாளில் திருத்துங்கள்.",
                "முன் தாள் பாணியில் கேள்விகளைப் பயிலுங்கள்.",
            ],
            "definitions": [],
            "dates": [],
            "maps_locations": [],
            "scientific_concepts": [],
            "formulae": [],
            "summary": f"தரம் {grade} நிலையான பயிற்சி வேகத்தையும் துல்லியத்தையும் உருவாக்கும்.",
            "exam_tips": [
                "எளிய மதிப்பெண்களுடன் தொடங்குங்கள்.",
                "கட்டமைப்புக் கேள்வியை காலியாக விடாதீர்கள் — முதல் படிகளை எழுதுங்கள்.",
            ],
            "study_tips": [
                "தினம்: 5 திறன் கேள்விகள்",
                "வாரம்: 1 நேர அளவுப் பகுதி",
            ],
            "important_questions": [
                "இந்த வாரம் எந்தத் தலைப்பில் அதிகம் தவறு செய்தேன்?",
            ],
            "revision_notes": (
                "• தினம்: 5 திறன் கேள்விகள்\n"
                "• வாரம்: 1 நேர அளவுப் பகுதி\n"
                "• மாதம்: முழு மாதிரித் தேர்வு (கிடைத்தால்)"
            ),
            "keywords": ["பயிற்சி", "practice", "revision", "தேர்வு", f"grade{grade}"],
            "resource_links": [
                {
                    "label": "திருத்தத் திட்டம்",
                    "url": "",
                    "note": "வாரநாட்களில் தலைப்புகளைப் பிரியுங்கள்; ஞாயிறு மீளாய்வு.",
                }
            ],
            "language": "Tamil",
            "generated_by": "vstudy_ai_template_ta",
        },
    ]
