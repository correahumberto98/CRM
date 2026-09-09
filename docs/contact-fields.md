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
