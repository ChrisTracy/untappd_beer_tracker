# Untappd_Beer_Tracker

Docker pull:

```sh
docker pull christracy/untappd_beer_tracker
```

Docker-Compose (Recommended):

```yaml
version: "3"
services:
  beer_tracker:
    image: christracy/untappd_beer_tracker
    restart: unless-stopped
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
