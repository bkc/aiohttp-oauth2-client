## [2.0.1] - 2025-09-11
### 🐛 Bug Fixes

- Cast token `expires_in` field to `int` to be compatible with APIs returning a string ([#3](https://github.com/VITObelgium/aiohttp-oauth2-client/pull/3))

## [2.0.0] - 2025-06-18

### 🚀 Features

- Use middleware functionality of aiohttp ClientSession instead of subclassing
