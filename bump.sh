#!/bin/bash

if [ -z "$1" ]; then
    echo Specify \'major\', \'minor\', or \'patch\' with optional second argument \'beta\' for a new release, \'beta\' when bumping beta version, or \'release\' when ready to remove beta and make stable
    exit
fi
if [ -n "$(grep current_version .bumpversion.cfg | cut -d \= -f 2 | cut -d \. -f 3 | grep b)" ]; then
    echo Currently on beta version $(grep current_version .bumpversion.cfg | cut -d \= -f 2)
    if [ "$1" = "beta" ]; then
        echo ... Bumping beta version
        SERIALIZE={major}.{minor}.{patch}b{beta}
        PART=beta
    elif [ "$1" = "release" ]; then
        echo ... Bumping to stable version
        SERIALIZE={major}.{minor}.{patch}
        PART=beta
    else
        echo ... You must specify either \'beta\' or \'release\'
        exit
    fi
else
    echo Currently on stable version $(grep current_version .bumpversion.cfg | cut -d \= -f 2)
    if [ "$1" = "major" ]; then
        PART=major
        if [ -z "$2" ]; then
            echo ... Major version bump, skipping beta
            SERIALIZE={major}.{minor}.{patch}
        elif [ "$2" = "beta" ]; then
            echo ... Major version bump, entering beta
            SERIALIZE={major}.{minor}.{patch}b{beta}
        else
            echo ... Second input must be \'beta\' or nothing
            exit
        fi
    elif [ "$1" = "minor" ]; then
        PART=minor
        if [ -z "$2" ]; then
            echo ... Minor version bump, skipping beta
            SERIALIZE={major}.{minor}.{patch}
        elif [ "$2" = "beta" ]; then
            echo ... Minor version bump, entering beta
            SERIALIZE={major}.{minor}.{patch}b{beta}
        else
            echo ... Second input must be \'beta\' or nothing
            exit
        fi
    elif [ "$1" = "patch" ]; then
        PART=patch
        if [ -z "$2" ]; then
            echo ... Patch version bump, skipping beta
            SERIALIZE={major}.{minor}.{patch}
        elif [ "$2" = "beta" ]; then
            echo ... Patch version bump, entering beta
            SERIALIZE={major}.{minor}.{patch}b{beta}
        else
            echo ... Second input must be \'beta\' or nothing
            exit
        fi
    else
        echo Specify \'major\', \'minor\', or \'patch\' optionaly followed by \'beta\'
        exit
    fi
fi
echo executing: bumpversion $PART --serialize $SERIALIZE --commit
bumpversion $PART --serialize $SERIALIZE --commit
