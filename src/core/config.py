"""Core config Class
"""

# Copyright (C) 1999-2021 Jerome Erasmus
# Written by Jerome Erasmus

from dotenv import dotenv_values
from github import Github
from jira import JIRA

__all__ = ['CommandsConfig', 'get_github_client', 'get_jira_client']


class CommandsConfig:
    config = None
    github_client = None
    jira_client = None
    github_repo = None
    github_branch = None

    def __init__(self, **kwargs):
      
        self.config = dotenv_values()
        self.github_client = Github(self.config['GITHUB_TOKEN'], per_page=30)
        self.jira_client = JIRA(server=self.config['JIRA_SERVER'], basic_auth=(self.config['JIRA_USER_EMAIL'],
                                                                               self.config['JIRA_TOKEN']))
        if kwargs['repository']:
            self.github_repo = kwargs['repository']
        else:
            self.github_repo = self.config['GITHUB_DEFAULT_REPOSITORY']

        if kwargs['branch']:
            self.github_branch= kwargs['branch']
        else:
            self.github_branch = self.config['GITHUB_DEFAULT_BRANCH']
        

    def get_github_client(self, **kwargs):
        """Gets a Github Client configuration
        """
        return self.github_client

    def get_jira_client(self, **kwargs):
        """Gets a Jira Client configuration
        """
        return self.jira_client
