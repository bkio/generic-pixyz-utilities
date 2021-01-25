# generic-pixyz-utilities

For installing redis and redis-cli, you can use that commands:

	docker pull redis
	docker run --name redis --restart=always -d -p 6379:6379 redis
	npm install -g redis-cli


When using this library remove pubsub limits from your redis instance to avoid issues due to large message ontaining model geometry.

Do this by using `rdcli` and running the command:

	  CONFIG SET client-output-buffer-limit "normal 0 0 0 slave 0 0 0 pubsub 0 0 0"

or setting the same values in redis.conf with:

	client-output-buffer-limit normal 0 0 0
	client-output-buffer-limit slave 0 0 0
	client-output-buffer-limit pubsub 0 0 0
