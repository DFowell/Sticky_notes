# Testing

## Automated tests

|Area|What is checked|
|-|-|
|URLs|Each path resolves to the right view; `reverse()` builds the right paths|
|Model|`\\\_\\\_str\\\_\\\_`, `get\\\_absolute\\\_url`, timestamps, ordering, max length, blank values|
|Form|Only title and content are exposed; valid data saved; missing or too-long values rejected|
|View all notes|Page loads, empty state, notes listed, newest first, long text truncated, HTML escaped|
|View one note|Note shown; unknown id gives 404|
|Create|Form loads; valid POST saves and redirects; success message; invalid POST saves nothing|
|Edit|Form prefilled; valid POST updates (no duplicate); invalid POST leaves note unchanged; 404|
|Delete|GET only asks for confirmation; POST deletes and redirects; only the chosen note is removed; 404|
|Workflow|One test runs create, read, update and delete end to end|

**Result of my last run:** 38 tests, OK

