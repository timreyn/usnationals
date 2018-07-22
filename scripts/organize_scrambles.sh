function organize() {
  mkdir $1
  mv "$2 Round "* $1

  for round in 1 2 3 4; do
    mkdir $1/$round
    mv $1/*"Round $round"* $1/$round
  done
}

organize 333 "3x3x3 Cube"
organize 222 "2x2x2 Cube"
organize 444 "4x4x4 Cube"
organize 555 "5x5x5 Cube"
organize 666 "6x6x6 Cube"
organize 777 "7x7x7 Cube"
organize 333bf "3x3x3 Blindfolded"
organize 333oh "3x3x3 One-Handed"
organize 333ft "3x3x3 With Feet"
organize clock "Clock"
organize minx "Megaminx"
organize pyram "Pyraminx"
organize skewb "Skewb"
organize sq1 "Square-1"
organize 444bf "4x4x4 Cube Blindfolded"
organize 555bf "5x5x5 Cube Blindfolded"
organize 333mbf "3x3x3 Multiple Blindfolded"
