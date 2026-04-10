import re


# ─────────────────────────────────────────────────────────────
# README QUALITY DETECTION
# ─────────────────────────────────────────────────────────────

# Sections from the mandatory structured README format
STRUCTURED_SECTIONS = [
    "Features", "Key Features",
    "How It Works", "How it Works", "Flow",
    "Scalability", "Scale",
    "Novelty", "Innovation",
    "Feature Depth", "Features in Depth",
    "Feasibility",
    "Tech Stack", "Technology Stack",
    "Problem Statement", "Proposed Solution",
    "Comparison", "Existing Solutions",
]


def detect_readme_quality(readme: str) -> dict:
    """
    Detect how structured a README is.

    Returns:
        {
            "mode":           "structured" | "fallback",
            "sections_found": int,
            "matched":        [list of section names found],
        }

    Rules:
        >= 2 known sections → structured mode (use section extraction)
        <  2 sections       → fallback mode   (use code signals + raw snippet)
    """
    if not readme or len(readme.strip()) < 30:
        return {"mode": "fallback", "sections_found": 0, "matched": []}

    matched = []
    for section in STRUCTURED_SECTIONS:
        # Look for ## Section or ### Section headers
        pattern = rf"#{1,3}\s*[^\n]*{re.escape(section)}[^\n]*"
        if re.search(pattern, readme, re.IGNORECASE):
            matched.append(section)

    sections_found = len(matched)
    mode = "structured" if sections_found >= 2 else "fallback"
    return {"mode": mode, "sections_found": sections_found, "matched": matched}


# ─────────────────────────────────────────────────────────────
# README SECTION EXTRACTION (for structured READMEs)
# ─────────────────────────────────────────────────────────────

def _extract_readme_section(readme: str, *section_names) -> str:
    """
    Extract a section from a structured README by header name.
    Returns up to 250 chars of content, whitespace-collapsed.
    Returns "" if not found — callers handle the empty case gracefully.
    """
    for name in section_names:
        pattern = rf"#{2,3}\s*[^\n]*{re.escape(name)}[^\n]*\n(.*?)(?=\n#{1,3}\s|\Z)"
        match = re.search(pattern, readme, re.IGNORECASE | re.DOTALL)
        if match:
            content = match.group(1).strip()
            content = re.sub(r"[*\-`>#]", "", content)
            content = re.sub(r"\s+", " ", content)
            return content[:250].strip()
    return ""


def _extract_functional_requirements(problem_statement: str) -> list:
    """
    Parse numbered requirements from the structured PS format.
    Matches: '1. Requirement text' or '* 1. Requirement text'
    Returns up to 12 requirements.
    """
    requirements = []
    for _, text in re.findall(r"(?:\*\s*)?(\d+)\.\s+(.+)", problem_statement):
        text = text.strip()
        if len(text) > 10:
            requirements.append(text)
    return requirements[:12]


# ─────────────────────────────────────────────────────────────
# PROJECT UNDERSTANDING PROMPT  (hybrid)
# ─────────────────────────────────────────────────────────────

def build_project_understanding_prompt(context):
    """
    Hybrid prompt:
      - Structured READMEs (>= 2 known sections): extract Features, How It Works,
        Novelty, etc. and feed them explicitly to the LLM.
      - Unstructured READMEs: fall back to raw first-200-chars + code signals.

    Either way the output format is identical (name=value lines).
    """
    readme   = context.get("project_description", "")
    tech     = list(context.get("detected_tech_stack", {}).keys())
    metrics  = context.get("code_metrics", {})
    snippets = context.get("code_snippets", [])
    cg       = context.get("call_graph_summary", {})
    fs       = context.get("folder_structure", {})

    files       = metrics.get("files_analyzed", 0) + metrics.get("files_fallback", 0)
    funcs       = metrics.get("total_functions", 0)
    func_names  = [s.get("function_name", "") for s in snippets if s.get("function_name")][:5]
    most_called = cg.get("most_called", [])[:4]

    snip = ""
    if snippets:
        lines = snippets[0].get("snippet", "").splitlines()[:4]
        snip  = snippets[0].get("file", "") + ": " + " | ".join(lines)

    quality = detect_readme_quality(readme)

    if quality["mode"] == "structured":
        # ── STRUCTURED PATH ─────────────────────────────────
        how_it_works = _extract_readme_section(readme, "How It Works", "How it Works", "Flow")
        features     = _extract_readme_section(readme, "Features", "Key Features")
        novelty      = _extract_readme_section(readme, "Novelty", "Innovation")
        tagline      = _extract_readme_section(readme, "Problem Statement", "Proposed Solution") \
                       or readme[:180].replace("\n", " ").strip()

        readme_block = (
            f"features={features}\n"
            f"how_it_works={how_it_works}\n"
            f"novelty={novelty}\n"
            f"tagline={tagline[:150]}"
        )
    else:
        # ── FALLBACK PATH ────────────────────────────────────
        # Just use a raw snippet of the README — don't try section extraction
        readme_block = f"readme={readme[:200].replace(chr(10), ' ').strip()}"

    return f"""Describe this project. Reply as name=value lines only, nothing else.

tech={tech} files={files} functions={funcs}
folder_dirs={fs.get('unique_dirs', 0)} named_layers={fs.get('named_layers', [])}
key_functions={func_names} most_called={most_called}
{readme_block}
code={snip[:150]}

project_type= (e.g. web app, CLI tool, ML model, game, desktop app, security tool)
problem_summary= (one sentence: what real-world problem does it solve)
solution_summary= (one sentence: specifically how the code solves it)
technologies= (comma separated: actual frameworks and libraries used)
architecture= (one sentence: how frontend/backend/data layers connect)"""