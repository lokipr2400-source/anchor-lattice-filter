import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from anchor_lattice.filter import filter_batch
from anchor_lattice.spec import DUP_COS, H_MAX, H_MIN, MIN_CHARS, SPEC_VERSION


def test_short_dropped():
    out = filter_batch(["too short", "This statement is long enough to pass the character floor."])
    by_text = {item["text"]: item for item in out["items"]}
    assert by_text["too short"]["reason"] == "short"
    assert by_text["too short"]["keep"] is False


def test_duplicate_second_copy_dropped():
    text = "Keep model updates small so continuity does not collapse during a scale jump."
    out = filter_batch([text, text, "Balance opposing clusters so one faction cannot dominate the preference signal."])
    same = [item for item in out["items"] if item["text"] == text]
    assert sum(item["keep"] for item in same) == 1
    assert any(item["reason"] == "duplicate" for item in same)


def test_spec_version_frozen():
    out = filter_batch(["A coherent preference about keeping updates conservative and small."])
    assert out["spec_version"] == SPEC_VERSION


def test_example_batch_runs():
    batch = json.loads((ROOT / "examples" / "batch.json").read_text())
    texts = [row["text"] for row in batch]
    poles = [row["pole"] for row in batch]
    out = filter_batch(texts, poles=poles, backend="hash")
    assert out["kept"] + out["dropped"] == len(texts)
    assert any(item["keep"] for item in out["items"])
    assert any(item["reason"] == "short" for item in out["items"])


if __name__ == "__main__":
    test_short_dropped()
    test_duplicate_second_copy_dropped()
    test_spec_version_frozen()
    test_example_batch_runs()
    print("ok")
    print("H band", H_MIN, H_MAX, "dup", DUP_COS, "min_chars", MIN_CHARS)
