# Git and GitHub practice

## `git commit -m` and `git commit -a -m`

`git commit -m "message"` commits only changes already added to the staging area. It works for new
files and tracked files after `git add`.

`git commit -a -m "message"` first stages modified and deleted **tracked** files, then commits them.
It does not include a new untracked file.

The important result from my test was:

```text
modified tracked file  -> included by git commit -a
new untracked file     -> not included by git commit -a
```

I would use `git commit -a` only after checking `git status` and the diff. Explicit `git add` is
clearer when a change contains several unrelated files.

## Cherry-pick exercise

I used a temporary repository for this exercise so the practice history would not clutter the
homework repository.

```bash
git init -b main cherry-pick-lab
cd cherry-pick-lab

printf 'base\n' > notes.txt
git add notes.txt
git commit -m "Add base notes"

printf 'linux\n' >> notes.txt
git commit -a -m "Add Linux note"

printf 'docker\n' >> notes.txt
git commit -a -m "Add Docker note"

git switch -c command-notes
printf 'networking\n' >> notes.txt
git commit -a -m "Add networking note"

printf 'journalctl\n' >> notes.txt
git commit -a -m "Add journalctl note"

git log --oneline --all --decorate --graph
git switch main
git cherry-pick <networking-commit-id>
git log --oneline --decorate
grep networking notes.txt
```

The actual commit IDs and output from my run are in [cherry-pick-output.txt](cherry-pick-output.txt).
A cherry-pick copies the selected change onto the current branch, so the new commit has a different
ID even though its patch is the same.
