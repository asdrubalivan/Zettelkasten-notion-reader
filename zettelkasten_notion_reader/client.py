from pydantic import BaseSettings, SecretStr
import requests_cache

__all__ = ["settings"]


class _Settings(BaseSettings):
    notion_token: SecretStr
    notion_database_id: SecretStr


class NotionClient:
    def __init__(self, settings):
        self.settings = settings
        self.requests = requests_cache.session.CachedSession(
            allowable_methods=("GET", "POST", "HEAD")
        )

    @property
    def database_id(self):
        return self.settings.notion_database_id.get_secret_value()

    @property
    def token(self):
        return self.settings.notion_token.get_secret_value()

    def query_database(self):
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


def get_client():
    return NotionClient(_Settings(_env_file=".env"))
