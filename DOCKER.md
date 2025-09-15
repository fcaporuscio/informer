# Build

```sh
docker build -t informer:app .
```

# Run

```sh
# Create the directories/files beforehand otherwise the -v option
# may create a directory instead of a file where a file is needed!
mkdir -p /tmp/informer/cache
touch /tmp/informer/informer.log

docker run -d -it --rm --network host \
  --name="informer" \
  -e TZ=$(cat /etc/timezone) \
  -v ./informer.yml:/app/informer.yml \
  -v /tmp/informer/informer.log:/var/log/gunicorn/informer.log \
  -v /tmp/informer/cache:/app/.cache \
  informer:app
```

You can leave out '-v ./.cache:/app/.cache' if you don't want to persist
the cache between stoping and starting the container.

# Stop

```sh
docker stop informer
```
