echo 'Starting test...'

#for i in {0..30}; do
python3 client/main.py --app 1  &
python3 client/main.py --app 2  &
python3 client/main.py --app 3  &
python3 client/main.py --app 4  &
python3 client/main.py --app 5  &
python3 client/main.py --app 6  &
python3 client/main.py --app 7  &
python3 client/main.py --app 8  &
python3 client/main.py --app 9  &
#done

echo  'Finished'
