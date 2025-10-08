# Architecture: Overview

This repo is organized as follows:

- `.vscode`: Recommended extensions and settings
- `data-store`: Defines **shared** data-store components for the digital twin platform, e.g. PostgreSQL, InfluxDB, Neo4j.
- `dev-docs`: These docs.
- `infra`: Infrastructure components such as the Traefik reverse proxy and MQTT broker.
- `misc`: Components that do not fit neatly into any of the other categories, such as demonstrative/testing components.
- `node`: Node.js packages.  Note that we separate implementation from deployment; thus a software package should contain just the Dockerfile with any Docker Compose or Kubernetes configuration files placed in the correct deployment-related directory.
- `pypackages`: Python packages.
- `pytests`: PyTest modules.
- `scratch`: Place temporary scripts and notebooks (e.g. .ipynb) here; these will be ignored by Git.
- `scripts`: Shell scripts for developer convenience.
- `twins`: Collection of Docker Compose stacks / Helm charts corresponding to **digital twins** in the platform.  Each twin may have its own internal data storage, API and UI components, access control policies, etc.
- `ui`: Shared user interfaces for the DT platform, e.g. a login page or user management UI.
  - UIs tied to a specific component should belong under the directory for that component. For example, a PhpPgAdmin portal should go under `data-store/` while the Traefik dashboard should go under `infra/`.

## Platform architecture

(*Right-click &rarr; Open image in new tab* to view full-size.)

```kroki-plantuml
@startuml
!theme crt-green
cloud "IOT Network" {
  [Sensor 1]
  [Sensor 2]
  [Sensor 3]
}

package "MQTT bridge" as MQTTpkg {
  component "Eclipse Mosquitto\n(MQTT dumb\naggregator/pipe)" as Mosquitto {
    portin "MQTT                         " as MQTTin
    portout "MQTT            " as MQTTout
  }
  [Packet filter\n& validator] as filter
  MQTTout <-- filter : subscribe
}

[Sensor 1] --> MQTTin: publish
[Sensor 2] --> MQTTin: publish
[Sensor 3] --> MQTTin: publish

package "DT Platform" as Platform {
  component "Reverse Proxy" as Traefik {
    portin "MQTT" as TraefikMQTT
    portin "HTTP         " as TraefikHTTP
  }

  interface "Internal\nnetwork" as Internal

  frame Databases {
    database "Relational\nDatabase" as SQL
    database "Time-series\nDB" as Influx
    database "Graph DB" as Neo4j
    [Data summary] <-up-> Influx
  }

  package "Auth / Admin" as Auth {
    component "API" as AuthAPI
    component "Login page" as Login
    component "User\nmanagement UI"
    component "Platform Metrics /\nMonitoring"
  }

  package  "Digital Twins" as DTs {
    package "Digital Twin 1" as DT {
      component UI
      component "API"
      component "Background\nworkers"
      database "Internal\nDB"
    }
    [DT 2]
    [DT 3]
  }

  database Registries {
    [Container\nimages]
    [Software\npackages]
    [DT manifest\nfiles]
    [compose.yaml\nfiles]
    [Helm charts]
  }
}

filter -right-> TraefikMQTT: publish

cloud Users
Users <-down-> TraefikHTTP

Traefik <--> Internal
Databases <-up-> Internal
Auth <--> Internal
DTs <--> Internal
Registries <-up--> Internal
```
