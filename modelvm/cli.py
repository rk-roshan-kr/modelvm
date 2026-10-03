"""ModelVM Command Line Interface.

Provides rich terminal visualization, live demo execution, ablation benchmarks,
and the local web dashboard launcher.
"""

from __future__ import annotations
import argparse
import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.layout import Layout
from rich.live import Live

from modelvm.core.types import AblationMode, PagingAction, PagingEvent
from modelvm.executor.kernel import CognitiveKernel, StageExecutionResult, TaskExecutionSummary
from modelvm.registry.catalog import ModelCatalog
from modelvm.benchmark.ablation import AblationStudyRunner


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

console = Console(legacy_windows=False)


def render_banner() -> None:
    """Displays the ModelVM header."""
    banner = (
        "[bold cyan] __  __           _      ___      ____  __ [/bold cyan]\n"
        "[bold cyan]|  \\/  | ___   __| | ___| \\ \\   / /  \\/  |[/bold cyan]\n"
        "[bold cyan]| |\\/| |/ _ \\ / _` |/ _ \\ |\\ \\ / /| |\\/| |[/bold cyan]\n"
        "[bold cyan]| |  | | (_) | (_| |  __/_| \\ V / | |  | |[/bold cyan]\n"
        "[bold cyan]|_|  |_|\\___/ \\__,_|\\___(_)  \\_/  |_|  |_|[/bold cyan]\n\n"
        "[bold white]       Virtual Memory for Intelligence — Local Cognitive Pager[/bold white]\n"
        "[dim]    Heterogeneous Open-Weight Models as Pageable Cognitive Resources[/dim]"
    )
    console.print(Panel(banner, border_style="cyan", padding=(1, 2)))


def print_memory_bar(active_gb: float, budget_gb: float, total_lib_gb: float) -> None:
    """Renders an ASCII memory allocation bar."""
    pct = min(1.0, active_gb / max(0.1, budget_gb))
    bar_width = 30
    filled = int(bar_width * pct)
    color = "green" if pct < 0.75 else ("yellow" if pct < 0.95 else "red")
    bar = f"[{color}]" + "=" * filled + "." * (bar_width - filled) + f"[/{color}]"
    
    console.print(
        f" [bold]Active RAM:[/bold] [{bar}] [bold {color}]{active_gb:.1f} / {budget_gb:.1f} GB[/bold {color}] "
        f"[dim](Model Library: {total_lib_gb:.1f} GB Total)[/dim]"
    )


def run_demo(budget_gb: float = 8.0) -> None:
    """Executes the winning PDR Section 11 demonstration."""
    render_banner()
    catalog = ModelCatalog()
    total_lib = catalog.total_library_size_gb()

    console.print("\n[bold yellow]═══ WINNING DEMONSTRATION: HARD MEMORY BUDGET EXPERIMENT ═══[/bold yellow]")
    console.print(f"[bold cyan]Model Library:[/bold cyan] {len(catalog.all_models())} models, [bold green]{total_lib} GB[/bold green] total on storage")
    console.print(f"[bold cyan]Active RAM Budget:[/bold cyan] [bold magenta]{budget_gb} GB hard limit[/bold magenta]")
    console.print(
        "[bold cyan]Task:[/bold cyan] [italic]\"Analyze this scientific paper, reproduce its numerical result, "
        "write the implementation, and explain the physical meaning.\"[/italic]\n"
    )

    kernel = CognitiveKernel(catalog=catalog, memory_budget_gb=budget_gb)

    def on_paging(event: PagingEvent):
        color = "green" if event.action == PagingAction.PAGE_IN else ("yellow" if event.action == PagingAction.CACHE_HIT else "red")
        console.print(
            f" [bold {color}][{event.action.value}][/bold {color}] "
            f"Model: [bold white]{event.model_id:<20}[/bold white] "
            f"({event.ram_gb:.1f} GB) — {event.reason} "
            f"[dim]({event.duration_sec:.2f}s)[/dim]"
        )
        print_memory_bar(event.active_memory_gb, budget_gb, total_lib)

    kernel.pager.add_listener(on_paging)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Orchestrating Cognitive Kernel...", total=None)
        summary = kernel.execute_task(
            goal="Analyze this scientific paper, reproduce its numerical result, write the implementation, and explain the physical meaning.",
            ablation_mode=AblationMode.D_FULL_MODELVM,
        )

    console.print("\n[bold green][OK] TASK EXECUTION COMPLETED SUCCESSFULLY[/bold green]\n")

    # Results Table
    table = Table(title="Execution Stages & Cognitive State Transitions", border_style="cyan")
    table.add_column("Stage", style="bold cyan", width=6)
    table.add_column("Domain Capability", style="magenta")
    table.add_column("Model Paged In", style="white")
    table.add_column("Footprint", justify="right")
    table.add_column("Action", style="yellow")
    table.add_column("Confidence", justify="right", style="green")

    for s in summary.stage_results:
        table.add_row(
            str(s.stage_index + 1),
            s.capability.value.upper(),
            s.model_name,
            f"{s.model_ram_gb:.1f} GB",
            s.stage_title,
            f"{s.confidence_score * 100:.0f}%",
        )
    console.print(table)

    # Final summary box
    summary_box = (
        f"[bold white]Available Model Capability:[/bold white] [bold cyan]{summary.total_library_size_gb:.1f} GB[/bold cyan]\n"
        f"[bold white]Peak Active Memory Used:[/bold white]   [bold magenta]{summary.peak_resident_memory_gb:.1f} / {budget_gb:.1f} GB[/bold magenta]\n"
        f"[bold white]Physical Memory Savings:[/bold white]   [bold green]{summary.memory_savings_ratio * 100:.1f}%[/bold green]\n"
        f"[bold white]Cognitive Capability Density:[/bold white] [bold yellow]{summary.capability_density:.2f}[/bold yellow]\n"
        f"[bold white]Total Runtime (with Paging):[/bold white] [bold white]{summary.total_duration_sec:.2f}s[/bold white]"
    )
    console.print(Panel(summary_box, title="[bold green]ModelVM Metric Verification[/bold green]", border_style="green"))


