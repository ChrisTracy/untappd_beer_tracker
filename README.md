# Untappd_Beer_Tracker


Docker-Compose (Recommended):

```yaml
version: "3"
services:
  beer_tracker:
    build: .
    environment:
      UNTAPPD_USERNAME: "mikesmith"
      INTERVAL: "60"
    volumes:
      - beer_data:/app/data
    ports:
      - "8089:8089"
volumes:
  beer_data:
```
