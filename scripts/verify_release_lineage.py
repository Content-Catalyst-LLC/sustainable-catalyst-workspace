#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys
from release_lineage import validate_current_release_lineage

parser=argparse.ArgumentParser(description='Verify current Sustainable Catalyst Workspace release lineage.')
parser.add_argument('--root', default='.')
parser.add_argument('--expected')
parser.add_argument('--previous')
args=parser.parse_args()
result=validate_current_release_lineage(Path(args.root), args.expected, args.previous)
print(json.dumps(result, indent=2, sort_keys=True))
if not result['ok']:
    for error in result['errors']:
        print('FAIL - '+error, file=sys.stderr)
    raise SystemExit(1)
print(f"PASS - release lineage v{result['version']} <- v{result['previous_version']}")
