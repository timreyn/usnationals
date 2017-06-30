
COMPETITOR_NUM=1
while [ $COMPETITOR_NUM -lt 777 ]; do
  wget -O- https://www.cubingusa.com/nationals2017/groups.php?i=$COMPETITOR_NUM\&printable >> $1
  COMPETITOR_NUM=$[ $COMPETITOR_NUM + 1]
done
