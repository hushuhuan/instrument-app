from __future__ import annotations

import socket
from urllib.parse import urlparse

from instrument_app.domain.app_config import AppConfig


def check_network(cfg: AppConfig) -> tuple[bool, str]:
    """
    TCP connect to ``cfg.selftest_ping_host`` (``host:port``) with ~3 s timeout.
    If host is empty, perform a weak local lookup check only (per plan).
    """
    raw = (cfg.selftest_ping_host or "").strip()
    if not raw:
        try:
            socket.gethostbyname(socket.gethostname())
            return True, "未配置 ping 目标：已做本机主机名解析检查"
        except OSError as e:
            return False, f"本机网络栈检查失败: {e}"

    host, port = _parse_host_port(raw)
    try:
        with socket.create_connection((host, port), timeout=3.0):
            pass
    except OSError as e:
        return False, f"TCP {host}:{port} 连接失败: {e}"
    return True, f"TCP {host}:{port} 连接成功"


def _parse_host_port(spec: str) -> tuple[str, int]:
    if "://" in spec:
        u = urlparse(spec)
        h = u.hostname or "localhost"
        p = u.port or (443 if u.scheme == "https" else 80)
        return h, p
    if ":" in spec:
        host, ps = spec.rsplit(":", 1)
        return host.strip(), int(ps)
    return spec, 80
