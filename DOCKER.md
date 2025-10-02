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

# This will run a container and make it available on port 8001:
docker run -d -it --rm --network bridge \
  --name informer \
  -e TZ=$(cat /etc/timezone) \
  -v ./informer.yml:/app/informer.yml \
  -v /tmp/informer/informer.log:/var/log/gunicorn/informer.log \
  -v /tmp/informer/cache:/root/.cache/informer \
  -p 8001:8181 \
  informer:latest
```

You can leave out '-v /tmp/informer/cache:/root/.cache/informer' if
you don't need to persist the cache between stoping and starting
the container.

Check the paths as this command assumes that your informer.yml file is
in the currect directory.

Note that the we're passing the system's timezone (TZ) environment
variable so that the container runs in the host's timezone. This is how
it is done in Linux. You can hardcode your value directly as well:

-e TZ="Europe/London"

# Cache

You can view and clean the cache files from the running container
with the following commands:

```sh
# List cache files
docker exec -it informer uv run informer.py cache

# Clean all cache files
docker exec -it informer uv run informer.py cache clean

# Clean all cache files for a specific widget (rss, for example)
docker exec -it informer uv run informer.py cache clean rss
```

# Stop

```sh
docker stop informer
```

# Podman

You can substitute the 'docker' command for 'podman' to use Podman.
