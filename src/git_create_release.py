#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Github Create Release
# @raycast.mode fullOutput
# @raycast.packageName Github

# Optional parameters:
# @raycast.icon ''
# @raycast.argument1 { "type": "text", "placeholder": "parameter key", "optional": false}

# Documentation:
# @raycast.description Github Create Release
# @raycast.author Jerome Erasmus
# @raycast.authorURL https://github.com/JeromeErasmus

import sys
import re
import json
from core.config import CommandsConfig
from datetime import datetime
from itertools import groupby
from jira import JIRA, JIRAError

github_client = CommandsConfig().get_github_client()
jira_client = CommandsConfig().get_jira_client()
repo_name = "caradvice/drive-boot"


def main(*args):
    release = get_last_release()

    if not release:
        print('Error. Previous release not found')
        return False

    if release.prerelease:
        print('Previous release is a PreRelease. Publish the previous release')
        return False

    issues = create_issues_list(release)
    grouped_issues = group_issues_list(issues)
    print(json.dumps(grouped_issues))
    

def create_issues_list(release):
    issues = []
    
    for issue in search_issues(release):
        ticket_key = extract_ticket(issue.title)
        lable_name = extract_lable(issue.title)

        issues.append(dict(
            number=issue.number,
            title=issue.title,
            ticket_key=ticket_key,
            lable_name=lable_name,
        ))

    return issues


def group_issues_list(issues):
    sorted_issues = sorted(issues, key=sort_key_func)
    grouped = dict()

    for key, value in groupby(sorted_issues, sort_key_func):
        grouped[key] = dict(children=list(value), ticket_key=key)
    
    for key in grouped:
        issue = grouped[key]
        
        jira_issue = get_jira_issue(issue['ticket_key'])
        
        if not jira_issue:
            issue['valid_issue'] = False
            summary = []
            for child in issue['children']:
                summary.append(child['lable_name'])

            issue['issue_summary'] = ', '.join(summary)
        else:
            issue['valid_issue'] = True
            issue['issue_summary'] = jira_issue.fields.summary

    return grouped


def get_jira_issue(ticket_key):
    try:
        issue = jira_client.issue(ticket_key)
        if issue:
            return issue
    except JIRAError as error:
        pass

    return None

def extract_ticket(string):
    ticket_label = re.search(r"(?<=\[)(.*?)(?=\])", string)

    if ticket_label:
        return ticket_label.group(0).lstrip().rstrip()
    else:
        return ''


def extract_lable(string):
    index = string.rfind(']')

    if index != -1:
        return string[index+1:].lstrip().capitalize()
    else:
        return ''


def get_jira_ticket():
    pass


def search_issues(release):
    date = release.published_at.strftime('%Y-%m-%dT%H:%M:%S')
    query = 'repo:{0} type:pr merged:>{1}'.format(repo_name, date)
    return github_client.search_issues(query=query)


def sort_key_func(k):
    return k['ticket_key']


def get_last_release(*args):
    repo = github_client.get_repo(repo_name)
    repos = repo.get_releases()

    if repos and repos[0]:
        return repos[0]

    return False


if len(sys.argv) > 1:
    main(sys.argv[1])
else:
    main(None)

exit(0)
