# Stop the server that's running and start it again
# This is for personal use you should read this code before running it

pkill python3
mkdir -p temp
nohup python3 src/server.py 80 --release &