def run_benchmark(budget_gb: float = 8.0) -> None:
    """Runs the 4-mode Critical Ablation Study."""
    render_banner()
    console.print("\n[bold yellow]═══ RUNNING CRITICAL ABLATION STUDY (PDR SECTION 13) ═══[/bold yellow]")
    console.print("[dim]Evaluating: A. Static Router | B. Dynamic Loading | C. Dynamic + CSP | D. Full ModelVM[/dim]\n")

    runner = AblationStudyRunner(memory_budget_gb=budget_gb)
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("[cyan]Running 4-configuration benchmark...", total=None)
        report = runner.run_study()

    table = Table(title="Critical Ablation Study Results", border_style="cyan")
    table.add_column("Configuration", style="bold cyan")
    table.add_column("Peak RAM", justify="right")
    table.add_column("Memory Savings", justify="right", style="green")
    table.add_column("Quality Coverage", justify="right", style="magenta")
    table.add_column("Cap. Density", justify="right", style="yellow")
    table.add_column("Overhead", justify="right")
    table.add_column("Facts Preserved", justify="right")
    table.add_column("Calculations", justify="right")

    for mode_name, m in report.runs.items():
        name_clean = mode_name.replace("_", " ")
        table.add_row(
            name_clean,
            f"{m.peak_memory_gb:.1f} GB",
            f"{m.memory_savings_percent:.1f}%",
            f"{m.capability_coverage_score * 100:.0f}%",
            f"{m.capability_density:.2f}",
            f"{m.paging_overhead_sec:.2f}s",
            str(m.facts_preserved),
            str(m.calculations_verified),
        )

    console.print(table)
    console.print(Panel(report.winner_analysis, title="[bold green]Ablation Finding[/bold green]", border_style="green"))


def list_library() -> None:
    """Lists all models in the ModelVM catalog."""
    render_banner()
    catalog = ModelCatalog()
    models = catalog.all_models()

    table = Table(title=f"ModelVM Catalog ({len(models)} Models, {catalog.total_library_size_gb()} GB Total)", border_style="cyan")
    table.add_column("ID", style="bold cyan")
    table.add_column("Model Name", style="white")
    table.add_column("Capabilities", style="magenta")
    table.add_column("RAM Footprint", justify="right", style="green")
    table.add_column("Load Time", justify="right")
    table.add_column("Quality", justify="right", style="yellow")
    table.add_column("Quantization", style="dim")

    for m in models:
        caps = ", ".join(c.value for c in m.capabilities)
        table.add_row(
            m.id,
            m.name,
            caps,
            f"{m.ram_required:.1f} GB",
            f"{m.load_time:.1f}s",
            f"{m.quality * 100:.0f}%",
            m.quantization,
        )

    console.print(table)


def serve_dashboard(port: int = 8000) -> None:
    """Starts the FastAPI Web Dashboard server."""
    render_banner()
    console.print(f"\n[bold green]Launching ModelVM Web Dashboard on http://localhost:{port}[/bold green]")
    import uvicorn
    from modelvm.api.server import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


def main() -> None:
    parser = argparse.ArgumentParser(description="ModelVM: Virtual Memory for Intelligence")
    subparsers = parser.add_subparsers(dest="command")

    # Demo
    demo_parser = subparsers.add_parser("demo", help="Run the winning PDR demonstration")
    demo_parser.add_argument("--budget", type=float, default=8.0, help="RAM budget in GB (default: 8.0)")

    # Run
    run_parser = subparsers.add_parser("run", help="Run a custom task")
    run_parser.add_argument("--task", type=str, required=True, help="Task query")
    run_parser.add_argument("--budget", type=float, default=8.0, help="RAM budget in GB")
    run_parser.add_argument("--mode", type=str, default="D_FULL_MODELVM", choices=[m.value for m in AblationMode])

    # Benchmark
    bench_parser = subparsers.add_parser("benchmark", help="Run the 4-mode Critical Ablation Study")
    bench_parser.add_argument("--budget", type=float, default=8.0, help="RAM budget in GB")

    # Library
    subparsers.add_parser("library", help="List registered models in catalog")

    # Serve
    serve_parser = subparsers.add_parser("serve", help="Launch interactive web visualizer")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")

    args = parser.parse_args()

    if args.command == "demo" or args.command is None:
        budget = getattr(args, "budget", 8.0)
        run_demo(budget_gb=budget)
    elif args.command == "benchmark":
        run_benchmark(budget_gb=args.budget)
    elif args.command == "library":
        list_library()
    elif args.command == "serve":
        serve_dashboard(port=args.port)
    elif args.command == "run":
        kernel = CognitiveKernel(memory_budget_gb=args.budget)
        mode = AblationMode(args.mode)
        summary = kernel.execute_task(goal=args.task, ablation_mode=mode)
        console.print(f"[bold green]Task complete.[/bold green] Peak RAM: {summary.peak_resident_memory_gb} GB, Savings: {summary.memory_savings_ratio*100:.1f}%")


if __name__ == "__main__":
    main()
