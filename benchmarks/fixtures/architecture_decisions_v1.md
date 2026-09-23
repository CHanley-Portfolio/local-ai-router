# Architecture Planning Notes

Several options were considered during early planning.

One idea was to expose Ollama-specific request names directly throughout the
application.

Another idea was to store benchmark results only as JSON files.

A possible future experiment may investigate alternative inference backends.

## Final Decisions

1. Application-facing routing contracts will use backend-independent names.

2. Backend-specific parameter translation will occur inside inference adapters.

3. Historical benchmark results will use PostgreSQL as the authoritative
   persistent store.

The earlier ideas of exposing backend terminology throughout the application
and using loose JSON files as the authoritative benchmark history are rejected.