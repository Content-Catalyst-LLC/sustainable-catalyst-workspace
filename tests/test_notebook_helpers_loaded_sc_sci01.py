"""SC-SCI-01: the WordPress page loads the research notebook helpers the compatibility runtime needs.

Plugin 3.70.0 printed only the thin adapter, so ``window.SCWorkspaceResearchNotebook`` and its companions were
never defined and the notebook editor fell back to an empty template. The helpers are now registered as
dependencies of the one thin-adapter enqueue. These tests check the PHP wiring statically and run the helpers
in Node in the printed order to show a stored notebook (blocks and executable cells) survives normalisation.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "wordpress/sustainable-catalyst-workspace"
PHP = PLUGIN / "includes/class-sc-workspace.php"
JS = PLUGIN / "assets/js"
COMPAT = JS / "sc-workspace-local-project-compat-v3500.js"  # the runtime manifest v3500 the plugin loads
NOTEBOOK_GLOBALS = {"SCWorkspaceSourceCapture", "SCWorkspaceResearchNotebook", "SCWorkspaceNotebookPortability",
                    "SCWorkspaceNotebookReviewProvenance"}


def enqueue_block():
    return PHP.read_text().split("private function enqueue_assets()", 1)[1].split("wp_localize_script(", 1)[0]


def registered():
    block = enqueue_block()
    table = block.split("$notebook_helpers = array(", 1)[1].split(");", 1)[0]
    return {h: re.findall(r"'([a-z0-9-]+)'", deps) for h, deps in re.findall(r"'([a-z0-9-]+)' => array\(([^)]*)\)", table)}


def test_wordpress_still_enqueues_one_script_and_it_depends_on_the_notebook_helpers():
    block = enqueue_block()
    assert block.count("wp_enqueue_script(") == 1
    assert "wp_register_script($handle, SC_WORKSPACE_URL . 'assets/js/' . $handle . '.js', $deps" in block
    assert "array_keys($notebook_helpers)" in block.split("'sc-workspace-wordpress-thin-adapter-v3500'", 1)[1]
    helpers = registered()
    assert list(helpers) == ["sc-workspace-source-capture-v1", "sc-workspace-research-notebook-v8",
                             "sc-workspace-notebook-portability-v1", "sc-workspace-notebook-review-provenance-v1"]
    assert helpers["sc-workspace-research-notebook-v8"] == ["sc-workspace-source-capture-v1"]
    for handle in helpers:
        assert (JS / f"{handle}.js").is_file(), handle


def test_every_notebook_global_the_compatibility_runtime_reads_is_defined_by_a_registered_helper():
    used = set(re.findall(r"window\.(SCWorkspace[A-Za-z]+)", COMPAT.read_text())) & NOTEBOOK_GLOBALS
    assert used == NOTEBOOK_GLOBALS
    defined = set()
    for handle in registered():
        defined |= set(re.findall(r"root\.(SCWorkspace[A-Za-z]+)\s*=", (JS / f"{handle}.js").read_text()))
    assert NOTEBOOK_GLOBALS <= defined


NODE = r"""
const vm = require('vm'), fs = require('fs'), path = require('path');
const [dir, order] = [process.argv[1], JSON.parse(process.argv[2])];
const win = {}; win.globalThis = win; win.window = win;
const ctx = vm.createContext(win);
for (const h of order) vm.runInContext(fs.readFileSync(path.join(dir, h + '.js'), 'utf8'), ctx, {filename: h});
const nb = win.SCWorkspaceResearchNotebook;
const stored = {notebooks: [{schema: 'sc-workspace-notebook/3.0', id: 'nb-erw', title: 'Wexford ERW',
  sections: [{id: 's1', title: 'Method', blocks: [{id: 'b1', type: 'note', content: 'OLS in R; Julia replay.'}]}],
  cells: [{id: 'fit', type: 'code', language: 'r', source: 'fit <- lm(y ~ x, data = rows)',
           execution: {operation: 'workspace.polyglot.r.linear-model', payload: {outcome: 'y', predictors: ['x']}}}]}],
  activeNotebookId: 'nb-erw'};
const out = nb.workspace(stored, (p) => p + '-id', () => '2026-11-13T00:00:00.000Z');
console.log(JSON.stringify({globals: Object.keys(win).filter(k => k.startsWith('SCWorkspace')).sort(),
  notebook: out.notebooks[0]}));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="needs node")
def test_helpers_load_in_printed_order_and_keep_stored_notebooks_and_cells():
    order = list(registered())
    raw = subprocess.run(["node", "-e", NODE, str(JS), json.dumps(order)], capture_output=True, text=True, check=True).stdout
    out = json.loads(raw)
    assert NOTEBOOK_GLOBALS <= set(out["globals"])
    nb = out["notebook"]
    assert nb["id"] == "nb-erw" and nb["title"] == "Wexford ERW"
    assert nb["sections"][0]["blocks"][0]["content"] == "OLS in R; Julia replay."
    assert nb["cells"][0]["execution"]["operation"] == "workspace.polyglot.r.linear-model"  # kept verbatim
