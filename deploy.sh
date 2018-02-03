#!/bin/bash

set -eu

if [[ $TRAVIS_BRANCH != master ]]; then
    echo "Skipping deploy because $TRAVIS_BRANCH != master"
    exit
fi

# Stage needed bits in a deploy directory.
git config user.name "Deployment Bot (from Travis CI)"
git config user.email "deploy@travis-ci.org"

revision=$(git rev-parse --short=12 HEAD)

remote_url=$(git config remote.origin.url | sed -e "s/\(github.com\)/$GITHUB_TOKEN@\1/")

git clone --quiet --branch gh-pages $remote_url _deploy
cp index.html winsim.js _deploy

cd _deploy
git add .
git commit --message "Deploy seankelly/winsim@$revision"
git push --quiet
