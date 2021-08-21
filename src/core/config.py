"""Core Github config Class
"""

# Copyright (C) 1999-2021 Jerome Erasmus
# Written by Jerome Erasmus


from github import Github

__all__ = ['GithubConfig', 'get_client']


class GithubConfig:
    client = None

    def __init__(self):
        self.client = Github("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", per_page=30)

    def get_client(self, **kwargs):
        """Creates a Github Client configuration
        """
        return self.client