# Project Database Decision

## Final Decision

The application will use PostgreSQL as its production relational database.

PostgreSQL was selected because the system requires durable relational storage,
historical benchmark queries, explicit relationships, migrations, and future
reporting.

SQLite may still be useful for isolated experiments or disposable tests, but
it must not become the production application database.