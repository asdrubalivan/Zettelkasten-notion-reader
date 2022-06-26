import typer
from client import get_client

app = typer.Typer()


@app.command()
def gather_data():
    client = get_client()
    print(client.query_database())


if __name__ == "__main__":
    app()
