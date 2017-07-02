for STAGE in r g b o; do
  for STATION in 1 2 3 4 5 6 7 8; do
    wget -O- https://usnationals2017.appspot.com/job_schedule?job=J\&stage=$STAGE\&station=$STATION >> $1
  done
  wget -O- https://usnationals2017.appspot.com/job_schedule?job=R\&stage=$STAGE >> $1
  wget -O- https://usnationals2017.appspot.com/job_schedule?job=S\&stage=$STAGE >> $1
done
wget -O- https://usnationals2017.appspot.com/job_schedule?job=H\&stage=$STAGE >> $1
wget -O- https://usnationals2017.appspot.com/job_schedule?job=D\&stage=$STAGE >> $1
wget -O- https://usnationals2017.appspot.com/job_schedule?job=L\&stage=$STAGE >> $1
wget -O- https://usnationals2017.appspot.com/job_schedule?job=U\&stage=$STAGE >> $1
