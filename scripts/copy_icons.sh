SRC=../external/icons/svgs/event
TARGET=../USNationalsApp/app/src/main/res/drawable

for FILE in $(ls $SRC)
do
  FILENAME=$(echo $FILE | sed -s "s/\.svg//")
  convert $SRC/$FILENAME.svg $TARGET/e_$FILENAME.png
done
