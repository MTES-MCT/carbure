#!/bin/bash

git fetch old-origin
git rebase old-origin/master
git push

