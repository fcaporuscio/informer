# Build

```sh
docker buildx build -t informer:latest .
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
  informer:latest
```

You can leave out '-v ./.cache:/app/.cache' if you don't want to persist
the cache between stoping and starting the container.

Check the paths as this command assumes that your informer.yml file is
in the currect directory.

Note that the we're passing the system's timezone (TZ) environment
variable so that the container runs in the host's timezone. This is how
it is done in Linux. You can hardcode your value directly as well:

-e TZ="Europe/London"

# Stop

```sh
docker stop informer
```
