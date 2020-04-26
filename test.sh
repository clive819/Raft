cd /Users/clive/Google\ Drive/Q3\ -\ Spring\ 2020/Distributed\ Systems/Project/Raft

for _ in {1..5} 
do
	python3 main.py &
	sleep 0.1
done;

controlC() {
    pkill python3
	pkill Python
	pkill python
    exit
}

trap controlC SIGINT

wait %1