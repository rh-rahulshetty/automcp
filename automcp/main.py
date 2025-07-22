import click
import os
from automcp import VERSION
from automcp.pipeline import AutoMCP_Pipeline
from automcp.mcp_server import mcp
from automcp.constants import OUTPUT_TEMPLATE
from automcp.utils import safe_name

@click.group()
@click.version_option(VERSION, "-v", "--version")
def cli():
    pass

@cli.command()
@click.option("--program", "-p", help="Path to script, CLI, or executable", required=True)
@click.option("--help_command", "-hc", help="Name of the help command", default="--help")
@click.option("--output", "-o", help="Save path for the MCP server", default="./server.py")
def create(program, help_command, output):
    click.echo(f"Creating MCP server for project: {program}")

    pipeline = AutoMCP_Pipeline()
    server_template = pipeline.run(program, help_command)

    head, _ = os.path.split(output)
    os.makedirs(head, exist_ok=True)
    with open(output, "w") as f:
        f.write(server_template)

    # Full path to the output file
    save_dir = os.path.dirname(os.path.abspath(output))

    click.echo(OUTPUT_TEMPLATE.format(
        server_path=output,
        safe_command_name=safe_name(program),
        save_dir=save_dir,
        output_file_name=os.path.basename(output)
    ))


@cli.command()
def run():
    """
    Run the AutoMCP Server.
    """
    click.echo(f"Starting AutoMCP Server...")
    mcp.run()

@cli.command()
def gateway():
    """
    Run the MCP Gateway.
    """
    click.echo("Starting MCP Gateway...")
    import os
    os.system("mcpgateway --host 0.0.0.0 --port 4444")

if __name__ == "__main__":
    cli()
