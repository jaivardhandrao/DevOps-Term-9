#!/usr/bin/env bash

set -euo pipefail

run_if_available() {
    local command_name=$1
    shift

    if command -v "$command_name" >/dev/null 2>&1; then
        "$@"
    else
        printf '%s is not installed; skipping this check.\n' "$command_name"
    fi
}

echo "== Hostname =="
hostname

echo
echo "== Interfaces =="
if command -v ip >/dev/null 2>&1; then
    ip -brief address
else
    run_if_available ifconfig ifconfig
fi

echo
echo "== Routes =="
if command -v ip >/dev/null 2>&1; then
    ip route
else
    run_if_available netstat netstat -rn
fi

echo
echo "== DNS lookup =="
if command -v nslookup >/dev/null 2>&1; then
    nslookup example.com
else
    run_if_available host host example.com
fi

echo
echo "== Connectivity =="
ping -c 2 1.1.1.1

echo
echo "== HTTP headers =="
run_if_available curl curl -fsSI --max-time 10 https://example.com

echo
echo "== Listening sockets =="
if command -v ss >/dev/null 2>&1; then
    ss -tuln
else
    run_if_available netstat netstat -an
fi
