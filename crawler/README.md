# Crawler

```bash
  -h, --help   Show help message

Subcommand: process
  -b, --batch  <arg>
  -l, --limit  <arg>
  -o, --offset  <arg>
  -p, --phase  <arg>           Choices: terbalik, roi, problems,
                               problems-reported, forms-processed, test, fetch,
                               align, extract, presidential, detect, submit,
                               tps-unprocessed
  -r, --refresh-token  <arg>
  -s, --service  <arg>
  -t, --threads  <arg>
  -h, --help                   Show help message
Subcommand: create-db
  -d, --drop
  -n, --name  <arg>   Choices: terbalik, roi, problems, problems-reported,
                      forms-processed, test, fetch, align, extract,
                      presidential, detect, submit, tps-unprocessed
  -h, --help          Show help message
Subcommand: stats
  -o, --on  <arg>   Choices: duplicates, det-duplicated
  -h, --help        Show help message
Subcommand: submit
  -f, --force
  -n, --name  <arg>    Choices: problems, switch, submit
  -t, --token  <arg>
  -h, --help           Show help message

```