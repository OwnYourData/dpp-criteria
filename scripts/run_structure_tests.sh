#!/bin/sh
# Builds the SOyA structures and runs the test vectors against them inside the
# oydeu/soya-web-cli image, the same SOyA version that dpplint uses.
# The container does not use the SOyA repository at soya.ownyourdata.eu: it serves the built
# structures itself. The image exists for linux/amd64 only (emulated on Apple silicon).
set -eu
cd "$(dirname "$0")/.."
IMAGE="${SOYA_WEB_CLI_IMAGE:-oydeu/soya-web-cli:260704b}"

rm -rf build/structures
docker run --rm --platform linux/amd64 -v "$PWD":/work -w /work --entrypoint node "$IMAGE" scripts/build_structures.js

docker run --rm --platform linux/amd64 -v "$PWD":/work:ro --entrypoint sh \
  -e REPO_BASE_URL=http://127.0.0.1:9000 -e PORT=8080 "$IMAGE" -c '
    node /work/scripts/serve_structures.js /work/build/structures 9000 &
    node dist/index.js > /tmp/web-cli.log 2>&1 &
    node /work/scripts/test_structures.js'
