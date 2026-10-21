"""Baseline the frozen mote snapshot and independently reproduce the A008 defect."""
import json
import os
from pathlib import Path
import re
import subprocess
import time

AB = Path(__file__).resolve().parents[1] / "ab/2026-10-21"


def main():
    raw = AB / "raw"
    raw.mkdir(exist_ok=True)
    source = (AB / "snapshot/crates/mote-core/src/orbit.rs").read_text(encoding="utf-8")
    function = re.search(r"pub fn wrap180_deg\(lon: f64\) -> f64 \{[^}]+\}", source).group()
    harness = function + '''
#[test]
fn finite_longitudes_are_periodic() {
    for lon in [1e16_f64, -1e16, 1e20, -1e20, f64::MAX, -f64::MAX] {
        let reduced = lon.rem_euclid(360.0);
        assert_eq!(wrap180_deg(lon), wrap180_deg(reduced), "longitude {lon}");
    }
}
'''
    path = raw / "angle_repro.rs"
    path.write_text(harness, encoding="utf-8")
    executable = raw / "angle_repro.exe"
    subprocess.run(["rustc", "--edition=2024", "--test", str(path), "-o", str(executable)], check=True)
    probe = subprocess.run([str(executable), "--nocapture"], capture_output=True, text=True)
    (raw / "angle-repro.log").write_text(probe.stdout + probe.stderr, encoding="utf-8")
    print(f"Independent wrap periodicity reproduction: exit {probe.returncode}", flush=True)
    env = dict(os.environ, CARGO_TARGET_DIR=str(AB / "target"))
    started = time.monotonic()
    with (raw / "baseline-core.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(["cargo", "test", "--offline", "--release", "-p", "mote-core", "--lib"],
                                   cwd=AB / "snapshot", env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            code = process.wait(timeout=240)
            timeout = False
        except subprocess.TimeoutExpired:
            process.kill()
            code = process.wait()
            timeout = True
    result = {"repro_exit": probe.returncode, "baseline_exit": code,
              "baseline_timeout": timeout, "baseline_seconds": round(time.monotonic() - started, 2),
              "command": "cargo test --offline --release -p mote-core --lib",
              "bug": "A008: wrap180_deg violates longitude periodicity for accepted finite large inputs",
              "live_tree_modified": False}
    (AB / "baseline.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
