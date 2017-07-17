#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
import sys
import math
import datetime
import argparse
import tempfile
import os
import json
import stat
from git import Repo

def main():
    parser = argparse.ArgumentParser(description='Find secrets hidden in the depths of git.')
    parser.add_argument('--json', dest="output_json", action="store_true", help="Output in JSON")
    parser.add_argument('--search', dest="search", action="store", help="Terms to look for", default=None)
    parser.add_argument('git_url', type=str, help='URL for secret searching')
    args = parser.parse_args()

    if not args.search:
        parser.print_help()
        sys.exit(-1)

    output = find_strings(args.git_url, args.search, args.output_json)
    project_path = output["project_path"]
    shutil.rmtree(project_path, onerror=del_rw)


def del_rw(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def find_strings(git_url, search, printJson=False):
    project_path = tempfile.mkdtemp()
    Repo.clone_from(git_url, project_path)
    output = {"entropicDiffs": []}
    repo = Repo(project_path)
    already_searched = set()

    for remote_branch in repo.remotes.origin.fetch():
        branch_name = str(remote_branch).split('/')[1]
        try:
            repo.git.checkout(remote_branch, b=branch_name)
        except:
            pass

        prev_commit = None
        for curr_commit in repo.iter_commits():
            if not prev_commit:
                pass
            else:
                #avoid searching the same diffs
                hashes = str(prev_commit) + str(curr_commit)
                if hashes in already_searched:
                    prev_commit = curr_commit
                    continue
                already_searched.add(hashes)

                diff = prev_commit.diff(curr_commit, create_patch=True)
                for blob in diff:
                    #print i.a_blob.data_stream.read()
                    printableDiff = blob.diff.decode('utf-8', errors='replace')
                    if printableDiff.startswith("Binary files"):
                        continue
                    stringsFound = []
                    lines = blob.diff.decode('utf-8', errors='replace').split("\n")
                    for line in lines:
                        if search in line:
                            stringsFound.append(line)
                            printableDiff = printableDiff.replace(line, bcolors.WARNING + line + bcolors.ENDC)

                    if len(stringsFound) > 0:
                        commit_time =  datetime.datetime.fromtimestamp(prev_commit.committed_date).strftime('%Y-%m-%d %H:%M:%S')
                        entropicDiff = {}
                        entropicDiff['date'] = commit_time
                        entropicDiff['branch'] = branch_name
                        entropicDiff['commit'] = prev_commit.message
                        entropicDiff['diff'] = blob.diff.decode('utf-8', errors='replace') 
                        entropicDiff['stringsFound'] = stringsFound
                        output["entropicDiffs"].append(entropicDiff)
                        if printJson:
                            print(json.dumps(output, sort_keys=True, indent=4))
                        else:
                            print(bcolors.OKGREEN + "Date: " + commit_time + bcolors.ENDC)
                            print(bcolors.OKGREEN + "Branch: " + branch_name + bcolors.ENDC)
                            print(bcolors.OKGREEN + "Commit: " + prev_commit.message + bcolors.ENDC)
                            print(bcolors.OKGREEN + "SHA-1: " + prev_commit.hexsha + bcolors.ENDC)
                            print(printableDiff)

            prev_commit = curr_commit
    output["project_path"] = project_path
    return output

if __name__ == "__main__":
    main()