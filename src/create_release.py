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
from core.config import GithubConfig
from datetime import datetime

client = GithubConfig().get_client()
repo_name = "caradvice/drive-boot"
repo = client.get_repo(repo_name)

def create_release(*args):
    release = get_last_release()
    pulls = []
    if not release:
        print('Error. Previous release not found')
        return False

    if release.prerelease:
        print('Previous release is a PreRelease. Publish the previous release')
        return False

    for issue in search_issues(release):
        ticket_name = extract_ticket(issue.title)
        lable_name = extract_lable(issue.title)
        pulls.append(dict(
            issue=issue.number,
            title=issue.title,
            ticket_name=ticket_name,
            lable_name=lable_name
            ))
    
    print(json.dumps(pulls))


def extract_ticket(string):
    ticket_label = re.search(r"(?<=\[)(.*?)(?=\])", string)
    
    if ticket_label:
        return ticket_label.group(0)
    else:
        return None


def extract_lable(string):
    index = string.rfind(']')

    if index != -1:
        return string[index+1:].lstrip().capitalize()
    else:
        return None


def get_jira_ticket():
    pass     
    
def search_issues(release):
    date = release.published_at.strftime('%Y-%m-%dT%H:%M:%S')
    query = 'repo:{0} type:pr merged:>{1}'.format(repo_name, date)
    return client.search_issues(query=query)


def get_last_release(*args):
    repos = repo.get_releases()

    if repos and repos[0]:
        return repos[0]

    return False


if len(sys.argv) > 1:
    create_release(sys.argv[1])
else:
    create_release(None)

exit(0)
