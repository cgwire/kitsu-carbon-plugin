#!/bin/bash
set -e
git pull --rebase origin main
last_release_number=$(grep '^version' manifest.toml | sed 's/version = "\(.*\)"/\1/')
release_number=$(echo ${last_release_number} | awk -F. -v OFS=. '{$NF += 1 ; print}')
sed -i.bak "s/version = \"$last_release_number\"/version = \"$release_number\"/" manifest.toml
rm -f manifest.toml.bak
git commit manifest.toml -m "$release_number"
git tag -a -m "Release v$release_number" v$release_number
git push origin main --follow-tags
