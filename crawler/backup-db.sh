#!/usr/bin/env bash
sqlite3 ./results.db .dump | gzip -c >results.dump.gz
zcat < ./results.dump.gz | sqlite3 results.db