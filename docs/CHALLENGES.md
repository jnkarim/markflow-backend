# Engineering Challenges — Villains Faced

The assignment asks not only for working code, but also for an explanation of the difficulties encountered and how they were overcome. These were the main villains in the MarkFlow backend saga.

## 1. Email-first authentication

**Villain:** Django's default user model is username-oriented, but the product requires email and password login.

**Resolution:** A custom user model and manager were created before application data migrations. `USERNAME_FIELD` uses email, passwords remain managed by Django's hashing system, and Simple JWT reads the custom identifier correctly.

**Lesson:** Authentication architecture should be decided at the beginning. Replacing the user model after a database already contains authentication tables is unnecessarily risky.

## 2. Daily board date versus deadline

**Villain:** Using one date for both board filtering and deadlines creates ambiguous behavior. Changing a deadline could make a task disappear from the selected board.

**Resolution:** The model keeps `task_date` and `due_date` separate. `task_date` controls the daily Kanban board; `due_date` communicates urgency. Validation prevents a deadline earlier than the board date.

**Lesson:** Similar-looking fields can represent different business concepts and should not be coupled for convenience.

## 3. Persistent drag-and-drop ordering

**Villain:** A visual drag is easy on the client, but persisting it can produce duplicate positions, gaps, or inconsistent source and destination columns.

**Resolution:** Reordering was moved into a dedicated service. It locks relevant rows, removes the task, inserts it at a clamped destination, normalizes affected positions, and commits everything atomically.

**Lesson:** Multi-row state transitions belong in a transaction and should be tested separately from view code.

## 4. User data isolation

**Villain:** Object IDs are predictable. A user could try another ID and access someone else's task, image, or polygon.

**Resolution:** Every queryset begins with the authenticated owner. Polygon ownership is inherited through its parent image. Unauthorized object IDs resolve to `404` instead of exposing existence.

**Lesson:** Ownership should be enforced in the query itself, not checked only after retrieving the object.

## 5. Responsive polygon persistence

**Villain:** Pixel coordinates only match one rendered image size. A polygon drawn at 900 pixels wide shifts when the same image is shown at 500 pixels.

**Resolution:** Polygon points are stored as normalized `0–1` values. The API validates the bounds and minimum distinct point count; the frontend converts between normalized and display coordinates.

**Lesson:** Persist coordinates in the subject's coordinate system, not the current browser viewport's coordinate system.

## 6. Trustworthy image uploads

**Villain:** A file extension or browser-provided MIME type does not prove that a file is a valid image.

**Resolution:** The upload pipeline checks file size and accepted MIME type, then asks Pillow to verify the actual image contents and read dimensions. Stored filenames are randomized while original names remain metadata.

**Lesson:** Client-provided file metadata is useful input, not a security guarantee.

## 7. Partial multi-file failures

**Villain:** In a batch upload, one bad file should not necessarily discard several valid files, but silently ignoring the bad file would confuse the user.

**Resolution:** Valid files are saved, invalid files are skipped, and warnings are returned in the `X-Upload-Warnings` response header. If every file fails, the endpoint returns a normal validation error.

**Lesson:** Batch APIs need an explicit partial-success contract.

## 8. Free-tier persistence

**Villain:** The assignment requires hosted database and image persistence without paid storage services.

**Resolution:** SQLite and local media storage are used for the small recruiter demo. Image count and file-size limits protect the available disk space. Deployment instructions include static and media mappings and recommend backups.

**Trade-off:** This is suitable for a controlled demonstration, not horizontal scaling. A production version should use PostgreSQL and object storage.

## 9. Frontend and backend on different origins

**Villain:** A Vercel frontend and PythonAnywhere API use different origins, so browsers block requests unless CORS is exact.

**Resolution:** Allowed and trusted origins come from comma-separated environment variables. Development and deployment instructions use exact schemes and hostnames without trailing slashes.

**Lesson:** CORS is part of deployment architecture, not a last-minute browser workaround.

## 10. Avoiding regression while developing branch by branch

**Villain:** Authentication, tasks, uploads, and polygons share settings and routes. A change in one area can accidentally break another.

**Resolution:** Features were separated into focused branches and pull requests. A 49-test suite plus GitHub Actions checks Django configuration, migrations, and all API applications on every PR.

**Lesson:** A professional Git history is useful only when each branch is independently understandable and verifiable.
