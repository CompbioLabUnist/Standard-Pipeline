"""Offline checks for GATK Mutect2 job-script argument boundaries.

Tests the real upstream PipelineManager method, without running GATK or sbatch.
Run from a checkout of CompbioLabUnist/Standard-Pipeline.
"""
import importlib.util
import shlex
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "03_Somatic_short_variant_discovery" / "03_1_Mutect2.py"
# Test-only import resolution; the documented CLI workflow still uses symlinks.
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("mutect2_pipeline_module", MODULE)
mutect2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mutect2)


@pytest.mark.parametrize(
    ("panel_enabled", "making_panel", "expected_input_count"),
    [(False, False, 2), (True, True, 1), (True, False, 2)],
)
def test_mutect2_script_separates_gatk_options(
    tmp_path, panel_enabled, making_panel, expected_input_count
):
    # Bypass __init__: no config or biological data required.
    pipeline = mutect2.PipelineManager.__new__(mutect2.PipelineManager)
    pipeline.config = {
        "TOOLS": {"gatk": "gatk"},
        "DEFAULT": {"java_options": "-Xmx2g", "threads": "3"},
        "REFERENCES": {"fasta": "/ref.fa"},
    }
    pipeline.normal = "/normal.bam"
    pipeline.tumor = "/tumor.bam"
    pipeline.normal_name = "normal"
    pipeline.name = "sample"
    pipeline.output_dir = str(tmp_path)
    pipeline.panel_of_normals = panel_enabled

    # Capture the real generated command, but never write or submit jobs.
    scripts, submissions = [], []
    pipeline.create_sh = lambda name, command: scripts.append((name, command))
    pipeline.submit_job = lambda name, dependency_id=None: submissions.append(name)

    pipeline.run_mutect(make_panel_of_normals=making_panel)
    assert len(scripts) == len(submissions) == 1
    args = shlex.split(scripts[0][1])
    assert args[:2] == ["gatk", "Mutect2"]
    assert args.count("--input") == expected_input_count
    assert args.count("--native-pair-hmm-threads") == 1
    assert args[args.index("--native-pair-hmm-threads") + 1] == "3"
    if panel_enabled and not making_panel:
        assert args.count("--panel-of-normals") == 1
        assert args[args.index("--panel-of-normals") + 1] == str(
            tmp_path / "panel_of_normals.vcf.gz"
        )
    else:
        assert "--panel-of-normals" not in args
