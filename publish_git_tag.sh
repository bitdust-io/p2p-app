#!/bin/bash

git fetch --all -f

git tag -a alpha HEAD -f

git push upstream alpha -f
