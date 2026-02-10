import time
from dataclasses import dataclass, field

STALE_TIMEOUT = 300  # 5 минут


@dataclass
class DeviceInfo:
    device_id: str
    server: str = ""
    status: str = ""
    http_code: int = 0
    uptime_ms: int = 0
    last_seen: float = field(default_factory=time.time)


# chat_id пользователей, нажавших /start
subscribers: set[int] = set()

# deviceId → DeviceInfo
devices: dict[str, DeviceInfo] = {}


def register_ping(data: dict) -> bool:
    """Регистрирует пинг устройства. Возвращает True если устройство новое."""
    device_id = data["deviceId"]
    is_new = device_id not in devices
    devices[device_id] = DeviceInfo(
        device_id=device_id,
        server=data.get("server", ""),
        status=data.get("status", ""),
        http_code=data.get("httpCode", 0),
        uptime_ms=data.get("uptimeMs", 0),
        last_seen=time.time(),
    )
    return is_new


def pop_stale_devices() -> list[DeviceInfo]:
    """Удаляет и возвращает устройства без пинга > STALE_TIMEOUT."""
    now = time.time()
    stale = [d for d in devices.values() if now - d.last_seen > STALE_TIMEOUT]
    for d in stale:
        del devices[d.device_id]
    return stale
