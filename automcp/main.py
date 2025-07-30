from typing import Tuple
import click
import os
from automcp import VERSION
from automcp.pipeline import AutoMCP_Pipeline
from automcp.constants import OUTPUT_TEMPLATE
from automcp.utils import safe_name

@click.group()
@click.version_option(VERSION, "-v", "--version")
def cli():
    pass

@cli.command(
    help="Create an MCP server for a given program"
)
@click.option(
    "--program", "-p",
    help="Path to script, CLI, or executable. Can be specified multiple times.",
    required=True,
    multiple=True
)
@click.option("--help_command", "-hc", help="Name of the help command", default="--help")
@click.option("--output", "-o", help="Save path for the MCP server", default="./server.py")
def create(program: Tuple[str, ...], help_command: str, output: str):
    program = list(program)

    if len(program) == 1:
        click.echo(f"Creating MCP server for program: {program[0]}")
    else:
        click.echo(f"Creating MCP server for {len(program)} programs")

    pipeline = AutoMCP_Pipeline()
    server_template = pipeline.run(program, help_command)

    head, _ = os.path.split(output)
    if len(head.strip()) > 0:
        os.makedirs(head, exist_ok=True)
    with open(output, "w") as f:
        f.write(server_template)

    # Full path to the output file
    save_dir = os.path.dirname(os.path.abspath(output))

    click.echo(OUTPUT_TEMPLATE.format(
        server_path=output,
        safe_command_name=safe_name(program[0]) if len(program) == 1 else "my-server",
        save_dir=save_dir,
        output_file_name=os.path.basename(output)
    ))


@cli.command()
@click.option("--mode", "-m", help="Mode to run the server in (stdio, sse, streamable-http)", default='stdio', type=str)
def run(mode):
    """
    Run the AutoMCP Server.
    """
    from automcp.mcp_server import mcp
    click.echo(f"Starting AutoMCP Server...")

    if mode not in ['stdio', 'sse', 'streamable-http']:
        raise ValueError(f"Invalid mode: {mode}")

    mcp.run(transport=mode)

if __name__ == "__main__":
    cli()
