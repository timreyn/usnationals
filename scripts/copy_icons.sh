SRC=../external/icons/svgs/event
TARGET=../USNationalsApp/app/src/main/res/drawable

for FILE in $(ls $SRC)
do
  FILENAME=$(echo $FILE | sed -s "s/\.svg//")
  convert -resize 100x100 $SRC/$FILENAME.svg $TARGET/e_$FILENAME.png
  convert -background transparent $SRC/$FILENAME.svg \
          -fill white -opaque black -resize 50x50 $TARGET/e_${FILENAME}_transparent.png
done
