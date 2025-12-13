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

# percent for inputting leftover length, leftover, build
test_case "Basic save O 2nd PC" "percent -w O -pc 2 -l LSZO -b LSZO -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" "O: 26.27% [1324/5040]"
test_case "Null case with 2nd PC" "percent -w T -pc 2 -l LSZO -b LSZO -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" "T: 0.00% [0/5040]"
test_case "ILJO with 1st PC" "percent -w ILJO -pc 1 -l TILJSZO -b ILSZ -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "ILJO: 8.10% [408/5040]"
test_case "ILJO with 1st PC with only leftover" "percent -w ILJO -pc 1 -l TJO -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "ILJO: 8.10% [408/5040]"
test_case "ILJO with 1st PC with only leftover with hyphen" "percent -w ILJO -pc 1 -l TJO- -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "ILJO: 8.10% [408/5040]"
test_case "2nd PC using next bag and not using piece from leftover" "percent -w I -pc 2 -l IJSZ -b ISZO -f $PROJ_DIR/tests/testPath2-2.csv -lp /dev/null" "I: 50.00% [360/720]"
test_case "2nd PC using next bag and not using piece from leftover with shorthand leftover" "percent -w I -pc 2 -l J-O -f $PROJ_DIR/tests/testPath2-2.csv -lp /dev/null" "I: 50.00% [360/720]"
test_case "Basic save O 2nd PC with no leftover" "percent -w O -pc 2 -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" "O: 26.27% [1324/5040]"
test_case "Null case with 2nd PC with no leftover" "percent -w T -pc 2 -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" "T: 0.00% [0/5040]"

test_case "Basic save O 2nd PC" "percent -w O -ll 4 -l LSZO -b LSZO -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" "O: 26.27% [1324/5040]"
test_case "Null case with 2nd PC" "percent -w T -ll 4 -l LSZO -b LSZO -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" "T: 0.00% [0/5040]"
test_case "ILJO with 1st PC" "percent -w ILJO -ll 7 -l TILJSZO -b ILSZ -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "ILJO: 8.10% [408/5040]"
test_case "ILJO with 1st PC with only leftover" "percent -w ILJO -ll 7 -l TJO -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "ILJO: 8.10% [408/5040]"
test_case "ILJO with 1st PC with only leftover with hyphen" "percent -w ILJO -ll 7 -l TJO- -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "ILJO: 8.10% [408/5040]"
test_case "2nd PC using next bag and not using piece from leftover" "percent -w I -ll 4 -l IJSZ -b ISZO -f $PROJ_DIR/tests/testPath2-2.csv -lp /dev/null" "I: 50.00% [360/720]"
test_case "2nd PC using next bag and not using piece from leftover with shorthand leftover" "percent -w I -ll 4 -l J-O -f $PROJ_DIR/tests/testPath2-2.csv -lp /dev/null" "I: 50.00% [360/720]"

