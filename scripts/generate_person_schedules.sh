
for COMPETITOR_NUM in $(cat $(dirname $0)/nonstaff_ids); do
  wget -O- https://www.cubingusa.com/nationals2017/groups.php?i=$COMPETITOR_NUM\&printable >> $1
done

for COMPETITOR_NUM in $(cat $(dirname $0)/staff_ids); do
  wget -O- https://www.cubingusa.com/nationals2017/groups.php?i=$COMPETITOR_NUM\&printable >> $1
done
