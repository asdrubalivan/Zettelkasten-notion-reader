import typer
import os
from client import get_client
from pyvis.network import Network

app = typer.Typer()


@app.command()
def gather_data():
    client = get_client()
    print(client.query_database())


@app.command()
def create_graphs():
    client = get_client()
    nx_graph = client.get_graphs()
    nt = Network("2000px", "2000px")
    nt.show_buttons(filter_=["physics"])
    nt.from_nx(nx_graph)
    nt.show("nx.html")


@app.command()
def clear_cache():
    os.remove("http_cache.sqlite")


if __name__ == "__main__":
    app()
