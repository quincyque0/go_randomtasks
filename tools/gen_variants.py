
import csv
import json
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
ROSTER = ROOT / 'students' / 'roster.csv'
VARIANTS = ROOT / 'variants'

DOMAINS = [
    ('users', 'user', ('email', 'str')),
    ('items', 'item', ('sku', 'str')),
    ('orders', 'order', ('priority', 'int')),
    ('products', 'product', ('price', 'float')),
    ('tickets', 'ticket', ('status', 'str')),
    ('profiles', 'profile', ('phone', 'str')),
    ('devices', 'device', ('serial', 'str')),
    ('sessions', 'session', ('ip', 'str')),
    ('invoices', 'invoice', ('amount', 'float')),
    ('reviews', 'review', ('rating', 'int')),
    ('shipments', 'shipment', ('tracking', 'str')),
    ('notifications', 'notification', ('channel', 'str')),
    ('bookings', 'booking', ('date', 'str')),
    ('messages', 'message', ('topic', 'str')),
    ('likes', 'like', ('target', 'str')),
    ('photos', 'photo', ('url', 'str')),
    ('tasks', 'task', ('due', 'str')),
    ('events', 'event', ('location', 'str')),
    ('comments', 'comment', ('author', 'str')),
    ('logs', 'log', ('level', 'str')),
]


def hash_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16)


def build_variant(group: str, student_id: str, week: str):
    seed = hash_seed(f"{group}:{student_id}:{week}")
    resource, singular, extra = DOMAINS[seed % len(DOMAINS)]
    extra_name, extra_type = extra
    service_name = f"{resource}-svc-{student_id}"
    port = 8100 + (seed % 200)
    base = {
        "group": group,
        "student_id": student_id,
        "week": week,
        "resource": resource,
        "singular": singular,
        "extra_field": {"name": extra_name, "type": extra_type},
        "service": {"name": service_name, "port": port},
        "gateway": {
            "prefix": "/api",
            "routes": [
                {"path": f"/api/{resource}", "upstream": service_name}
            ],
        },
        "grpc": {
            "package": f"{resource}.v1",
            "service": f"{resource.capitalize()}Service",
        },
        "graphql": {
            "type": singular.capitalize(),
            "query": f"{resource}",
            "mutation": f"create{singular.capitalize()}",
        },
        "k8s": {
            "app": f"{resource}-app",
            "container": f"{resource}-container",
        },
        "project_code": f"{resource}-{student_id}",
    }
    return base


def main():
    VARIANTS.mkdir(exist_ok=True)
    with ROSTER.open() as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        sid = row['id']
        raw_grp = row.get('group', '431')
        if raw_grp.isdigit():
            grp = f"{raw_grp}"
        else:
            grp = raw_grp

        (VARIANTS / grp / sid).mkdir(parents=True, exist_ok=True)
        for w in range(1, 18):
            week = str(w).zfill(2)
            v = build_variant(grp, sid, week)
            path = VARIANTS / grp / sid / f"week-{week}.json"
            path.write_text(json.dumps(v, indent=2, ensure_ascii=False))

    print(f"Сгенерированы варианты для {len(rows)} студентов.")


if __name__ == '__main__':
    main()
