echo 'Starting test...'

# run processes and store pids in array
for i in {1..2}; do
    python3 ./main.py --invalid-params --read --app $i &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo  'Finished'
