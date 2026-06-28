echo 'Starting test...'

# run processes and store pids in array
for app in {1..10}; do
    # Writers
    python3 -m src.client.main --app $app &
    pids[${app}]=$!

    # Readers
    python3 -m src.client.main --repeat --read --app $app  &
    xpids[${app}]=$!
done

echo 'Processes started, waiting for them to finish...'

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo 'Writers done. Waiting for readers...'

for pid in ${xpids[*]}; do
    wait $pid
done


echo  'Readers done. Test completed.'
