#
# Filtering test: exercises the filtering feature against existing logs.
#

# Make sure there's data we can query later.

echo 'Writing some initial logs...'

for app in {1..5}; do
    python3 -m src.client.main --app $app &
    pids[${app}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo 'Done. Now testing'
echo "---------- Now filtering by app id... -------------"

# run processes and store pids in array
for i in {1..2}; do
    python3 -m src.client.main --read --app $i  &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo "---------- Now filtering by dates... -------------"

for i in {1..2}; do
    python3 -m src.client.main --filter-dates --read --app $i  &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo "---------- Now filtering by tag = 'test' -------------"

for i in {1..2}; do
    python3 -m src.client.main --tag test --read --app $i  &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo "---------- Now filtering by pattern = '.*\[info.*' -------------"

for i in {1..2}; do
    python3 -m src.client.main --pattern '.*\[info.*' --read --app $i  &
    pids[${i}]=$!
done

# wait for all pids
for pid in ${pids[*]}; do
    wait $pid
done

echo  'Finished'
