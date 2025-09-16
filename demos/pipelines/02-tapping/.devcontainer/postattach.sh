# This code runs when the user attaches to the development container.

# This code creates a symbolic link from the working directory to the user directory.
# Users can update values in the visible .dallingerconfig file and they will be automatically loaded by experiments.
# They must make sure not to delete it, though.
rm /root/.dallingerconfig || true
ln -s /workspaces/${RepositoryName}/.devcontainer/.dallingerconfig /root/.dallingerconfig


# The following code launches the Redis and Postgres services in Docker containers.
echo "Preparing services:"

docker start redis || true
if [[ "$(docker ps | grep redis)" = "" ]]
then
docker run -d --name redis \
    -v redis:/data \
    -p 6379:6379 \
    redis redis-server --appendonly yes
fi

docker start postgres || true
if [[ "$(docker ps | grep postgres)" = "" ]]
then
docker run -d --name postgres \
  -e POSTGRES_USER=dallinger \
  -e POSTGRES_PASSWORD=dallinger \
  -e POSTGRES_DB=dallinger \
  -v postgres:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:12
fi

echo "...complete."
