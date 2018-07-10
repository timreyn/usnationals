# Precondition: scrambles organized as follows:
# .
# ./222
# ./222/1
# ./222/1/2x2x2 Round 1 Group A.pdf
# ./222/1/2x2x2 Round 1 Group B.pdf
# ./222/2
# ./222/2/2x2x2 Round 2 Group A.pdf
# etc
#
# Usage:
# ./collate_scrambles.sh <event/round> <number of groups> <stage_name> <stage_code>

DIR=$1
NUM_GROUPS=$2
STAGE_NAME=$3
STAGE_CODE=$4

mkdir -p $DIR/$STAGE_CODE

NUM_MOVED=0

while [[ $NUM_MOVED -lt $NUM_GROUPS ]]; do
  NUM_MOVED=$(( $NUM_MOVED + 1 ))
  FILE_TO_MOVE=$(ls $DIR | grep "\.pdf$" | head -1)
  TARGET=$(echo "$FILE_TO_MOVE" | sed -s "s/Group .*\.pdf/$STAGE_NAME $NUM_MOVED.pdf/")
  mv "$DIR/$FILE_TO_MOVE" "$DIR/$STAGE_CODE/$TARGET"
done
