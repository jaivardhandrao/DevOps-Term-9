# System information script

[`system-info.sh`](system-info.sh) collects the requested system details. It deliberately writes
the full process list to a generated file instead of printing hundreds of rows to the terminal.

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
