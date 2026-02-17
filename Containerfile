FROM docker.io/prom/prometheus:v2.55.1

COPY prometheus.yml /etc/prometheus/prometheus.yml
COPY consoles/ /usr/share/prometheus/consoles/
COPY console_libraries/menu.lib /etc/prometheus/console_libraries/menu.lib
