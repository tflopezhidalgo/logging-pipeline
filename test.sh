echo 'Starting test...'

for i in {0..30}; do
    python3 client/main.py --app 1 > /dev/null
    python3 client/main.py --app 2 > /dev/null
    python3 client/main.py --app 3 > /dev/null
    python3 client/main.py --app 4 > /dev/null
    python3 client/main.py --app 5 > /dev/null
done

echo  'Finished'
