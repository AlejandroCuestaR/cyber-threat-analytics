"""
Genera los 3 datasets sintéticos pero realistas usados por la plataforma:
  - datasets/firewall_logs.csv
  - datasets/network_traffic.csv
  - datasets/login_attempts.csv

Los datos son DETERMINISTAS (semilla fija) para que el análisis sea reproducible.
Incluyen "suciedad" a propósito (nulos, duplicados, formatos mixtos) para que la
fase de limpieza tenga sentido.

> Para usar datos REALES (Kaggle / CIC-IDS-2017), reemplaza estos CSV por los
> tuyos respetando los mismos nombres de columna (ver docs/modelo_datos.md).

Uso:
    python generate_datasets.py
"""
import csv
import os
import random
from datetime import datetime, timedelta

random.seed(42)

OUT = os.path.join(os.path.dirname(__file__), "datasets")
os.makedirs(OUT, exist_ok=True)

START = datetime(2024, 1, 1, 0, 0, 0)
DAYS = 60

# --- Pools -----------------------------------------------------------------
PAISES = (
    ["China"] * 22 + ["Rusia"] * 18 + ["Estados Unidos"] * 15 + ["México"] * 12
    + ["Brasil"] * 8 + ["India"] * 8 + ["Alemania"] * 6 + ["Países Bajos"] * 5
    + ["Corea del Norte"] * 4 + ["Irán"] * 2
)

# IPs atacantes (pocas, mucho volumen) + IPs normales (muchas, poco volumen)
ATACANTES = [f"45.{random.randint(10,99)}.{random.randint(0,255)}.{random.randint(1,254)}"
             for _ in range(8)]
NORMALES = [f"192.168.{random.randint(0,5)}.{random.randint(1,254)}" for _ in range(120)]

PUERTOS_ATAQUE = [22, 3389, 445, 23, 1433, 3306, 21, 8080]
PUERTOS_NORMAL = [80, 443, 53, 123, 25, 110, 993]
PROTOCOLOS = ["TCP", "UDP", "ICMP"]

# Técnicas MITRE por puerto/contexto
MITRE = {
    22: "T1110",   # Brute Force (SSH)
    3389: "T1021", # Remote Services (RDP)
    445: "T1021",  # SMB
    23: "T1110",   # Telnet brute force
    1433: "T1190", # Exploit public-facing app (SQL Server)
    3306: "T1190", # MySQL
    21: "T1071",   # App layer protocol (FTP)
    8080: "T1190",
}


def rand_ts():
    delta = timedelta(
        days=random.randint(0, DAYS - 1),
        hours=_hora_sesgada(),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    return START + delta


def _hora_sesgada():
    # Más actividad de madrugada (ataques automatizados) y horario laboral
    pico = random.random()
    if pico < 0.45:
        return random.choice([0, 1, 2, 3, 4])      # madrugada
    if pico < 0.85:
        return random.randint(9, 18)               # laboral
    return random.randint(0, 23)


def severidad(accion, puerto):
    if accion == "deny" and puerto in (3389, 445, 1433):
        return "critica"
    if accion == "deny" and puerto in PUERTOS_ATAQUE:
        return random.choice(["alta", "critica"])
    if accion == "deny":
        return random.choice(["media", "alta"])
    return random.choice(["baja", "baja", "media"])


# ---------------------------------------------------------------------------
# 1) firewall_logs.csv
# ---------------------------------------------------------------------------
def gen_firewall(n=18000):
    rows = []
    for _ in range(n):
        es_ataque = random.random() < 0.55
        if es_ataque:
            src = random.choice(ATACANTES)
            puerto = random.choice(PUERTOS_ATAQUE)
            accion = "deny" if random.random() < 0.8 else "allow"
            pais = random.choice(["China", "Rusia", "Corea del Norte", "Irán"])
        else:
            src = random.choice(NORMALES)
            puerto = random.choice(PUERTOS_NORMAL)
            accion = "allow" if random.random() < 0.9 else "deny"
            pais = random.choice(PAISES)
        ts = rand_ts()
        rows.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": src,
            "dst_ip": f"10.0.0.{random.randint(1,50)}",
            "src_port": random.randint(1024, 65535),
            "dst_port": puerto,
            "protocol": random.choice(PROTOCOLOS),
            "action": accion,
            "bytes": random.randint(64, 50000),
            "country": pais,
            "severity": severidad(accion, puerto),
            "mitre_technique": MITRE.get(puerto, ""),
        })
    # Ensuciar: duplicados, nulos y un timestamp con otro formato
    for _ in range(int(n * 0.02)):
        rows.append(dict(random.choice(rows)))               # duplicados
    for r in random.sample(rows, int(len(rows) * 0.03)):
        r["country"] = ""                                    # nulos en country
    for r in random.sample(rows, int(len(rows) * 0.01)):
        r["bytes"] = ""                                      # nulos en bytes
    random.shuffle(rows)
    _write("firewall_logs.csv", rows,
           ["timestamp", "src_ip", "dst_ip", "src_port", "dst_port",
            "protocol", "action", "bytes", "country", "severity", "mitre_technique"])
    return len(rows)


