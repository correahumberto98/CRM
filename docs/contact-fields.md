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
