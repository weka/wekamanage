#! /usr/bin/env python3.11

# Copyright 2024, WekaIO, Inc.  
# Author: vince@weka.io

import argparse
import glob
import os.path
import shutil
import subprocess

parser = argparse.ArgumentParser(description='Copy an ISO, but not the dnf repos')
parser.add_argument('input_file', type=str, help='Input file of rpms to copy')
parser.add_argument('dest_dir', type=str, help='Destination directory')
parser.add_argument('source_dir', type=str, nargs='+', help='Source directory (ISO)')
parser.add_argument("-v", "--verbose", dest='verbosity', action='store_true', help="enable verbose mode")

args = parser.parse_args()

print(f"input_file is {args.input_file}, dest_dir is {args.dest_dir}, source_dir is {args.source_dir}")

# find_dir - recursively find a directory name
#       returns a list
def find_dir(root_path, dirname):
    subdirs = list()

    path = None
    contents = os.listdir(root_path)
    #print(f"dir={root_path}, contents={contents}")
    if dirname in contents:
        #print("found one")
        path = os.path.join(root_path, dirname)
        if os.path.isdir(path):
            return([path])
    else:
        # if the dir isn't in this directory, make a list of subdirs
        #subdirs = list()
        for name in contents:
            path = os.path.join(root_path, name)
            if os.path.isdir(path):
                subdirs.append(path)
        #print(f'subdirs are {subdirs}')
        dir_list = list()
        for subdir in subdirs:
            result = find_dir(subdir, dirname)
            if len(result) > 0:
                dir_list += result
        return(dir_list)

    return None

# find directories that are repos - identified by having a "Packages" subdir
#      returns a list of repos
def find_repo_dirs(starting_dirs):
    all_Package_dirs = list()

    for source_dir in starting_dirs:
        #print(f'looking for Packages in {source_dir}')
        package_dirs = find_dir(source_dir, "Packages")
        #print(f'package_dirs={package_dirs}')
        if package_dirs is not None or len(package_dirs) > 0:
            all_Package_dirs += package_dirs

    #print(f'FOUND: {all_Package_dirs}')
    # ok, we have the Package directories - ../ is the repo basedir.
    repos = list()
    for path in all_Package_dirs:
        repos.append(path[:-len('/Packages')])
    return(repos)

# main part #######################################

# get a list of repo directories from the source media/directory
#     current implementation assumes there is a Packages subdir in all repos, but this doesn't have to be
repo_dirs = find_repo_dirs(args.source_dir)
print(f'searching {repo_dirs}')

# copy all the rpms to the dest directory
with open(args.input_file) as f:
    for filename in f:
        filename = filename.rstrip()
        if len(filename) == 0:
            print('Blank line found, continuing')
            continue
        if args.verbosity > 1:
            print(f'filename={filename}')

        # find the file in the list of repos
        found = False
        for repo_dir in repo_dirs:
            repo_name = os.path.basename(repo_dir)
            for subdir in ['', 'Packages', f'Packages/{filename[0].lower()}']:
                sourcefile = os.path.join(repo_dir, subdir, filename)
                if os.path.isfile(sourcefile):
                    found = True
                    break   # stop so it can be copied
            if found:
                break
        if not found:
            # we've looked in all the repos, and didn't find the package!
            print(f'{filename}: File Not Found')
            continue

        if args.verbosity > 1:
            print(f'found={sourcefile}')

        # copy it to args.destdir 
        repodest = os.path.join(args.dest_dir, repo_name)   # add repo name to dest_dir - ie: AppStream, BaseOS, etc
        destfile = os.path.join(repodest, f'Packages/{filename[0].lower()}', filename)
        if args.verbosity > 1:
            print(f'copying {sourcefile} to {repodest}')
        os.makedirs(os.path.dirname(destfile), exist_ok=True)     # make sure the target directory exists
        result = shutil.copyfile(sourcefile, destfile)     # copy it
        if args.verbosity > 0:
            print(f'{destfile}')

# all the rpms should have been copied to their destinations, so
# run 'createrepo' on all repos...
for repo_dir in repo_dirs:
    comps = os.path.join(repo_dir, 'comps.xml')
    modules = os.path.join(repo_dir, 'modules.yaml')
    repo_name = os.path.basename(repo_dir)
    repodest = os.path.join(args.dest_dir, repo_name)   # add repo name to dest_dir - ie: AppStream, BaseOS, etc
    has_comps = False
    has_modules = False
    if os.path.isfile(comps):
        result = shutil.copyfile(comps, os.path.join(repodest, 'comps.xml'))     # copy it
        has_comps = True
    if os.path.isfile(modules):
        result = shutil.copyfile(modules, os.path.join(repodest, 'modules.yaml'))     # copy it
        has_modules = True

    if has_comps:
        arg = '-g comps.xml'
    else:
        arg = ''

    subprocess.run(f'createrepo {arg} {repodest}', shell=True)
    if has_modules:
        subprocess.run(f'modifyrepo {repodest}/modules.yaml {repodest}/repodata/', shell=True)



