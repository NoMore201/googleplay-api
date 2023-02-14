#! /bin/bash
#
# deploy.sh
# Copyright (C) 2015 Subho Halder <sunny@appknox.com>
#
# Distributed under terms of the MIT license.
#


rm -rf dist/
bumpversion patch
export CURRENT_BRANCH
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push --tags
git push origin "$CURRENT_BRANCH:$CURRENT_BRANCH"
python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*