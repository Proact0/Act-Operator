#!/usr/bin/env python3
"""Generate graph visualizations.

This script generates Mermaid diagrams and ASCII representations of LangGraph graphs.
Useful for documentation and understanding graph flow.

Usage:
    python visualize_graph.py <cast_name>
    python visualize_graph.py my_cast --format mermaid
    python visualize_graph.py my_cast --output graph.md
"""

import argparse
import importlib
import sys
from pathlib import Path
from typing import Any, Optional


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


class GraphVisualizer:
    """Generates visualizations of LangGraph graphs."""

    def __init__(self, cast_name: str, output_format: str = "mermaid"):
        """Initialize the visualizer.

        Args:
            cast_name: Name of the cast to visualize
            output_format: Output format (mermaid, ascii, both)
        """
        self.cast_name = cast_name
        self.output_format = output_format
        self.graph = None

    def load_graph(self) -> bool:
        """Load the graph from the cast module.

        Returns:
            True if successful, False otherwise
        """
        try:
            module = importlib.import_module(f"casts.{self.cast_name}.graph")
            print(f"{Colors.GREEN}✓{Colors.END} Loaded module: casts.{self.cast_name}.graph")

            # Find graph instance
            graph_instance = None
            for name in dir(module):
                obj = getattr(module, name)
                if hasattr(obj, "build") and not isinstance(obj, type):
                    graph_instance = obj
                    break

            if not graph_instance:
                print(
                    f"{Colors.RED}✗{Colors.END} No graph instance found with build() method"
                )
                return False

            print(f"{Colors.GREEN}✓{Colors.END} Found graph instance")

            # Build the graph
            self.graph = graph_instance.build()
            print(f"{Colors.GREEN}✓{Colors.END} Graph compiled successfully")

            return True

        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Failed to load graph: {str(e)}")
            return False

    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram of the graph.

        Returns:
            Mermaid diagram as string
        """
        if not self.graph:
            return "Error: Graph not loaded"

        lines = ["```mermaid", "graph TD"]

        # Get nodes from graph
        if hasattr(self.graph, "nodes"):
            nodes = self.graph.nodes
            
            # Add nodes
            for node_name in nodes:
                # Clean node name for Mermaid
                clean_name = node_name.replace(" ", "_").replace("-", "_")
                display_name = node_name
                lines.append(f"    {clean_name}[{display_name}]")

            # Add edges
            if hasattr(self.graph, "_graph"):
                graph_dict = self.graph._graph
                
                for source, targets in graph_dict.items():
                    source_clean = source.replace(" ", "_").replace("-", "_")
                    
                    if isinstance(targets, dict):
                        for target in targets.values():
                            target_clean = target.replace(" ", "_").replace("-", "_")
                            lines.append(f"    {source_clean} --> {target_clean}")
                    elif isinstance(targets, list):
                        for target in targets:
                            target_clean = target.replace(" ", "_").replace("-", "_")
                            lines.append(f"    {source_clean} --> {target_clean}")
                    else:
                        target_clean = targets.replace(" ", "_").replace("-", "_")
                        lines.append(f"    {source_clean} --> {target_clean}")

        lines.append("```")
        return "\n".join(lines)

    def generate_ascii(self) -> str:
        """Generate ASCII representation of the graph.

        Returns:
            ASCII diagram as string
        """
        if not self.graph:
            return "Error: Graph not loaded"

        lines = ["Graph Structure:", "=" * 50]

        # Get nodes
        if hasattr(self.graph, "nodes"):
            nodes = list(self.graph.nodes.keys())
            lines.append(f"\nNodes ({len(nodes)}):")
            for node in nodes:
                lines.append(f"  - {node}")

        # Get edges
        if hasattr(self.graph, "_graph"):
            lines.append(f"\nEdges:")
            graph_dict = self.graph._graph
            
            for source, targets in graph_dict.items():
                if isinstance(targets, dict):
                    for condition, target in targets.items():
                        lines.append(f"  {source} --[{condition}]--> {target}")
                elif isinstance(targets, list):
                    for target in targets:
                        lines.append(f"  {source} --> {target}")
                else:
                    lines.append(f"  {source} --> {targets}")

        lines.append("=" * 50)
        return "\n".join(lines)

    def visualize(self, output_file: Optional[str] = None) -> str:
        """Generate visualization.

        Args:
            output_file: Optional file path to write output

        Returns:
            Visualization as string
        """
        print(f"\n{Colors.BOLD}Generating Visualization: {self.cast_name}{Colors.END}\n")

        if not self.load_graph():
            return "Failed to load graph"

        # Generate visualization
        output = ""

        if self.output_format in ["mermaid", "both"]:
            print(f"\n{Colors.BOLD}Mermaid Diagram:{Colors.END}\n")
            mermaid = self.generate_mermaid()
            output += mermaid + "\n\n"
            print(mermaid)

        if self.output_format in ["ascii", "both"]:
            print(f"\n{Colors.BOLD}ASCII Representation:{Colors.END}\n")
            ascii_rep = self.generate_ascii()
            output += ascii_rep + "\n"
            print(ascii_rep)

        # Write to file if specified
        if output_file:
            try:
                Path(output_file).write_text(output)
                print(
                    f"\n{Colors.GREEN}✓{Colors.END} Wrote visualization to: {output_file}"
                )
            except Exception as e:
                print(f"\n{Colors.RED}✗{Colors.END} Failed to write file: {str(e)}")

        return output


def main():
    """Main entry point for the visualization script."""
    parser = argparse.ArgumentParser(
        description="Generate graph visualizations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python visualize_graph.py my_cast
  python visualize_graph.py my_cast --format mermaid
  python visualize_graph.py my_cast --format ascii
  python visualize_graph.py my_cast --format both --output graph.md
        """,
    )
    parser.add_argument("cast_name", help="Name of the cast to visualize")
    parser.add_argument(
        "-f",
        "--format",
        choices=["mermaid", "ascii", "both"],
        default="mermaid",
        help="Output format (default: mermaid)",
    )
    parser.add_argument(
        "-o", "--output", help="Output file path (optional)", default=None
    )

    args = parser.parse_args()

    visualizer = GraphVisualizer(args.cast_name, output_format=args.format)
    visualizer.visualize(output_file=args.output)


if __name__ == "__main__":
    main()
