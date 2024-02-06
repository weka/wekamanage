#! /usr/bin/env python3.11

import argparse
import shutil

parser = argparse.ArgumentParser(description='Copy an ISO, but not the dnf repos')
parser.add_argument('source_dir', type=str, help='Source directory (ISO)')
parser.add_argument('dest_dir', type=str, help='Destination directory')
args = parser.parse_args()

def repo_dirs(directory, contents):
    #print(f'directory={directory}, contents={contents}')
    ignore_list = list()
    for item in contents:
        if item in ['Packages', 'repodata']:
            ignore_list.append(item)
    #print(f'ignore_list={ignore_list}')
    return(ignore_list)

shutil.copytree(args.source_dir, args.dest_dir, ignore=repo_dirs, dirs_exist_ok=True)
