#!/bin/sh

PROJ_DIR="$(dirname $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd))"

# Path to your python script
SCRIPT="$PROJ_DIR/sfinder-saves.py"

# Keep track of tests
passed=0
failed=0

# A function to run a single test:
# test_case "description" "command args" "expected output"
test_case() {
    local desc="$1"
    local args="$2"
    local expected="$3"

    echo -n "Test: $desc ... "

    # Capture output
    output=$(python "$SCRIPT" $args)

    if [[ "$output" == "$expected" ]]; then
        echo "OK"
        ((passed++))
    else
        echo "FAIL"
        echo "   Expected: '$expected'"
        echo "   Got:      '$output'"
        ((failed++))
    fi
}

# -------------------------------
# Add your tests here:
# -------------------------------

test_case "Basic save O 2nd PC" "percent -w O -pc 2 -l LSZO -b LSZO -f $PROJ_DIR/tests/testPath2.csv -lp /dev/null" "O: 26.27% [1324/5040]"
test_case "Null case with 2nd PC" "percent -w T -pc 2 -l LSZO -b LSZO -f $PROJ_DIR/tests/testPath2.csv -lp /dev/null" "T: 0.00% [0/5040]"
test_case "ILJO with 1st PC" "percent -w ILJO -pc 1 -l TILJSZO -b ILSZ -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "ILJO: 8.10% [408/5040]"
test_case "ILJO with 1st PC with only leftover" "percent -w ILJO -pc 1 -l TJO -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "ILJO: 8.10% [408/5040]"
test_case "ILJO with 1st PC with only leftover with hyphen" "percent -w ILJO -pc 1 -l TJO- -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "ILJO: 8.10% [408/5040]"
# test_case "Missing argument fails" "--add 2" "Error: missing operand"

# -------------------------------

echo
echo "Passed: $passed"
echo "Failed: $failed"

# Exit non-zero if tests failed
[[ $failed -eq 0 ]]
