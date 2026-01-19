"""
Test Runner for MS Portfolio AI Demo

This script executes demo prompts through the multi-agent system and
captures full response chains for review and iteration.

Usage:
    python tests/test_runner.py --project project1
    python tests/test_runner.py --project project2
    python tests/test_runner.py --all
    python tests/test_runner.py --project project2 --step P2_STEP3
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from demo_prompts import ALL_DEMO_PROMPTS, get_project_prompts

# Configuration
MODEL = "claude-sonnet-4-20250514"
OUTPUT_DIR = Path(__file__).parent / "outputs"


class DemoTestRunner:
    """Executes demo prompts and captures full agent interaction chains."""

    def __init__(self, project_key: str):
        self.project_key = project_key
        self.project_config = ALL_DEMO_PROMPTS[project_key]
        self.results = {
            "project_name": self.project_config["name"],
            "scenario": self.project_config["scenario"],
            "test_run_timestamp": datetime.now().isoformat(),
            "model": MODEL,
            "steps": []
        }

        # Initialize orchestrator based on project
        self.orchestrator = None
        self._initialize_orchestrator()

    def _initialize_orchestrator(self):
        """Initialize the appropriate orchestrator for the project."""
        if self.project_key == "project1":
            from agents.project1 import CoordinatorAgent
            self.orchestrator = CoordinatorAgent()
        else:
            from agents.project2 import StrategicPlanningAgent
            self.orchestrator = StrategicPlanningAgent()

    def run_step(self, step_config: dict) -> dict:
        """Execute a single demo step and capture results."""

        step_result = {
            "step_id": step_config["step_id"],
            "step_name": step_config["step_name"],
            "description": step_config["description"],
            "prompt": step_config["prompt"],
            "expected_agents": step_config.get("expected_agents", []),
            "timestamp_start": datetime.now().isoformat(),
            "agent_chain": [],
            "final_output": None,
            "validation": {
                "expected_content_found": [],
                "expected_content_missing": []
            }
        }

        print(f"\n{'='*60}")
        print(f"STEP: {step_config['step_name']}")
        print(f"{'='*60}")
        print(f"Prompt: {step_config['prompt'][:150]}...")

        # Skip system handoff steps (these are just notes for the demo flow)
        if step_config["prompt"].startswith("[SYSTEM:"):
            step_result["final_output"] = "[SKIPPED - System handoff step for demo flow]"
            step_result["timestamp_end"] = datetime.now().isoformat()
            print(f"\nSKIPPED: This is a demo flow notation step")
            return step_result

        # Execute through orchestrator
        try:
            response = self.orchestrator.invoke(step_config["prompt"])

            # Build agent chain from response
            agent_chain_entry = {
                "agent_name": response.agent_name,
                "agent_name_en": response.agent_name_en,
                "thinking": response.thinking,
                "metadata": response.metadata,
                "timestamp": datetime.now().isoformat()
            }
            step_result["agent_chain"].append(agent_chain_entry)
            step_result["final_output"] = response.content
            step_result["timestamp_end"] = datetime.now().isoformat()

            # Validate expected content
            if "expected_output_contains" in step_config:
                for expected in step_config["expected_output_contains"]:
                    if expected.lower() in response.content.lower():
                        step_result["validation"]["expected_content_found"].append(expected)
                    else:
                        step_result["validation"]["expected_content_missing"].append(expected)

            print(f"\nAgent: {response.agent_name} ({response.agent_name_en})")
            print(f"Output length: {len(response.content)} characters")
            print(f"Validation: {len(step_result['validation']['expected_content_found'])} found, "
                  f"{len(step_result['validation']['expected_content_missing'])} missing")

            if step_result['validation']['expected_content_missing']:
                print(f"Missing: {step_result['validation']['expected_content_missing']}")

        except Exception as e:
            step_result["error"] = str(e)
            step_result["timestamp_end"] = datetime.now().isoformat()
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

        return step_result

    def run_all_steps(self):
        """Execute all steps in sequence."""
        print(f"\n{'#'*60}")
        print(f"PROJECT: {self.project_config['name']}")
        print(f"{'#'*60}")
        print(f"Scenario: {self.project_config['scenario']}")

        for step_config in self.project_config["steps"]:
            step_result = self.run_step(step_config)
            self.results["steps"].append(step_result)

        return self.results

    def run_single_step(self, step_id: str):
        """Execute a single step by ID."""
        for step_config in self.project_config["steps"]:
            if step_config["step_id"] == step_id:
                step_result = self.run_step(step_config)
                self.results["steps"].append(step_result)
                return self.results

        raise ValueError(f"Step '{step_id}' not found in project '{self.project_key}'")

    def save_results(self) -> Path:
        """Save results to JSON file."""
        OUTPUT_DIR.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.project_key}_demo_run_{timestamp}.json"
        filepath = OUTPUT_DIR / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*60}")
        print(f"Results saved to: {filepath}")
        print(f"{'='*60}")

        return filepath

    def generate_summary_report(self) -> str:
        """Generate a human-readable summary of the test run."""

        lines = [
            "=" * 70,
            f"DEMO TEST RUN SUMMARY",
            f"Project: {self.results['project_name']}",
            f"Timestamp: {self.results['test_run_timestamp']}",
            f"Model: {self.results['model']}",
            "=" * 70,
            "",
            "STEP RESULTS:",
            "-" * 70,
        ]

        for step in self.results["steps"]:
            has_error = step.get("error")
            has_missing = len(step["validation"].get("expected_content_missing", [])) > 0

            if has_error:
                status = "X ERROR"
            elif has_missing:
                status = "! ISSUES"
            else:
                status = "* PASS"

            lines.append(f"\n{step['step_id']}: {step['step_name']}")
            lines.append(f"  Status: {status}")

            if step.get("agent_chain"):
                agents = [a.get('agent_name_en') or a.get('agent_name') for a in step['agent_chain']]
                lines.append(f"  Agents: {' -> '.join(agents)}")

            if has_error:
                lines.append(f"  Error: {step['error']}")
            elif step.get("final_output"):
                lines.append(f"  Output length: {len(step['final_output'])} chars")

                if has_missing:
                    lines.append(f"  Missing expected content: {step['validation']['expected_content_missing']}")

            lines.append("-" * 70)

        lines.append("")
        lines.append("FULL OUTPUTS:")
        lines.append("=" * 70)

        for step in self.results["steps"]:
            lines.append(f"\n{'#'*70}")
            lines.append(f"# {step['step_id']}: {step['step_name']}")
            lines.append(f"{'#'*70}")
            lines.append(f"\nPROMPT:\n{step['prompt']}")

            if step.get('agent_chain'):
                lines.append(f"\nAGENT CHAIN:")
                for agent in step['agent_chain']:
                    name = agent.get('agent_name_en') or agent.get('agent_name')
                    lines.append(f"  - {name}")
                    if agent.get('thinking'):
                        thinking_preview = agent['thinking'][:300] + "..." if len(agent['thinking']) > 300 else agent['thinking']
                        lines.append(f"    Thinking: {thinking_preview}")

            lines.append(f"\nOUTPUT:\n{step.get('final_output', 'NO OUTPUT')}")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run demo tests for MS Portfolio AI")
    parser.add_argument(
        "--project",
        choices=["project1", "project2", "all"],
        default="all",
        help="Which project to test"
    )
    parser.add_argument(
        "--step",
        type=str,
        default=None,
        help="Run a specific step by ID (e.g., P2_STEP3)"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print summary, don't save full JSON"
    )
    parser.add_argument(
        "--no-summary-file",
        action="store_true",
        help="Don't save summary to text file"
    )

    args = parser.parse_args()

    # Determine projects to test
    if args.project == "all":
        projects_to_test = ["project1", "project2"]
    else:
        projects_to_test = [args.project]

    for project_key in projects_to_test:
        print(f"\n{'*'*70}")
        print(f"* STARTING TEST: {project_key}")
        print(f"{'*'*70}")

        runner = DemoTestRunner(project_key)

        # Run tests
        if args.step:
            runner.run_single_step(args.step)
        else:
            runner.run_all_steps()

        # Save results
        if not args.summary_only:
            runner.save_results()

        # Print summary
        summary = runner.generate_summary_report()
        print(summary)

        # Save summary as text file
        if not args.summary_only and not args.no_summary_file:
            OUTPUT_DIR.mkdir(exist_ok=True)
            summary_path = OUTPUT_DIR / f"{project_key}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(summary)
            print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
