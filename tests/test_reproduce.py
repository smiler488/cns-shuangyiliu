"""The committed result must be reproducible from the committed data."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(tmp_path, cls):
    out = tmp_path / f"{cls}.json"
    subprocess.run([sys.executable, str(ROOT / "scripts/analyze_cns.py"), "--cls", cls, "--out", str(out)],
                   check=True, capture_output=True)
    return json.loads(out.read_text(encoding="utf-8"))


def test_default_reproduces_published_result(tmp_path):
    published = json.loads((ROOT / "data/cns_result.json").read_text(encoding="utf-8"))
    assert run(tmp_path, "tsinghua") == published
    assert published["total_works"] == 3166
    assert published["nonzero_count"] == 120 and published["zero_count"] == 27


def test_cls_variants(tmp_path):
    rows = {c: {r["school"]: r for r in run(tmp_path, c)["rows"]} for c in ("none", "both")}
    assert (rows["none"]["清华大学"]["calA_strict"], rows["none"]["清华大学"]["calC_firstcorr"]) == (55, 259)
    assert rows["both"]["北京大学"]["calC_firstcorr"] == 296
