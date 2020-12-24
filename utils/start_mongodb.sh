#!/usr/bin/env bash
# Start a fresh mongodb container

cd "$(dirname "$0")/.." || return
echo "$PWD"

if grep -q "mongodb_test" <<< "$(docker ps -a)"
then
    echo "Removing old mongdb_test container"
    docker rm --force mongodb_test
fi
sudo rm -rf test_data/mongodb_data

echo "Starting container 'mongodb_test' with username:password 'admin:admin'..."
docker run -d \
    -p 27017:27017 \
    -v "${PWD}/test_data/mongodb_data:/data/db" \
    --name=mongodb_test \
    -e MONGO_INITDB_ROOT_USERNAME=admin \
    -e MONGO_INITDB_ROOT_PASSWORD=admin \
    mongo:latest
