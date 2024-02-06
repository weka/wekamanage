#! /usr/bin/env python3

import argparse
import glob
import os

parser = argparse.ArgumentParser(description='Reformat a dnf repo into a hierarchy of subdirectories')

parser.add_argument('directory', type=str, help='dnf repo directory to work on')
parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbose output')
args = parser.parse_args()

base_dir = args.directory

pack_dir = os.path.join(base_dir, "Packages")

if not os.path.exists(pack_dir):
    print(f"no Packages subdir found in {args.directory}")
    os.mkdir(pack_dir)
    print(f"created {pack_dir}")
    rpm_dir = base_dir
else:
    rpm_dir = pack_dir

if args.verbose:
    print(f"pack_dir: {pack_dir}, rpm_dir: {rpm_dir}")

pack_count = 0
subdir_count = 0
for pack in glob.glob(os.path.join(rpm_dir, "*.rpm")):
    subdir = os.path.join(pack_dir, os.path.basename(pack)[0].lower())
    if not os.path.exists(subdir):
        os.mkdir(subdir)
        subdir_count += 1
    new_name = os.path.join(subdir, os.path.basename(pack))
    os.rename(pack, new_name)
    pack_count += 1
    if args.verbose:
        print(f"{pack} -> {new_name} in {subdir}")

print(f"{subdir_count} subdirs created, {pack_count} packages moved")
