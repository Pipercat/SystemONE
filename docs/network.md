# SystemONE Netzwerk

## Ziel

SystemONE soll wie ein kompaktes Homelab-Datacenter betrieben werden: lokal stabil, remote sicher erreichbar und modular erweiterbar.

## Empfohlene physische Rollen

- **Intel Mini PC**: Hauptserver (Docker Host, Core Services)
- **Mac Mini**: Dev-/Cluster-Node (Builds, Experimente, Offloading)
- **NAS**: Persistente Daten, Backups, Dokumentenablage
- **Router (z. B. FritzBox)**: Segmentierung, DHCP, Port-/Tunnel-Policies

## Logische Netzwerkstruktur

```text
[Internet]
   |
[Cloudflare Tunnel]
   |
[NGINX Reverse Proxy]
   |
[SystemONE Services]
  |- /            -> Dashboard/UI
  |- /api         -> API
  |- /qdrant      -> Qdrant API
  |- /ollama      -> Ollama API (optional intern)
  |- /ha          -> Home Assistant Connector
```

## Routing- und Expositions-Regeln

- Extern wird nur der Reverse Proxy/Tunnel exponiert.
- Interne Services bleiben im Docker-Netz ohne direkte WAN-Exposition.
- Management-Interfaces nur über VPN/Tunnel zugänglich.

## Docker-Netzwerke (Empfehlung)

- `systemone-public`: nur NGINX + ggf. Web-UI
- `systemone-private`: API, Worker, Datenbanken, AI-Services
- `systemone-observability`: optionale Monitoring-Komponenten

## Basis-Checks

```bash
docker compose ps
docker compose logs -f api
docker compose logs -f nginx
curl http://localhost/api/health
curl http://localhost/
curl http://localhost/qdrant/collections
```

## Nächste Netzwerk-Schritte

1. Optionales VLAN für IoT/SmartHome-Geräte.
2. Strikte Firewall-Regeln zwischen Segmenten.
3. DNS-Namensschema für interne Services (`*.lab.local`).