# ---------------------------------------------------------------------------
# 2) network_traffic.csv
# ---------------------------------------------------------------------------
def gen_network(n=14000):
    rows = []
    for _ in range(n):
        anomalo = random.random() < 0.08
        src = random.choice(ATACANTES if anomalo else NORMALES)
        ts = rand_ts()
        if anomalo:
            packet = random.randint(8000, 65000)
            dur = round(random.uniform(0.01, 0.5), 3)        # ráfagas cortas
            bsent = random.randint(500000, 5000000)
        else:
            packet = random.randint(40, 1500)
            dur = round(random.uniform(0.1, 30), 3)
            bsent = random.randint(100, 200000)
        rows.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "src_ip": src,
            "dst_ip": f"10.0.0.{random.randint(1,50)}",
            "protocol": random.choice(PROTOCOLOS),
            "packet_size": packet,
            "duration": dur,
            "flag": random.choice(["SYN", "ACK", "FIN", "RST", "PSH"]),
            "bytes_sent": bsent,
            "bytes_received": random.randint(64, 100000),
        })
    for _ in range(int(n * 0.015)):
        rows.append(dict(random.choice(rows)))
    for r in random.sample(rows, int(len(rows) * 0.02)):
        r["duration"] = ""
    random.shuffle(rows)
    _write("network_traffic.csv", rows,
           ["timestamp", "src_ip", "dst_ip", "protocol", "packet_size",
            "duration", "flag", "bytes_sent", "bytes_received"])
    return len(rows)


# ---------------------------------------------------------------------------
# 3) login_attempts.csv
# ---------------------------------------------------------------------------
def gen_logins(n=9000):
    usuarios = ["admin", "root", "jdoe", "mflores", "soporte", "sa",
                "test", "guest", "administrator", "oracle", "backup"]
    rows = []
    for _ in range(n):
        ataque = random.random() < 0.5
        if ataque:
            src = random.choice(ATACANTES)
            user = random.choice(["admin", "root", "administrator", "sa", "test"])
            exito = random.random() < 0.05
            pais = random.choice(["China", "Rusia", "Corea del Norte", "Irán"])
            motivo = "" if exito else random.choice(
                ["bad_password", "user_not_found", "account_locked"])
        else:
            src = random.choice(NORMALES)
            user = random.choice(usuarios)
            exito = random.random() < 0.85
            pais = random.choice(PAISES)
            motivo = "" if exito else "bad_password"
        ts = rand_ts()
        rows.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "username": user,
            "src_ip": src,
            "country": pais,
            "success": str(exito).lower(),
            "failure_reason": motivo,
        })
    for _ in range(int(n * 0.02)):
        rows.append(dict(random.choice(rows)))
    for r in random.sample(rows, int(len(rows) * 0.02)):
        r["country"] = ""
    random.shuffle(rows)
    _write("login_attempts.csv", rows,
           ["timestamp", "username", "src_ip", "country", "success", "failure_reason"])
    return len(rows)


def _write(name, rows, fields):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    fw = gen_firewall()
    nt = gen_network()
    lg = gen_logins()
    print(f"firewall_logs.csv   -> {fw:>6} filas")
    print(f"network_traffic.csv -> {nt:>6} filas")
    print(f"login_attempts.csv  -> {lg:>6} filas")
    print("Datasets generados en datasets/")
