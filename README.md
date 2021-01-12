# generic-pixyz-utilities

When using this library remove pubsub limits from your redis instance to avoid issues due to large message ontaining model geometry.

Do this by using rediscli and running the command:

  - CONFIG SET client-output-buffer-limit "normal 0 0 0 slave 0 0 0 pubsub 0 0 0"
  - or setting the same value in redis.conf
