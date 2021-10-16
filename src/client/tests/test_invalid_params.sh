echo 'Starting test...'

INVALID_APP_ID='inexistent_app_id'

echo "Sending read request with app_id=$INVALID_APP_ID to server"

# run processes and store pids in array
python3 -m src.client.main --invalid-params --read --app $INVALID_APP_ID

echo "Sending write request without timestamp to server"

python3 -m src.client.main --no-timestamp --app 1

echo  'Finished'
