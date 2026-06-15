#!/bin/bash

TEST_FILE="src/client/tests/test_$TEST.sh"

if [[ -f $TEST_FILE ]]; then
    echo "Running '$TEST' tests..."
    ./$TEST_FILE
else
    echo "Looks like there's no tests with that name"
    echo "Available tests:"
    for test in $(ls -l src/client/tests | grep -o '\w*.sh'); do
        echo '-' $test
    done
fi
