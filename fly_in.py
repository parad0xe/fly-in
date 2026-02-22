import logging

import arcade
from rich.console import Console
from rich.table import Table

from flyin.arguments import Args
from flyin.exceptions.base import FlyInError
from flyin.io.file_loader import GraphFileLoader
from flyin.logging import LoggingSystem
from flyin.models.graph import Graph
from flyin.renderer import GraphWindow

logger: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    args = Args.parse_arguments()

    LoggingSystem.global_setup(args)

    # load data from file
    # validate data from file
    # create graph
    try:
        graph = GraphFileLoader.load(args.file)
    except FlyInError as e:
        logger.exception(e)
        exit(1)
    except Exception as e:
        logger.exception(e)
        exit(2)

    print_graph_summary(graph)

    window = GraphWindow.load(graph)

    arcade.run()
    # render graph
    # update graph (+render graph)
    # create solutions


def print_graph_summary(graph: Graph) -> None:
    """Display the graph structure and metadata in a terminal table."""
    console = Console()

    # Information générale sur les points d'entrée/sortie
    console.print(f"[bold green]Start Hub:[/] {graph.start_hub.name}")
    console.print(f"[bold red]End Hub:[/] {graph.end_hub.name}\n")

    table = Table(
        title="Network Nodes", show_header=True, header_style="bold cyan"
    )
    table.add_column("Hub")
    table.add_column("Pos (X,Y)")
    table.add_column("Type")
    table.add_column("Connections")

    for hub in graph.hubs:
        # Formatage des connexions : 'Voisin (Capacité)'
        conns = ", ".join(
            [
                f"{hub.name} <-> {peer.name} (drone: {link.drones}) (max: {link.max_link_capacity})"
                for peer, link in hub.links
            ]
        )

        node_type = "Leaf" if hub.is_leaf else "Node"
        table.add_row(
            f"{hub.name} (drones: {hub.drones}) (max: {hub.max_drones})",
            f"{hub.x},{hub.y}",
            node_type,
            conns,
        )

    console.print(table)


if __name__ == "__main__":
    main()
