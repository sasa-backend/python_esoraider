gunicorn --keyfile=./privkey.pem --certfile=./fullchain.pem -w 4 -k uvicorn.workers.UvicornWorker -b :5000 esoraider_server.app:app --daemon --log-file=./log.log --capture-output --log-level debug