"""Core Github config Class
"""

# Copyright (C) 1999-2021 Jerome Erasmus
# Written by Jerome Erasmus

from dotenv import dotenv_values
from github import Github

__all__ = ['GithubConfig', 'get_client']


class GithubConfig:
    client = None

    def __init__(self):
        config = dotenv_values()
        self.client = Github(config['GITHUB_TOKEN'], per_page=30)

    def get_client(self, **kwargs):
        """Creates a Github Client configuration
        """
        return self.client