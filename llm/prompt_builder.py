import json


def build_project_understanding_prompt(context):
    """
    Ultra-compact project understanding prompt.
    Uses key=value format so LLM just continues lines — reliable even on slow CPU.
    """
    readme   = context.get("project_description", "")[:200]
    tech     = list(context.get("detected_tech_stack", {}).keys())
    metrics  = context.get("code_metrics", {})
    snippets = context.get("code_snippets", [])

    snip = ""
    if snippets:
        lines = snippets[0].get("snippet", "").splitlines()[:4]
        snip  = "\n".join(lines)

    funcs   = metrics.get("total_functions", 0)
    files   = metrics.get("files_analyzed", 0)

    return f"""Describe this project. Reply as name=value lines only.

tech={tech} files={files} functions={funcs}
readme={readme[:150]}
code={snip[:150]}

project_type=
problem_summary=
solution_summary=
technologies=
architecture="""