#!/bin/bash

TEST_FILE="./tests/test_$TEST.sh"

if [[ -f $TEST_FILE ]]; then
    echo "Running '$TEST' tests..."
    ./$TEST_FILE
else
    echo "Looks like there's no tests with that name"
fi
