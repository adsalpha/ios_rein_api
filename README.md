# Rein REST API for the iOS App

This API currently supplies Rein jobs for the Rein iOS app.

## Query paths

### `/jobs`

Return all valid Rein jobs. Fields included - `Job name`, `Job ID`, `Tags`, `Description`, `Expires at`, `Job creator`, `Job creator contact`, `Mediator`, `Mediator contact`.
No more fields are necessary for the app at the moment.

## Setup

First, clone this repo. `cd` into its directory.

Then, request Let's Encrypt certificates for the URL which is specified in `docker-compose.yaml`.
Symlink them to `${PWD}/nginx/ssl`

Run `docker-compose up` and enjoy the magic!
