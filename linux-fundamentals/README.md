# Linux fundamentals

## Soft links and hard links

A hard link is another directory entry for the same inode. A soft link is a small file containing
a path to another file.

| Check | Hard link | Soft link |
| --- | --- | --- |
| Shares the target inode | Yes | No |
| Can cross file systems | No | Yes |
| Can point to a directory | Normally no | Yes |
| Works after the original name is removed | Yes | No, it becomes broken |

I used this small test:

```bash
mkdir link-lab
cd link-lab
printf 'first file\n' > original.txt
ln original.txt hard-link.txt
ln -s original.txt soft-link.txt
ls -li

rm soft-link.txt
rm hard-link.txt
rm original.txt
cd ..
rmdir link-lab
```

`ls -li` showed the same inode number for `original.txt` and `hard-link.txt`. The symbolic link
had a different inode and displayed `soft-link.txt -> original.txt`.

## `adduser` and `useradd`

Both commands create users, but they are aimed at different levels.

| Command | Behaviour on Ubuntu |
| --- | --- |
| `adduser` | Friendly interactive wrapper. It creates the home directory, asks for account details, and applies Ubuntu defaults. |
| `useradd` | Lower-level command. It is useful in scripts, but options such as `-m` and `-s` must be supplied explicitly. |

For an interactive Ubuntu machine I would normally choose `adduser`:

```bash
sudo adduser devopsdemo
id devopsdemo
getent passwd devopsdemo
sudo deluser --remove-home devopsdemo
```

The equivalent low-level creation command is:

```bash
sudo useradd -m -s /bin/bash devopsdemo
sudo passwd devopsdemo
```

I ran the `adduser` exercise inside an Ubuntu container so that no user was added to my laptop.
The observed `id` output is in [lab-output.txt](lab-output.txt).

## `journalctl`

`journalctl` reads logs collected by `systemd-journald`. The most useful commands from my notes
are:

```bash
journalctl                         # all available journal entries
journalctl -b                      # current boot only
journalctl -p err                  # errors and more severe messages
journalctl -u ssh                  # logs for the ssh service
journalctl -u nginx --since today  # nginx entries since midnight
journalctl -f                      # follow new entries
journalctl --disk-usage            # journal storage used
```

Docker containers normally do not boot with systemd as PID 1, so service-level `journalctl`
practice needs a Linux VM or a regular Linux host. In containers I use `docker logs`; on Ubuntu
servers running systemd I use `journalctl`.

## Command cheat sheet

| Purpose | Command |
| --- | --- |
| Current directory | `pwd` |
| List files, including hidden files | `ls -la` |
| Create/copy/move/remove | `mkdir`, `cp`, `mv`, `rm` |
| Read text | `cat`, `less`, `head`, `tail` |
| Search text and files | `grep`, `find` |
| Permissions and ownership | `chmod`, `chown` |
| Disk space and directory size | `df -h`, `du -sh` |
| Memory and processes | `free -h`, `ps aux`, `top` |
| Identity | `whoami`, `id` |
| Network interfaces and routes | `ip addr`, `ip route` |
| Listening sockets | `ss -tulpn` |
| Services and logs | `systemctl`, `journalctl` |
| Archives | `tar -czf`, `tar -xzf` |
| Built-in help | `man`, `command --help` |

## Fresh isolated run — 7 October 2026

[Raw commands and output](evidence/live-20261007T175903Z.txt) verify hard-link inode equality, a dangling soft link after target removal, temporary container user creation/removal, file/archive commands, disk/memory/process inspection, and two real `coursework-demo` journal entries. The [lab image](evidence/Dockerfile) installs its packages only inside disposable Ubuntu containers; no laptop account or package was changed.

The application journal was produced by a standalone `systemd-journald`. The recorded `journalctl -u coursework-demo.service` returned no entries because systemd was not PID 1. A real systemd-managed service demonstration remains outstanding; tagged application logs do not establish that requirement. The earlier failed attempt is retained in [the initial transcript](evidence/live-20261007T175642Z.txt).

A [read-only check of the isolated coursework Kubernetes node](evidence/systemd-service-journal.txt) subsequently confirmed PID 1 was `systemd` and `kubelet` was active. However, its unprivileged `journalctl -u kubelet --no-pager -n 15` read failed with journal ACL/permission errors. No elevated-user workaround or node change was attempted. This verifies the service state, but still does not provide readable service journal entries.

Reproduce from the repository root: `python3 scripts/run-foundation-evidence.py --topic linux`. This runs real commands and cleans up its own container.
