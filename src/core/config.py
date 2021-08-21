"""Core config Class
"""

# Copyright (C) 1999-2021 Jerome Erasmus
# Written by Jerome Erasmus

from dotenv import dotenv_values
from github import Github
from jira import JIRA

__all__ = ['CommandsConfig']


class CommandsConfig:
    config = None
    github_client = None
    jira_client = None

    def __init__(self):
        self.config = dotenv_values()
        self.github_client = Github(self.config['GITHUB_TOKEN'], per_page=30)
        self.jira_client = JIRA(self.config['JIRA_TOKEN'])
