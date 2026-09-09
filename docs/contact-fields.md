# Contact fields

Contact creation and editing use one Name field, Phone, optional Email, Source, Stage, Address, City, Zip Code, State, Preferred Communication Channel and Notes. Name, Phone, Source and Stage are required in the form and on API creation.

Source options: Meta, Google, TikTok, Organic, Call, Customer Referal, Employer Referal, Walk In.

Contact stages: Lead, Follow Up, Qualified, Not Qualified, Lost. These are independent of deal pipeline stages.

Communication channels: SMS, Call, Email. The field can be left unspecified.

Catalogs live in backend/contacts/choices.py and are returned by the contacts API for the frontend dropdowns. Notes uses the existing description field; Address uses address_line and Zip Code uses postcode (text, preserving leading zeros).

The API accepts name while retaining first_name and last_name compatibility. Existing split names remain unchanged when the displayed name is unchanged. New names are stored in first_name with an empty last_name. Existing contacts retain their data and have no assumed source, stage or channel. Partial API updates may omit required fields; the edit form asks for missing required values. Legacy imports and automatic contact creation continue to use their existing contracts.

Apply migrations before running the updated interface:

```sh
docker compose exec -T backend python manage.py migrate --noinput
```

Migrations 0014 and 0015 add the fields and finalize the selected catalogs. No contact rows are deleted or backfilled. Organization scoping and existing RLS policies remain in place.

## Contact views

The Contacts module offers List and Pipeline views. List starts with Name, Phone, Email, Source, Stage and Contact Owner. Edit columns can show or hide all contact form fields plus account, status and timestamps; at least one data column stays selected. Open/Edit actions remain available even when Name is hidden. Preferences are saved in this browser, not synchronized across devices.

Pipeline uses the contact stage catalog returned by the API. Each card shows name, phone, email, source, owner and preferred channel. Contacts without a recognized stage appear under No stage. Editing a contact's Stage changes its column on the next board load. Deal pipelines are independent.

Both views retain the existing contact filters and organization permissions. List uses 25 contacts per page; each pipeline column independently fetches 25 contacts and its own total, with Previous/Next controls. The board does not infer column totals from the first page of the contact list. The API's `stage=UNASSIGNED` filter includes null, blank and unrecognized stages.

## Stage age and contact history

Migration 0016 adds the server-managed `stage_entered_at`. New contacts start their clock at creation; subsequent Stage changes reset it. Editing other fields does not reset it. Existing contacts retain a null value because their historic stage entry time is unknown. Pipeline cards show this elapsed time in color and the creation timestamp at the lower right. Displayed dates include the timezone; elapsed times refresh every minute while the page is open.

The contact profile shows its original creation timestamp and creator, stage entry timestamp, and Contact history. History reads organization-scoped Activity rows only after the existing contact access check. Server-side signals record Contact creation, scalar field changes (including before/after values), deletion and many-to-many assignments/links; generic contact notes and attachments record additions, edits and removals. Opening the contact and requesting an attachment download are also recorded. A download-request event does not assert that the client completed the transfer. User identity is derived from the authenticated request's organization profile and snapshotted; operations without an attributable user are labeled System / actor unavailable. Creation can use an explicitly supplied server-side creator for background operations.

Contact saves and their audit writes run in the same transaction. Existing Activity RLS applies; no public write endpoint for history is added. Deleted-contact events remain in Activity, but a deleted contact no longer has a profile page. Older notes, files and creation information remain visible even if they predate detailed history. Prior modifications cannot be reconstructed when no historical record exists. The stage clock and creator are not writable through the contact form/API serializer.

This tracks persisted CRM operations, not external phone calls or emails merely launched from a link; those need a note or a future communication integration. Direct SQL, QuerySet.update/bulk_update and bulk_create bypass Django save signals and must explicitly emit audit records if introduced for contact business operations. No full-history backfill is fabricated.

## List column order and fixed widths

Edit columns only selects visible fields. Drag a column header name onto another header to insert it at that position; the order is saved in this browser. Alt + left/right arrow keys on the header provide a keyboard alternative. Header edges retain drag resizing, arrow-key width adjustment and double-click to fit content; there are no numeric width controls in Edit columns. Existing column selections and saved widths are preserved.

A newly displayed column is measured against its header and the currently loaded contact rows, then its width is saved. Loading another page or changing viewport size does not automatically resize it. Fit widths to content explicitly recalculates selected widths against the current page. Column widths have a 60-pixel minimum. Long content in manually narrowed cells is truncated with an ellipsis and remains accessible through its tooltip or by opening the contact.

The contact list uses its own fixed-layout table styles instead of the app's mobile card transformation. Small screens retain the same column widths and use horizontal scrolling. Preferences are local to the browser and are not synchronized between devices.

## Sorting by column

Click a column name to sort ascending; click it again to sort descending. The arrow and aria-sort indicate the direction. Dragging a header reorders columns without triggering sorting. Sorting is applied by the API before pagination and within the existing filters/access permissions; switching sort starts at the first page. Text is case-insensitive, dates sort chronologically, and blank values appear last. Phone numbers and ZIP codes are text identifiers. Catalog columns sort by their displayed labels. Multiple owners are represented by the first email alphabetically; account sorting uses the primary account or first linked account alphabetically, then the free-text organization. Unknown sorting keys fall back to creation order.
