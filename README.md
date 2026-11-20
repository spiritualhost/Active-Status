# Active Status

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

Get daily Windows server and workstation activation status in the amount of days remaining for the trial period. The server daemon sends email notifications to a desired address from your personal SMTP server.

Frequent testing of Windows machines will have a lot of them looking like this:

![countdown](client/assets/countdown.png)

Eval period machines will often slip into regular production use and, often at the very worst time, will expire and begin intermittently shutting down. To prevent this, it's a good idea to keep an eye on your machines -- this gets far more difficult when you admin hundreds of servers. That's what this tool sets out to remedy.

For info on the server-side daemon, go [to the README here](server/SERVER.md). For info on the client-side, go [to the README here](client/CLIENT.md).
