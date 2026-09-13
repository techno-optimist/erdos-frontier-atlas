"""Keep the README inventory, research entry points and anchors current."""
import json
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_readme_inventory_matches_the_source_ledgers():
    sources = {
        "Hub records": ("atlas/stubs.json", "problems"),
        "Deep-tier records": ("atlas/problems.json", "problems"),
        "Bracketed quantities": ("atlas/gap_map.json", "entries"),
        "Registered methods": ("atlas/substrate.json", "methods"),
    }
    readme = (ROOT / "README.md").read_text()
    for label, (path, key) in sources.items():
        count = len(json.loads((ROOT / path).read_text())[key])
        assert f"| {label} | {count:,} |" in readme, (label, count)


def test_readme_points_to_current_method_and_freshness_records():
    readme = (ROOT / "README.md").read_text()
    targets = (
        "experiments/astra-substrate-20260911/README.md",
        "experiments/astra-rh-969-20260912/REPOSITORY_STATUS.md",
        "experiments/astra-rh-crt-20260912/GM_TRANSFER.md",
        "experiments/astra-rh-crt-20260912/ARITHMETIC_FRONTIER.md",
        "experiments/astra-327-fiber-20260912/README.md",
        "experiments/astra-i3-20260911/GOAL.md",
        "experiments/astra-freshness-20260911/README.md",
    )
    for target in targets:
        assert f"]({target})" in readme, target
        assert (ROOT / target).is_file()


def _without_fenced_code(markdown):
    """Skip top-level backtick/tilde fences, not general Markdown parsing."""
    visible = []
    fence = None
    for line in markdown.splitlines():
        if fence is not None:
            if re.fullmatch(rf" {{0,3}}{fence[0]}{{{len(fence)},}}[ \t]*", line):
                fence = None
            continue
        opener = re.match(r" {0,3}(`{3,}|~{3,})(.*)", line)
        if opener:
            marker, info = opener.groups()
            if marker[0] == "~" or "`" not in info:
                fence = marker
                continue
        visible.append(line)
    return "\n".join(visible)


def test_readme_same_page_anchors_resolve():
    readme = _without_fenced_code((ROOT / "README.md").read_text())
    anchors = set(re.findall(r'<a\s+(?:id|name)="([^"]+)"', readme))
    counts = {}
    for title in re.findall(r"^#{1,6} (.+)$", readme, re.M):
        base = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        number = counts.get(base, 0)
        anchors.add(base if number == 0 else f"{base}-{number}")
        counts[base] = number + 1
    links = re.findall(r"\]\(#([^\s)]+)\)", readme)
    assert not (set(links) - anchors)


def test_readme_rejects_fenced_heading_anchor(tmp_path, monkeypatch):
    (tmp_path / "README.md").write_text(
        "```markdown\n## Visible\n```\n\n[x](#visible)\n", encoding="utf-8"
    )
    monkeypatch.setitem(globals(), "ROOT", tmp_path)
    with pytest.raises(AssertionError):
        test_readme_same_page_anchors_resolve()


@pytest.fixture
def scratch_anchor_guard(tmp_path, monkeypatch):
    monkeypatch.setitem(globals(), "ROOT", tmp_path)

    def check(readme):
        (tmp_path / "README.md").write_text(readme, encoding="utf-8")
        test_readme_same_page_anchors_resolve()

    return check


@pytest.mark.parametrize("opening, closing", [
    pytest.param("```markdown", "```", id="backticks"),
    pytest.param("~~~markdown", "~~~", id="tildes"),
    pytest.param("````markdown", "`````", id="long-backticks"),
    pytest.param("~~~~markdown", "~~~~~~", id="long-tildes"),
    pytest.param("   ```markdown", " ````` \t", id="indented-backticks"),
    pytest.param(" ~~~markdown", "   ~~~~~ \t", id="indented-tildes"),
])
@pytest.mark.parametrize("before, body, after, resolves", [
    pytest.param("", "## Visible", "[x](#visible)", False, id="hidden-heading"),
    pytest.param("", '<a id="visible"></a>', "[x](#visible)", False, id="hidden-id"),
    pytest.param("", '<a name="visible"></a>', "[x](#visible)", False, id="hidden-name"),
    pytest.param("## Visible", "## Visible", "[x](#visible-1)", False,
                 id="hidden-heading-does-not-increment-suffix"),
    pytest.param(
        '## Visible\n<a id="before"></a>\n[x](#before)',
        "## Visible\n[example](#not-an-anchor)",
        '## Visible\n<a name="after"></a>\n'
        "[x](#visible)\n[x](#visible-1)\n[x](#after)",
        True, id="code-link-ignored-real-anchors-preserved",
    ),
])
def test_readme_fenced_anchor_controls(
    scratch_anchor_guard, opening, closing, before, body, after, resolves
):
    readme = f"{before}\n\n{opening}\n{body}\n{closing}\n\n{after}\n"
    if resolves:
        scratch_anchor_guard(readme)
    else:
        with pytest.raises(AssertionError):
            scratch_anchor_guard(readme)


@pytest.mark.parametrize("marker", ["`", "~"])
@pytest.mark.parametrize("invalid_kind", ["shorter", "different", "text", "indented"])
def test_readme_fences_require_valid_closing_markers(
    scratch_anchor_guard, marker, invalid_kind
):
    invalid = {
        "shorter": marker * 3,
        "different": ("~" if marker == "`" else "`") * 4,
        "text": marker * 4 + " not-a-closer",
        "indented": "    " + marker * 4,
    }[invalid_kind]
    scratch_anchor_guard(
        f"{marker * 4}markdown\n{invalid}\n[example](#missing)\n"
        f"{marker * 5}\n\n## Visible\n[x](#visible)\n"
    )


@pytest.mark.parametrize("marker", ["`", "~"])
def test_readme_unclosed_fences_extend_to_eof(scratch_anchor_guard, marker):
    code = f'{marker * 3}\n## Hidden\n<a id="hidden-id"></a>\n[x](#missing)\n'
    scratch_anchor_guard("## Visible\n[x](#visible)\n\n" + code)
    for fragment in ("hidden", "hidden-id"):
        with pytest.raises(AssertionError):
            scratch_anchor_guard(f"[x](#{fragment})\n\n" + code)


@pytest.mark.parametrize("readme, resolves", [
    pytest.param("## Visible\n[x](#visible)\n", True, id="real-heading"),
    pytest.param('<a id="visible"></a>\n[x](#visible)\n', True, id="real-id"),
    pytest.param('<a name="visible"></a>\n[x](#visible)\n', True, id="real-name"),
    pytest.param("[x](#missing)\n", False, id="ordinary-broken-link"),
    pytest.param("```bad`info\n## Visible\n[x](#visible)\n", True,
                 id="backtick-in-info-is-not-an-opener"),
    pytest.param("~~~valid`info\n[x](#missing)\n~~~\n## Visible\n[x](#visible)\n",
                 True, id="backtick-in-tilde-info-is-allowed"),
])
def test_readme_anchor_scratch_controls(scratch_anchor_guard, readme, resolves):
    if resolves:
        scratch_anchor_guard(readme)
    else:
        with pytest.raises(AssertionError):
            scratch_anchor_guard(readme)
