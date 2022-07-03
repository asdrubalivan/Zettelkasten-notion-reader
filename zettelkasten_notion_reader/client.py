from pydantic import BaseSettings, SecretStr
import requests_cache
from datetime import timedelta, datetime
from dataclasses import dataclass, asdict
from typing import List
import networkx as nx
import itertools as it

__all__ = ["get_client"]


@dataclass(frozen=True)
class Zettel:
    id: str
    title: str
    url: str
    links_to: List[str]
    tags: List[str]
    last_edited: str

    def to_dict(self):
        return asdict(self)


class _Settings(BaseSettings):
    notion_token: SecretStr
    notion_database_id: SecretStr


class NotionClient:
    def __init__(self, settings):
        self.settings = settings
        self.requests = requests_cache.session.CachedSession(
            allowable_methods=("GET", "POST", "HEAD"),
            expire_after=timedelta(hours=3),
        )

    @property
    def database_id(self):
        return self.settings.notion_database_id.get_secret_value()

    @property
    def token(self):
        return self.settings.notion_token.get_secret_value()

    def query_database(self, query=None):
        url = f"https://api.notion.com/v1/databases/{self.database_id}/query"

        r = self.requests.post(
            url,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": "2021-08-16",
            },
        )

        result_dict = r.json()

        return result_dict

    def get_graphs(self, query=None):
        data = self.query_database(query)
        return create_graphs(data["results"])


def get_client():
    return NotionClient(_Settings(_env_file=".env"))


def generate_title(title_obj):
    def generator():
        for val in title_obj:
            yield_plain_text = True
            type_ = val["type"]
            if type_ == "mention":
                if val["mention"]["type"] == "date":
                    start = val["mention"]["date"]["start"]
                    yield datetime.fromisoformat(start).strftime("%m/%d/%Y, %H:%M:%S")
                    yield_plain_text = False

            if yield_plain_text:
                yield val["plain_text"].strip()

    return " | ".join(generator())


def map_graph(page):
    properties = page["properties"]
    title = generate_title(properties["Name"]["title"])
    links_to = [r["id"] for r in properties["links to"]["relation"]]
    tags = [t["name"] for t in properties["Areas & Topics"]["multi_select"]]
    return Zettel(
        id=page["id"],
        title=title,
        last_edited=page["last_edited_time"],
        url=page["url"],
        links_to=links_to,
        tags=tags,
    )


def create_graphs(pages):
    ordered_pages = {p["id"]: map_graph(p) for p in pages}

    graph = nx.Graph()
    add_node = graph.add_node
    for key, data in ordered_pages.items():
        add_node(
            key,
            data=data.to_dict(),
            title=data.title,
            label=data.title,
        )

    graph.add_edges_from(
        it.chain.from_iterable(
            zip(it.repeat(node.id), node.links_to) for node in ordered_pages.values()
        )
    )

    return graph
