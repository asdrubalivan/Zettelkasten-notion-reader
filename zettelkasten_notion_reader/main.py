import typer
import os
from client import get_client

app = typer.Typer()


@app.command()
def gather_data():
    client = get_client()
    print(client.query_database())


@app.command()
def clear_cache():
    os.remove("http_cache.sqlite")


if __name__ == "__main__":
    app()
