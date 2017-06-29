URL="https://usnationals2017.appspot.com/scorecards?$2&$3"

if [[ -n "$4" ]]; then
  URL="$URL&$4"
fi

set -e

OUTPUT_DIR=$(dirname $0)
TEX_FILE=$1.tex
ORIGINAL_DIR=$(pwd)

cd $OUTPUT_DIR

echo "Fetching $URL"
wget -O $TEX_FILE $URL

pdflatex $TEX_FILE > /dev/null
evince $1.pdf

cd $ORIGINAL_DIR
