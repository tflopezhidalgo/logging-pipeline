echo 'Starting test...'

echo "---------- Now filtering by app id... -------------"

# run processes and store pids in array
for i in {1..2}; do
    python3 ./main.py --read --app $i  &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo "---------- Now filtering by dates... -------------"

for i in {1..2}; do
    python3 ./main.py --filter-dates --read --app $i  &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo "---------- Now filtering by tags... -------------"

for i in {1..2}; do
    python3 ./main.py --tag test --read --app $i  &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo "---------- Now filtering by pattern... -------------"

for i in {1..2}; do
    python3 ./main.py --pattern '.*[info].*' --read --app $i  &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo  'Finished'
