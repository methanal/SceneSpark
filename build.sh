#!/bin/bash

set -euxo pipefail

./api/build.sh

./web/build.sh
