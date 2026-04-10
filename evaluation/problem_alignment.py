import re

from llm.ollama_client import call_ollama
from llm.prompt_builder import (
    detect_readme_quality,
    _extract_readme_section,
    _extract_functional_requirements,
)
from utils.kv_parser import parse_kv, get_str


def build_alignment_prompt(context, problem_statement):
    """
    Hybrid alignment prompt.

    Structured README (>= 2 sections):
        - Extracts Features, How It Works, Feature Depth from README.
        - Parses numbered requirements from the problem statement into a checklist.
        - LLM is asked to verify each requirement against code + README evidence.

    Unstructured README:
        - Uses raw readme snippet + code signals only.
        - No requirement checklist (avoids hallucinating checks against empty sections).
        - Fallback scoring is gentler.
    """
    tech     = list(context.get("detected_tech_stack", {}).keys())
    readme   = context.get("project_description", "")
    metrics  = context.get("code_metrics", {})
    snips    = context.get("code_snippets", [])
    cg       = context.get("call_graph_summary", {})
    mg       = context.get("module_graph_summary", {})

    total         = metrics.get("files_analyzed", 0) + metrics.get("files_fallback", 0)
    func_names    = [s.get("function_name", "") for s in snips if s.get("function_name")][:8]
    most_called   = cg.get("most_called", [])[:5]
    most_imported = mg.get("most_imported", [])[:5]
    ps_trimmed    = problem_statement[:600]

    quality = detect_readme_quality(readme)

    if quality["mode"] == "structured":
        # ── STRUCTURED PATH ─────────────────────────────────
        features      = _extract_readme_section(readme, "Features", "Key Features")
        how_it_works  = _extract_readme_section(readme, "How It Works", "How it Works")
        feature_depth = _extract_readme_section(readme, "Feature Depth", "Features in Depth")

        requirements  = _extract_functional_requirements(problem_statement)
        if requirements:
            reqs_block = "\n".join(f"  {i+1}. {r}" for i, r in enumerate(requirements))
        else:
            reqs_block = "  (no numbered requirements found — evaluate against plain PS text)"

        readme_evidence = (
            f"readme_features={features}\n"
            f"readme_how_it_works={how_it_works}\n"
            f"readme_feature_depth={feature_depth}"
        )

        checklist_instruction = (
            "For each functional requirement above, check if the project implements it."
        )
    else:
        # ── FALLBACK PATH ────────────────────────────────────
        # No section extraction. Show raw readme + code only.
        reqs_block = "  (unstructured README — score based on tech stack and code signals)"
        readme_evidence = f"readme={readme[:200].replace(chr(10), ' ').strip()}"
        checklist_instruction = (
            "README is unstructured. Score based on tech stack match and function evidence only."
        )

    return f"""Score how well this project addresses its problem statement.
Reply as name=value lines only, nothing else.

PROBLEM STATEMENT:
{ps_trimmed}

FUNCTIONAL REQUIREMENTS CHECKLIST:
{reqs_block}

PROJECT EVIDENCE:
tech={tech} files={total} key_functions={func_names}
most_called={most_called} most_imported={most_imported}
{readme_evidence}

{checklist_instruction}
Score 0-10:
  0-2 = completely unrelated
  3-4 = same domain, barely addresses requirements
  5-6 = partially addresses, several requirements missing
  7-8 = strongly aligned, most requirements met with code evidence
  9-10 = all requirements addressed with clear implementation

alignment_score= (integer 0-10)
reasoning= (one sentence referencing specific requirements met or missed)
matched= (comma-separated SHORT names of requirements that ARE implemented)
missing= (comma-separated SHORT names of requirements that are ABSENT)"""


def run_problem_alignment(context, problem_statement):
    files_a = context.get("code_metrics", {}).get("files_analyzed", 0)
    files_f = context.get("code_metrics", {}).get("files_fallback", 0)

    if files_a == 0 and files_f == 0:
        return {
            "alignment_score":      0,
            "alignment_reasoning":  "No files found.",
            "matched_requirements": [],
            "missing_requirements": [],
        }

    readme   = context.get("project_description", "")
    quality  = detect_readme_quality(readme)
    tech     = list(context.get("detected_tech_stack", {}).keys())
    total    = files_a + files_f

    # Fallback score is slightly more generous for unstructured READMEs
    # because we have less evidence — we shouldn't penalise what we can't see
    if quality["mode"] == "structured":
        fallback_score = 3 if (tech and total > 0) else 0
    else:
        fallback_score = 4 if (tech and total > 0) else 1

    fb     = {"alignment_score": fallback_score}
    raw    = call_ollama(build_alignment_prompt(context, problem_statement))
    parsed = parse_kv(raw, ["alignment_score"], fb)
    score  = min(max(round(float(parsed.get("alignment_score", fallback_score)), 1), 0), 10)

    reasoning = get_str(parsed, "reasoning",
                        default="Alignment assessed from tech stack and function names.")

    matched = []
    missing = []
    if raw:
        for line in raw.splitlines():
            line = line.strip()
            if not line or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip().lower()
            val = val.strip().strip("\"'")
            if key == "matched" and val:
                items = [v.strip() for v in re.split(r"[,;]", val) if v.strip()]
                matched = [i for i in items if len(i) < 80]
            elif key == "missing" and val:
                items = [v.strip() for v in re.split(r"[,;]", val) if v.strip()]
                missing = [i for i in items if len(i) < 80]

    bad = {"requirement 1", "requirement 2", "requirement 3",
           "matched requirement", "missing requirement"}
    matched = [r for r in matched if r.lower() not in bad and r.lower() != "none"]
    missing = [r for r in missing if r.lower() not in bad and r.lower() != "none"]

    return {
        "alignment_score":      score,
        "alignment_reasoning":  reasoning,
        "matched_requirements": matched,
        "missing_requirements": missing,
        # expose readme quality so final_evaluator can use it in scoring
        "_readme_mode":         quality["mode"],
        "_readme_sections":     quality["sections_found"],
    }