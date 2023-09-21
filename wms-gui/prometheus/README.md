# Prometheus configuration files

The files here are scrape stanzas for the various WEKAmon containers.

The idea is if a service is enabled, the associated stanza is copied to the prometheus.yml file, and the 
prometheus.yml can be customized by this UI, turning scraping services on and off as desired.