# filter for inputting leftover length, leftover, build
test_case "Basic save O 2nd PC" "filter -w O -pc 2 -l LSZO -b LSZO -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" $'2 edges, 2 nodes
You must learn 2 solutions to cover all queues. There are 1 combinations of solutions to cover all patterns.
True minimal for O:
v115@9gzhilR4A8i0wwglAtR4D8xwBtF8g0wwAtE8JeAgWm?A6untCMOUABBoo2AS7HOBwngHBFbcRAS0+5AUOaHBQecRAy?lAAA9gi0wwilR4A8zhglAtR4D8xwBtF8g0wwAtE8JeAgWkA?ad9VC0PUABBoo2AWFjHBFrnRASo78A48o2AvfEEBwnAVB'
test_case "Null case with 2nd PC" "filter -w T -pc 2 -l LSZO -b LSZO -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" "No solutions found"
test_case "ILJO with 1st PC" "filter -w ILJO -pc 1 -l TILJSZO -b ILSZ -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" $'3 edges, 3 nodes
You must learn 3 solutions to cover all queues. There are 1 combinations of solutions to cover all patterns.
True minimal for ILJO:
v115@9gD8R4BtRpC8R4ywRpE8xwi0D8ywBtg0JeAgWkA0vy?tC0nUABBoo2AVFM6AFrnRASo78AYb2RBvfEEBwnAVB9gD8w?wR4i0C81wg0E8BtwwRpD8R4BtRpJeAgWkAvOmPCadUABBoo?2ATVFVBFrnRASo78A4JELBvfEEBwnAVB9gD8zwRpC8ywBtR?pE8R4i0D8R4wwBtg0JeAgWjAK3TxC6eUABBoo2AR1QOBFrn?RASo78AYhVzAVYt2AFr4AA'
test_case "ILJO with 1st PC with only leftover" "filter -w ILJO -pc 1 -l TJO -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" $'3 edges, 3 nodes
You must learn 3 solutions to cover all queues. There are 1 combinations of solutions to cover all patterns.
True minimal for ILJO:
v115@9gD8R4BtRpC8R4ywRpE8xwi0D8ywBtg0JeAgWkA0vy?tC0nUABBoo2AVFM6AFrnRASo78AYb2RBvfEEBwnAVB9gD8w?wR4i0C81wg0E8BtwwRpD8R4BtRpJeAgWkAvOmPCadUABBoo?2ATVFVBFrnRASo78A4JELBvfEEBwnAVB9gD8zwRpC8ywBtR?pE8R4i0D8R4wwBtg0JeAgWjAK3TxC6eUABBoo2AR1QOBFrn?RASo78AYhVzAVYt2AFr4AA'
test_case "ILJO with 1st PC with only leftover with hyphen" "filter -w ILJO -pc 1 -l TJO- -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" $'3 edges, 3 nodes
You must learn 3 solutions to cover all queues. There are 1 combinations of solutions to cover all patterns.
True minimal for ILJO:
v115@9gD8R4BtRpC8R4ywRpE8xwi0D8ywBtg0JeAgWkA0vy?tC0nUABBoo2AVFM6AFrnRASo78AYb2RBvfEEBwnAVB9gD8w?wR4i0C81wg0E8BtwwRpD8R4BtRpJeAgWkAvOmPCadUABBoo?2ATVFVBFrnRASo78A4JELBvfEEBwnAVB9gD8zwRpC8ywBtR?pE8R4i0D8R4wwBtg0JeAgWjAK3TxC6eUABBoo2AR1QOBFrn?RASo78AYhVzAVYt2AFr4AA'
test_case "2nd PC using next bag and not using piece from leftover" "filter -w I -pc 2 -l IJSZ -b ISZO -f $PROJ_DIR/tests/testPath2-2.csv -lp /dev/null" $'1 edges, 1 nodes
You must learn 1 solutions to cover all queues. There are 1 combinations of solutions to cover all patterns.
True minimal for I:
v115@9gh0R4Bthli0R4B8Btglg0wwg0F8glxwH8g0wwJeAg?WkA0iLuCqPUABBoo2AV4f2AwngHBFbcRASU7KBwGk9AwnAV?B'
test_case "2nd PC using next bag and not using piece from leftover with shorthand leftover" "filter -w I -pc 2 -l J-O -f $PROJ_DIR/tests/testPath2-2.csv -lp /dev/null" $'1 edges, 1 nodes
You must learn 1 solutions to cover all queues. There are 1 combinations of solutions to cover all patterns.
True minimal for I:
v115@9gh0R4Bthli0R4B8Btglg0wwg0F8glxwH8g0wwJeAg?WkA0iLuCqPUABBoo2AV4f2AwngHBFbcRASU7KBwGk9AwnAV?B'
test_case "Basic save O 2nd PC with no leftover" "filter -w O -pc 2 -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" $'2 edges, 2 nodes
You must learn 2 solutions to cover all queues. There are 1 combinations of solutions to cover all patterns.
True minimal for O:
v115@9gzhilR4A8i0wwglAtR4D8xwBtF8g0wwAtE8JeAgWm?A6untCMOUABBoo2AS7HOBwngHBFbcRAS0+5AUOaHBQecRAy?lAAA9gi0wwilR4A8zhglAtR4D8xwBtF8g0wwAtE8JeAgWkA?ad9VC0PUABBoo2AWFjHBFrnRASo78A48o2AvfEEBwnAVB'
test_case "Null case with 2nd PC with no leftover" "filter -w T -pc 2 -f $PROJ_DIR/tests/testPath2-1.csv -lp /dev/null" "No solutions found"

# errors
test_case "Invalid build" "percent -w I -pc 1 -l TILJSZO -b ILSz -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "Build expected to contain only TILJSZO pieces"
test_case "Invalid no leftover but with build" "percent -w I -pc 1 -b ILSZ -f $PROJ_DIR/tests/testPath1.csv -lp /dev/null" "-l must be set"




# -------------------------------

echo
echo "Passed: $passed"
echo "Failed: $failed"

# Exit non-zero if tests failed
[[ $failed -eq 0 ]]
