#!/usr/bin/env python3

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Github Create Release
# @raycast.mode fullOutput
# @raycast.packageName Github

# Optional parameters:
# @raycast.icon ''
# @raycast.argument1 { "type": "text", "placeholder": "repository", "optional": true}
# @raycast.argument2 { "type": "text", "placeholder": "branch", "optional": true}

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
from github import GithubException
from core.functions import Functions, Fontcol

config = None
github_client = None
jira_client = None
repo = None


def main(*args):
    global config, github_client, jira_client, repo

    config = CommandsConfig(repository=args[0], branch=args[1])
    github_client = config.get_github_client()
    jira_client = config.get_jira_client()
  
    repo = get_repository()
    last_release = get_last_release()

    if not last_release:
        print('Error. Previous release not found')
        return False

    if last_release.prerelease:
        print('Previous release is a PreRelease. Publish the previous release')
        return False

    issues = create_issues_list(last_release)
    grouped_issues = group_issues_list(issues)
    notes = format_notes(grouped_issues)
    create_release(last_release, notes)

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
        else:
            issue['valid_issue'] = True
            issue['issue_summary'] = jira_issue.fields.summary

    return grouped

def format_notes(issues):
    notes = []
    for key in issues:
        issue = issues[key]
        
        summary = []
        numbers = []
        for child in issue['children']:
            numbers.append(str(child['number']))
        
        if not issue['valid_issue']:
            for child in issue['children']:
                summary.append(child['lable_name'])
        else:
            summary = [issue['issue_summary']]
        
        notes.append("#{0} [{1}] {2} \n\r".format(
            ' #'.join(numbers),
            issue['ticket_key'],
            ', '.join(summary),
            )
        )
    return ''.join(notes)


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


def search_issues(release):
    date = release.published_at.strftime('%Y-%m-%dT%H:%M:%S')
    query = 'repo:{0} type:pr merged:>{1}'.format(config.github_repo, date)
    
    try:
        result = github_client.search_issues(query=query)
        return result
    except GithubException as error:
        print(error)

    return False

def sort_key_func(k):
    return k['ticket_key']


def get_repository():
    
    try:
        repo = github_client.get_repo(config.github_repo)
        if repo:
            return repo
    except GithubException as error:
        print(error)
    
    return False

def get_last_release():
    try:
        releases = repo.get_releases()
        if releases and releases[0]:
            return releases[0]
    except GithubException as error:
        print(error)
    
    return False


def get_branch_head():
    try:
        branch = repo.get_branch(config.github_branch)
        return branch
    except GithubException as error:
        print(error)
    
    return False
    


def create_release(last_release, notes):
    if not last_release:
        print('Error. Last release not found')
        return False
    
    last_tag = last_release.tag_name
    m = int(last_tag[last_tag.rfind('.')+1:]) + 1
    tag = last_tag[:last_tag.rfind('.')+1] + str(m)
    name = "{0}-{1}".format(tag, datetime.today().strftime('%Y-%m-%d'))

    try:
        release = repo.create_git_release(
            tag=tag,
            name=name,
            prerelease=True,
            message=notes,
            target_commitish=config.github_branch
        )

        if release:
            print(Fontcol.YELLOW, 'Version: {0}'.format(name))
            print('Url: {0}'.format(release.html_url))
            print(Fontcol.WHITE, '\n{0}\n{1}'.format('-'*10, notes))
    except GithubException as error:
        print(error)
        return False
    

if len(sys.argv) > 1:
    main(sys.argv[1], sys.argv[2])
else:
    print('Error. Invalid argumnet count')

exit(0)
