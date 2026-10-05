#!/usr/bin/env python3
"""dump.py: Automated Architectural Codebase Dump Generator for ModelVM.

Consolidates the complete implementation of ModelVM into a single, clean,
well-indexed Markdown document (`dump.md`), ensuring that research papers,
auditors, and code reviewers always have an up-to-date, single-file reference.

Usage:
    python dump.py
    python dump.py --output custom_dump.md
    python dump.py --also-docs
    python dump.py --include-tests
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Core architecture files ordered logically from foundational types to benchmarks
CORE_ARCHITECTURE_FILES: List[Tuple[str, str, str]] = [
    # (Section Title, Relative Path, Description)
    (
        "1. Core Type System & Enumerations",
        "modelvm/core/types.py",
        "Foundational enums: Capabilities, PagingActions, AblationModes, PagingEvent, TaskStatus",
    ),
    (
        "2. Model Manifest & Catalog",
        "modelvm/core/manifest.py",
        "ModelManifest, ModelCatalog, capability scoring, and 10-model heterogeneous library",
    ),
    (
        "3. Cognitive State Packet (CSP)",
        "modelvm/core/state_packet.py",
        "Semantic state transfer schema, multi-source confidence aggregation, and artifact conflict preservation",
    ),
    (
        "4. Independent Verification & Ground-Truth Engine",
        "modelvm/core/verifier.py",
        "Independent ArithmeticVerifier (safe AST arithmetic checking) and IndependentEvaluator for non-circular grading",
    ),
    (
        "5. Virtual Memory Eviction Policies",
        "modelvm/pager/policy.py",
        "EvictionPolicy ABC, LRUEvictionPolicy, and future-protected CostAwareEvictionPolicy",
    ),
    (
        "6. Model Pager & Memory Manager",
        "modelvm/pager/memory_manager.py",
        "ModelPager virtual memory runtime, hard RAM budget enforcement, page-in/out, and prefetch",
    ),
    (
        "7. Resource-Aware Multi-Objective Scheduler",
        "modelvm/scheduler/cognitive_scheduler.py",
        "Multi-objective 6-term selection formula balancing capability fit, RAM, load, energy, eviction, and future demand",
    ),
    (
        "8. Working Set Predictor & Prefetch Scorer",
        "modelvm/router/working_set.py",
        "Unified working set predictor using scheduler model ranking and dimensionally consistent prefetch utility",
    ),
    (
        "9. Confidence Controller & Cognitive Escalation",
        "modelvm/router/confidence.py",
        "Output quality evaluation, uncertainty tracking, and closed-loop escalation triggers",
    ),
    (
        "10. Task Decomposer & Pipeline Planner",
        "modelvm/router/task_decomposer.py",
        "Cognitive task decomposition into ordered stage graphs with capability requirements",
    ),
    (
        "11. Cognitive Operating System Kernel",
        "modelvm/executor/kernel.py",
        "Central execution runtime orchestrating Modes A, B, C, D with resource-aware Delta-Q escalation",
    ),
    (
        "12. Execution Backends & Inference Connectors",
        "modelvm/executor/backends.py",
        "High-fidelity simulation backend and live local Ollama connector with strict execution modes (no silent fallback)",
    ),
    (
        "13. Decoupled Benchmark Evaluator",
        "modelvm/benchmark/evaluator.py",
        "Non-circular evaluator separating CSP completeness, ground-truth state integrity, task correctness, and efficiency",
    ),
    (
        "14. Critical Ablation Study Suite",
        "modelvm/benchmark/ablation.py",
        "Automated runner executing the 4-mode orthogonal ablation study and 2^3 factorial matrix",
    ),
    (
        "15. Hardware Telemetry & Resource Profiler",
        "modelvm/telemetry/hardware.py",
        "Delta-based GPU VRAM, host RSS memory profiling, and transition latency measurement",
    ),
    (
        "16. Empirical Capability Profiler",
        "modelvm/registry/profiler.py",
        "Standardized held-out capability probes and empirical matrix generator answering Reviewer Attack 3",
    ),
]

TEST_FILES: List[Tuple[str, str, str]] = [
    (
        "Appendix A. CSP State Packet & Merge Algebra Tests",
        "tests/test_state_packet.py",
        "Unit tests proving associativity, commutativity, idempotence, confidence aggregation, and conflict resolution",
    ),
    (
        "Appendix B. Scheduler, Pager & Prefetch Tests",
        "tests/test_scheduler.py",
        "Unit tests verifying multi-objective scores, lookahead window clamping, and prefetch ROI logic",
    ),
    (
        "Appendix C. Benchmark & Dynamic Quality Tests",
        "tests/test_benchmark.py",
        "Unit tests verifying dynamic quality computation from verified facts, calcs, and evidence",
    ),
    (
        "Appendix D. 2^3 Factorial Ablation Matrix Tests",
        "tests/test_factorial_ablation.py",
        "Unit tests verifying the 2^3 orthogonal factorial matrix, main effects, and interactions",
    ),
    (
        "Appendix E. Empirical Capability Profiler Tests",
        "tests/test_profiler.py",
        "Unit tests verifying probe responses, empirical catalog scoring, and capability matrix tables",
    ),
]


def generate_dump(
    root_dir: Path,
    output_path: Path,
    include_tests: bool = False,
    also_docs: bool = True,
) -> None:
    """Generates a complete, indexed markdown dump from actual codebase files."""
    sections_to_dump = list(CORE_ARCHITECTURE_FILES)
    if include_tests:
        sections_to_dump.extend(TEST_FILES)

    lines: List[str] = []

    # Header
    lines.append("# ModelVM: Core Architectural Codebase Dump\n")
    lines.append(
        "This document contains a comprehensive, consolidated dump of the core architecture implementation for "
        "**ModelVM (Virtual Memory for Intelligence)**, updated with all peer-review alignment fixes "
        "(confidence aggregation, stage-level lookahead with distance decay, prefetch ROI scoring, "
        "dynamic quality calculation from CSP artifacts, artifact conflict versioning, and scheduler-ranked "
        "escalation with loop protection).\n"
    )
    lines.append(f"**Generated on:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`  ")
    lines.append(f"**Source Repository:** `{root_dir.resolve()}`  \n")
    lines.append("---\n")

    # Directory Structure Tree
    lines.append("## Architecture Summary & Component Directory\n")
    lines.append("```")
    lines.append("modelvm/")
    lines.append("├── core/")
    lines.append("│   ├── types.py                 # Enums: Capabilities, PagingActions, AblationModes, ExecutionMode")
    lines.append("│   ├── manifest.py              # ModelManifest specification & capability matching")
    lines.append("│   ├── state_packet.py          # Cognitive State Packet (CSP), merge_update, serializations")
    lines.append("│   └── verifier.py              # Independent ArithmeticVerifier (AST) & GroundTruth Evaluator")
    lines.append("├── pager/")
    lines.append("│   ├── policy.py                # EvictionPolicy, LRUEvictionPolicy, CostAwareEvictionPolicy")
    lines.append("│   └── memory_manager.py        # ModelPager virtual memory manager, page_in/page_out, prefetch")
    lines.append("├── scheduler/")
    lines.append("│   └── cognitive_scheduler.py   # Multi-objective cost-aware scheduler (6-term Score formula)")
    lines.append("├── router/")
    lines.append("│   ├── task_decomposer.py       # TaskDecomposer: breaking goals into ordered cognitive stages")
    lines.append("│   ├── working_set.py           # CognitiveWorkingSetPredictor: W(t,k) lookahead & prefetching")
    lines.append("│   └── confidence.py            # ConfidenceController: quality thresholding & cognitive escalation")
    lines.append("├── executor/")
    lines.append("│   ├── backends.py              # SimulationBackend & OllamaBackend with domain fit effects")
    lines.append("│   └── kernel.py                # CognitiveKernel: central runtime executing modes A, B, C, D")
    lines.append("├── telemetry/")
    lines.append("│   └── hardware.py              # HardwareTelemetry: real host RSS, delta GPU VRAM & transition timing")
    lines.append("└── benchmark/")
    lines.append("    ├── evaluator.py             # Evaluator: computing MSR, CCS, Capability Density, Latency")
    lines.append("    └── ablation.py              # AblationStudyRunner & FactorialStudyRunner (2^3 factorial matrix)")
    if include_tests:
        lines.append("tests/")
        lines.append("├── test_state_packet.py         # Algebraic merge proofs (associativity, commutativity)")
        lines.append("├── test_scheduler.py            # Scheduler scoring, lookahead & prefetch tests")
        lines.append("├── test_benchmark.py            # Quality computation & metric evaluation tests")
        lines.append("└── test_factorial_ablation.py   # Orthogonal 2^3 factorial matrix & main effects tests")
    lines.append("```\n")
    lines.append("---\n")

    # Table of Contents
    lines.append("## Table of Contents\n")
    for title, rel_path, desc in sections_to_dump:
        anchor = title.lower().replace(" ", "-").replace(".", "").replace("&", "").replace("(", "").replace(")", "").replace(",", "")
        file_path = root_dir / rel_path
        if file_path.exists():
            line_count = len(file_path.read_text(encoding="utf-8").splitlines())
            size_kb = file_path.stat().st_size / 1024.0
            lines.append(f"- [{title}](#{anchor}) (`{rel_path}`) — *{line_count} lines, {size_kb:.1f} KB*")
        else:
            lines.append(f"- [{title}](#{anchor}) (`{rel_path}`) — *(Missing)*")
    lines.append("\n---\n")

    total_lines = 0
    total_bytes = 0

    # Dump file contents
    for title, rel_path, desc in sections_to_dump:
        file_path = root_dir / rel_path
        lines.append(f"## {title}\n")
        lines.append(f"**File:** [`{rel_path}`]({rel_path})  ")
        lines.append(f"**Role:** {desc}\n")

        if not file_path.exists():
            lines.append(f"> ⚠️ **Warning:** File `{rel_path}` not found.\n\n---\n")
            continue

        content = file_path.read_text(encoding="utf-8")
        file_line_count = len(content.splitlines())
        file_byte_count = len(content.encode("utf-8"))
        total_lines += file_line_count
        total_bytes += file_byte_count

        lines.append("```python")
        lines.append(content)
        lines.append("```\n")
        lines.append("---\n")

    full_text = "\n".join(lines)

    # Write target file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(full_text, encoding="utf-8")
    print(f"[+] Generated {output_path} ({len(lines)} markdown lines, {total_lines} source lines, {total_bytes / 1024:.1f} KB)")

    # Optionally sync docs/dump.md
    if also_docs and output_path.resolve() != (root_dir / "docs" / "dump.md").resolve():
        docs_dump_path = root_dir / "docs" / "dump.md"
        docs_dump_path.parent.mkdir(parents=True, exist_ok=True)
        docs_dump_path.write_text(full_text, encoding="utf-8")
        print(f"[+] Synchronized {docs_dump_path}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Generate dump.md from ModelVM codebase.")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="dump.md",
        help="Target output file path (default: dump.md in project root)",
    )
    parser.add_argument(
        "--include-tests",
        "-t",
        action="store_true",
        help="Include unit test files in the dump as appendices.",
    )
    parser.add_argument(
        "--no-docs-sync",
        action="store_true",
        help="Disable automatic synchronization with docs/dump.md.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    out_file = project_root / args.output

    generate_dump(
        root_dir=project_root,
        output_path=out_file,
        include_tests=args.include_tests,
        also_docs=not args.no_docs_sync,
    )


if __name__ == "__main__":
    main()
