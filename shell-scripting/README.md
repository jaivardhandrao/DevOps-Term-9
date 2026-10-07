# System information script

[`system-info.sh`](system-info.sh) collects the requested system details. It prints the process list
and also saves it to a generated file using output redirection.

It uses:

- variables for the date, hostname, username, and output paths;
- `read -p` for the student's name and enrollment number;
- `mkdir` and `touch` to prepare the report files;
- `df -h` for disk usage; and
- `ps ... > processes.txt` for output redirection.

Run it from this folder:

```bash
chmod +x system-info.sh
./system-info.sh
```

The generated `system-report/` directory is ignored by Git because it contains machine-specific
process information. A safe run made in a disposable Linux container is recorded in
[sample-output.txt](sample-output.txt).

## Fresh isolated run — 7 October 2026

[Raw commands and output](evidence/live-20261007T175931Z.txt) show the actual repository script accepting the student's name/enrollment and printing date, hostname, user, disk usage, and processes. Both `system-report/processes.txt` and `system-report/summary.txt` were confirmed nonempty inside a new disposable Linux container. No laptop process report is published.

Reproduce from the repository root: `python3 scripts/run-foundation-evidence.py --topic shell`.
