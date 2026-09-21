# Coursera Downloader — Master Plan

This file is the source of truth for the project. Complete work phase-by-phase, update checkboxes after verification, and commit each meaningful checkpoint.

## Phase 1 — Foundation
- [ ] Refactor the single-file prototype into a maintainable project structure
- [ ] Add `requirements.txt`
- [ ] Add `.env.example`
- [ ] Add application configuration module
- [ ] Add Coursera authentication/service wrapper
- [ ] Remove the hard-coded local `venv/Lib/site-packages` path hack
- [ ] Add a basic test suite
- [ ] Add a project README with local setup/run instructions
- [ ] Add downloads/runtime folders to `.gitignore`
- [ ] Verify the app still imports/starts with the new structure

## Phase 2 — Authentication
- [ ] Add browser-cookie authentication
- [ ] Add CAUTH cookie support
- [ ] Validate authentication before loading courses
- [ ] Persist session safely without committing credentials
- [ ] Detect expired sessions
- [ ] Provide clear re-authentication guidance
- [ ] Keep username/password login only as a compatibility fallback if useful

## Phase 3 — Course Library
- [ ] Retrieve enrolled courses
- [ ] Add course search/filtering
- [ ] Display course metadata
- [ ] Retrieve course curriculum/modules
- [ ] Enumerate downloadable lessons/files
- [ ] Add course detail view

## Phase 4 — Download Configuration & Engine
- [ ] Download videos
- [ ] Download subtitles
- [ ] Download PDFs
- [ ] Download readings/HTML
- [ ] Download assignments
- [ ] Download supplementary files
- [ ] Add video-resolution selector
- [ ] Add subtitle-language selector
- [ ] Add destination-folder configuration
- [ ] Preserve course/module folder structure
- [ ] Skip existing files safely
- [ ] Sanitize filenames
- [ ] Wrap `coursera-dl` behind a stable service interface

## Phase 5 — Download Manager
- [ ] Create persistent download jobs
- [ ] Add download queue
- [ ] Track per-file and overall progress
- [ ] Add real cancel support
- [ ] Add pause/resume where technically feasible
- [ ] Retry failed items
- [ ] Persist download state
- [ ] Persist/download logs
- [ ] Handle app restart without losing history

## Phase 6 — Local Library & History
- [ ] Add SQLite persistence
- [ ] Store downloaded courses
- [ ] Store downloaded files/items
- [ ] Show download history
- [ ] Detect missing files
- [ ] Re-download missing files
- [ ] Update an already-downloaded course
- [ ] Open course/download folder from the UI

## Phase 7 — UI Polish & Reliability
- [ ] Improve course/library layout
- [ ] Add download dashboard
- [ ] Add settings page
- [ ] Add storage/disk-space information
- [ ] Add friendly typed error messages
- [ ] Handle network failures
- [ ] Handle authentication failures
- [ ] Handle unavailable content
- [ ] Handle rate limiting
- [ ] Improve accessibility and responsive layout

## Phase 8 — Distribution
- [ ] Define supported Python/Windows versions
- [ ] Create portable Windows build
- [ ] Create installer if useful
- [ ] Add application versioning
- [ ] Add GitHub release workflow
- [ ] Document upgrades and troubleshooting

## Working Rules
1. `MASTER_PLAN.md` is the project source of truth.
2. Do not mark a task complete until it has been implemented and reasonably verified.
3. Update this file as part of each phase/task completion.
4. Commit and push meaningful completed checkpoints.
5. Avoid committing Coursera credentials, cookies, sessions, downloaded course content, or other private data.
