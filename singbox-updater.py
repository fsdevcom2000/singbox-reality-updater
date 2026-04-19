#!/usr/bin/env python3

# SingBox Reality Updater
# Automated REALITY node fetcher and configuration generator for Sing‑Box.

# SingBox Reality Updater is a lightweight and reliable automation tool that keeps your Sing‑Box configuration up to date.
# It fetches VLESS REALITY nodes, validates them, checks availability, builds a clean config.json, and safely restarts the service.

# Author: fsdevcom2000
# URL: https://github.com/fsdevcom2000/singbox-reality-updater/

import json
import socket
import requests
import tempfile
import os
import subprocess
import logging
import ssl
import yaml

from logging.handlers import RotatingFileHandler
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor


# LOAD YAML CONFIG
def load_yaml_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


# LOGGING
def setup_logging(log_path):
    logger = logging.getLogger("updater")
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(fmt)

    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())

    return logger


# SAFE FETCH
def fetch_list(url, log):
    try:
        r = requests.get(url, timeout=20)
    except Exception as e:
        log.error(f"fetch failed: {e}")
        return []

    if r.status_code != 200:
        log.error(f"fetch error: HTTP {r.status_code}")
        return []

    text = r.text.strip()
    if not text:
        log.error("fetch error: empty response")
        return []

    lines = text.splitlines()
    if len(lines) < 3:
        log.error("fetch error: too few lines, probably invalid file")
        return []

    return lines


# PARSER (REALITY ONLY)
def parse_vless(line):
    line = line.strip()
    if not line.startswith("vless://"):
        return None

    try:
        u = urlparse(line)

        uuid = u.username
        host = u.hostname
        port = u.port
        q = parse_qs(u.query)

        if not uuid or not host or not port:
            return None

        sec = (q.get("security", [""])[0]).lower()
        if sec != "reality":
            return None

        pbk = q.get("pbk", [""])[0]
        sid = q.get("sid", [""])[0]
        flow = q.get("flow", [""])[0]

        if not pbk or flow != "xtls-rprx-vision":
            return None

        sni = q.get("sni", [host])[0]

        return {
            "type": "vless",
            "server": host,
            "server_port": port,
            "uuid": uuid,
            "flow": "xtls-rprx-vision",
            "network": "tcp",
            "tls": {
                "enabled": True,
                "server_name": sni,
                "utls": {
                    "enabled": True,
                    "fingerprint": "chrome"
                },
                "reality": {
                    "enabled": True,
                    "public_key": pbk,
                    "short_id": sid,
                },
            },
        }

    except:
        return None


# FILTER
def is_valid(n):
    if not n:
        return False
    if n["server"] in ("127.0.0.1", "localhost"):
        return False
    if len(n["uuid"]) < 30:
        return False
    return True


# TLS CHECK
def tls_check(node, timeout):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        with socket.create_connection(
            (node["server"], node["server_port"]),
            timeout=timeout
        ) as sock:
            with ctx.wrap_socket(sock, server_hostname=node["tls"]["server_name"]):
                return True
    except:
        return False


def alive(node, timeout):
    return tls_check(node, timeout)


# DEDUP
def dedup(nodes):
    s = set()
    out = []
    for n in nodes:
        key = (n["server"], n["server_port"], n["uuid"])
        if key not in s:
            s.add(key)
            out.append(n)
    return out


# BUILD CONFIG
def build_config(nodes, max_nodes, dns, tun):
    outbounds = [
        {"type": "direct", "tag": "direct"},
        {"type": "block", "tag": "block"},
    ]

    tags = []

    for i, n in enumerate(nodes[:max_nodes]):
        n = dict(n)
        tag = f"n{i}"
        n["tag"] = tag
        tags.append(tag)
        outbounds.append(n)

    outbounds.append({
        "type": "urltest",
        "tag": "proxy",
        "outbounds": tags,
        "url": "http://www.gstatic.com/generate_204",
        "interval": "60s",
        "tolerance": 50,
        "interrupt_exist_connections": True
    })

    return {
        "log": {"level": "info"},
        "dns": {"servers": dns},
        "inbounds": [
            {
                "type": "tun",
                "tag": "tun",
                **tun
            }
        ],
        "outbounds": outbounds,
        "route": {
            "final": "proxy",
            "default_domain_resolver": dns[0]["tag"]
        }
    }


# WRITE + CHECK
def write(cfg, config_path, log):
    f = tempfile.NamedTemporaryFile(delete=False, mode="w")
    json.dump(cfg, f, indent=2)
    f.close()

    r = subprocess.run(
        ["sing-box", "check", "-c", f.name],
        capture_output=True
    )

    if r.returncode != 0:
        log.error(r.stderr.decode())
        os.unlink(f.name)
        return False

    os.replace(f.name, config_path)
    return True


# CHECK PIPELINE
def check_nodes(nodes, timeout):
    result = []

    with ThreadPoolExecutor(max_workers=20) as ex:
        for r in ex.map(lambda n: n if alive(n, timeout) else None, nodes):
            if r:
                result.append(r)

    return result


# MAIN
def main():
    cfg = load_yaml_config()

    URL = cfg["url"]
    MAX_NODES = cfg["max_nodes"]
    TIMEOUT = cfg["timeout"]
    CONFIG_PATH = cfg["paths"]["config"]
    LOG_PATH = cfg["paths"]["log"]
    SERVICE = cfg["service"]
    DNS = cfg["dns"]
    TUN = cfg["tun"]

    log = setup_logging(LOG_PATH)

    log.info("[+] fetching")
    raw = fetch_list(URL, log)
    if not raw:
        log.error("no data fetched, aborting")
        return

    log.info("[+] parsing")
    nodes = [parse_vless(x) for x in raw]
    nodes = [n for n in nodes if is_valid(n)]
    nodes = dedup(nodes)

    log.info(f"[+] parsed: {len(nodes)}")

    log.info("[+] checking")
    nodes = check_nodes(nodes, TIMEOUT)

    log.info(f"[+] alive: {len(nodes)}")

    if len(nodes) < 2:
        log.error("not enough nodes")
        return

    log.info("[+] building config")
    cfg_json = build_config(nodes, MAX_NODES, DNS, TUN)

    log.info("[+] writing config")
    if not write(cfg_json, CONFIG_PATH, log):
        return

    log.info("[+] restarting")
    subprocess.run(["systemctl", "restart", SERVICE])

    log.info("[+] done")


if __name__ == "__main__":
    main()
