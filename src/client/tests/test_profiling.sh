echo 'Starting test...'

# run processes and store pids in array
for i in {1..10}; do
    python3 -m src.client.main  --app $i  &
    pids[${i}]=$!

    python3 -m src.client.main  --repeat --read --app $i  &
    xpids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

for pid in ${xpids[*]}; do
    wait $pid
done


echo  'Finished'
