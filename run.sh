LOG='log.txt '
if test -f "$LOG"; then
    rm "$FILE"
fi
python3 gamemaster.py > log.txt