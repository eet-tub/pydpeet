import subprocess
from pathlib import Path

files = [
    "metadata.md",
    "summary.md",
    "statement_of_need.md",
    "state_of_the_field.md",
    "software_design.md",
    "research_impact_statement.md",
    "ai_usage_disclosure.md",
]

content = []

for file in files:
    content.append(Path("paper/src", file).read_text(encoding="utf-8"))

Path("paper/paper.md").write_text(
    "\n\n".join(content),
    encoding="utf-8",
)

paper_dir = Path.cwd() / "paper"

subprocess.check_call(
    ["docker", "run", "--rm", "--volume", f"{paper_dir}:/data", "--env", "JOURNAL=joss", "openjournals/inara"]
)
