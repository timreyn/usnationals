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
# Usage, to copy scrambles from the Red to Blue stage:
# ./copy_scrambles.sh Red r Blue b 333/2

SOURCE_STAGE_NAME=$1
SOURCE_STAGE_CODE=$2
TARGET_STAGE_NAME=$3
TARGET_STAGE_CODE=$4
DIR=$5

SOURCE_DIR=$DIR/$SOURCE_STAGE_CODE
TARGET_DIR=$DIR/$TARGET_STAGE_CODE

TMP_DIR=$DIR/tmp

mkdir -p $TARGET_DIR
mkdir -p $TMP_DIR

while [[ $(ls $SOURCE_DIR | wc -l) -gt 0 ]]; do
  FILE_TO_MOVE=$(ls $SOURCE_DIR | head -1)
  TARGET=$(echo "$FILE_TO_MOVE" | sed -s "s/$SOURCE_STAGE_NAME/$TARGET_STAGE_NAME/")
  cp "$SOURCE_DIR/$FILE_TO_MOVE" "$TARGET_DIR/$TARGET"
  mv "$SOURCE_DIR/$FILE_TO_MOVE" $TMP_DIR
done

mv $TMP_DIR/* $SOURCE_DIR

rmdir $TMP_DIR
