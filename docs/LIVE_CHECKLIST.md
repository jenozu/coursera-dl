# Live verification checklist (roadmap 3.4, 8.1)

Manual, on Windows, with your own Coursera account and a course you are enrolled in.
Mark each cell: OK / FAIL (note) / n/a.

## Browser cookie reading

| Browser | Logged in, browser closed | Logged in, browser open | Logged out | Normal user | Administrator |
|---|---|---|---|---|---|
| Firefox | | | | | |
| Edge | | | | | |
| Brave | | | | | |

Manual CAUTH fallback works: ___

## End-to-end

- [ ] Connect, enrolled courses listed
- [ ] Download one small course, videos only
- [ ] Download the same course again with PDFs only (audit C-1): both sets present
- [ ] Force a failure (disconnect network mid-download): job shows failures, not success
- [ ] Cancel a running job; later resume completes
- [ ] Kill the process mid-download, restart: job shown as interrupted, resume works
- [ ] Sign out of Coursera in the browser: app shows session expired and recovers after reconnect
- [ ] App unreachable from another device on the network
- [ ] No cookie values in `data/logs/` or the database

Tester: ____  Date: ____  Python: ____  Windows: ____
