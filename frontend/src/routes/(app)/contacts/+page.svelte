<script>
  import { resolve } from '$app/paths';
  import { page } from '$app/state';
  import { onMount } from 'svelte';
  import { stageDuration, exactTime } from '$lib/v2/contact-time.js';
  let clock = $state(Date.now());
  import PageHeader from '$lib/v2/components/PageHeader.svelte';
  import FilterBar from '$lib/v2/components/FilterBar.svelte';
  import { count, relativeDays } from '$lib/v2/format.js';
  import { Plus } from '@lucide/svelte';

  /** @type {{ data: any }} */
  let { data } = $props();
  const fields = [
    ['name', 'Name'],
    ['phone', 'Phone'],
    ['email', 'Email'],
    ['source_label', 'Source'],
    ['stage_label', 'Stage'],
    ['owner', 'Contact Owner'],
    ['address_line', 'Address'],
    ['city', 'City'],
    ['postcode', 'Zip Code'],
    ['state', 'State'],
    ['preferred_communication_channel_label', 'Preferred Communication Channel'],
    ['description', 'Notes'],
    ['account', 'Account'],
    ['is_active', 'Active'],
    ['do_not_call', 'Do not call'],
    ['created_at', 'Created'],
    ['updated_at', 'Updated']
  ];
  const defaults = ['name', 'phone', 'email', 'source_label', 'stage_label', 'owner'];
  let selected = $state([...defaults]);
  let configuring = $state(false);
  const storageKey = 'crm.contacts.columns.v1';
  onMount(() => {
    const timer = setInterval(() => {
      clock = Date.now();
    }, 60000);
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) ?? 'null');
      if (Array.isArray(saved)) {
        const valid = fields.map(([key]) => key).filter((key) => saved.includes(key));
        if (valid.length) selected = valid;
      }
    } catch {
      /* Browser storage is optional. */
    }
    return () => clearInterval(timer);
  });
  /** @param {string[]} next */
  function saveColumns(next) {
    selected = next;
    try {
      localStorage.setItem(storageKey, JSON.stringify(next));
    } catch {
      /* Keep session choice. */
    }
  }
  /** @param {string} key */
  function toggleColumn(key) {
    saveColumns(
      selected.includes(key) ? selected.filter((value) => value !== key) : [...selected, key]
    );
  }
  /** @param {Record<string, string | null>} changes */
  function link(changes) {
    const url = new URL(page.url);
    for (const [key, value] of Object.entries(changes)) {
      if (value === null) url.searchParams.delete(key);
      else url.searchParams.set(key, value);
    }
    return resolve('/contacts') + url.search;
  }
  /** @param {any} contact @param {string} key */
  function cell(contact, key) {
    if (key === 'account') return contact.account?.name || contact.organization || '—';
    if (key === 'owner')
      return contact.owner
        ? `${contact.owner}${contact.owner_count > 1 ? ` +${contact.owner_count - 1}` : ''}`
        : 'Unassigned';
    if (key === 'is_active' || key === 'do_not_call') return contact[key] ? 'Yes' : 'No';
    if (key.endsWith('_at')) return contact[key] ? relativeDays(contact[key]) : '—';
    return contact[key] || '—';
  }
</script>

<PageHeader title="Contacts">
  {#snippet sub()}<span class="v2-num">{count(data.totals.count)}</span> people{/snippet}
  {#snippet actions()}
    <a class="v2-btn" href={link({ inactive: data.includeInactive ? null : '1', offset: null })}
      >{data.includeInactive ? 'Hide inactive' : 'Show inactive'}</a
    >
    <a class="v2-btn v2-btn-primary" href={resolve('/contacts/new')}><Plus />New contact</a>
  {/snippet}
</PageHeader>

<div class="view-toolbar">
  <nav aria-label="Contact views">
    <a
      class="v2-btn"
      class:v2-btn-primary={data.view === 'list'}
      aria-current={data.view === 'list' ? 'page' : undefined}
      href={link({ view: 'list' })}>List</a
    >
    <a
      class="v2-btn"
      class:v2-btn-primary={data.view === 'pipeline'}
      aria-current={data.view === 'pipeline' ? 'page' : undefined}
      href={link({ view: 'pipeline' })}>Pipeline</a
    >
  </nav>
  {#if data.view === 'list'}
    <button
      class="v2-btn"
      aria-expanded={configuring}
      aria-controls="contact-columns"
      onclick={() => (configuring = !configuring)}>Edit columns</button
    >
  {/if}
</div>
{#if configuring && data.view === 'list'}
  <fieldset id="contact-columns" class="columns-picker">
    <legend>Fields shown in the list</legend>
    <p class="v2-sub">Choose at least one field. Saved in this browser.</p>
    <div class="column-options">
      {#each fields as [key, label]}
        <label
          ><input
            type="checkbox"
            checked={selected.includes(key)}
            disabled={selected.length === 1 && selected.includes(key)}
            onchange={() => toggleColumn(key)}
          />{label}</label
        >
      {/each}
    </div>
    <button class="v2-btn" onclick={() => saveColumns([...defaults])}>Restore defaults</button>
    <button class="v2-btn" onclick={() => (configuring = false)}>Done</button>
  </fieldset>
{/if}
<FilterBar
  page="contacts"
  url={page.url}
  people={data.people}
  tags={data.tags}
  meId={data.meId}
  meta="Most recently added first"
/>

<div class="v2-scroll">
  {#if data.view === 'pipeline'}
    <div class="contact-board" aria-label="Contacts by stage">
      {#each data.board as stage (stage.value)}
        <section class="stage-column" aria-label={stage.label}>
          <header>
            <h2>{stage.label}</h2>
            <span class="v2-num">{count(stage.count)}</span>
          </header>
          {#each stage.contacts as contact (contact.id)}
            <article class="contact-card">
              <a class="card-name" href={resolve(`/contacts/${contact.id}`)}
                ><strong>{contact.name}</strong></a
              >
              <dl>
                <dt>Phone</dt>
                <dd>{contact.phone || '—'}</dd>
                <dt>Email</dt>
                <dd>{contact.email || '—'}</dd>
                <dt>Source</dt>
                <dd>{contact.source_label || '—'}</dd>
                <dt>Owner</dt>
                <dd>{cell(contact, 'owner')}</dd>
                <dt>Channel</dt>
                <dd>{contact.preferred_communication_channel_label || '—'}</dd>
              </dl>
              {#if contact.do_not_call}<p class="v2-sub">Do not call</p>{/if}
              {#if !contact.is_active}<p class="v2-sub">Inactive</p>{/if}
              <a class="v2-btn" href={resolve(`/contacts/${contact.id}/edit`)}>Edit contact</a>
              <div class="card-dates">
                <span
                  class="stage-time"
                  title={contact.stage_entered_at
                    ? `Stage entered: ${exactTime(contact.stage_entered_at)}`
                    : 'Stage entry time was not recorded for this older contact'}
                  >{stageDuration(contact.stage_entered_at, clock)}</span
                >
                <time datetime={contact.created_at}>Created {exactTime(contact.created_at)}</time>
              </div>
            </article>
          {:else}<p class="v2-sub">No contacts on this page.</p>{/each}
          <footer>
            {#if stage.offset > 0}<a
                class="v2-btn"
                aria-label={`Previous ${stage.label} page`}
                href={link({
                  [`${stage.value}_offset`]: String(Math.max(0, stage.offset - data.pageSize))
                })}>Previous</a
              >{/if}
            {#if stage.offset + data.pageSize < stage.count}<a
                class="v2-btn"
                aria-label={`Next ${stage.label} page`}
                href={link({ [`${stage.value}_offset`]: String(stage.offset + data.pageSize) })}
                >Next</a
              >{/if}
          </footer>
        </section>
      {/each}
    </div>
  {:else}
    <div class="v2-table-wrap">
      <table class="v2-table">
        <thead
          ><tr
            >{#each fields.filter(([key]) => selected.includes(key)) as [key, label]}<th>{label}</th
              >{/each}<th>Actions</th></tr
          ></thead
        >
        <tbody>
          {#each data.contacts as contact (contact.id)}
            <tr>
              {#each fields.filter(([key]) => selected.includes(key)) as [key]}
                <td class="contact-cell">
                  {#if key === 'name'}<a
                      class="v2-row-link v2-table-primary"
                      href={resolve(`/contacts/${contact.id}`)}>{contact.name}</a
                    >
                  {:else if key === 'email' && contact.email}<a href={`mailto:${contact.email}`}
                      >{contact.email}</a
                    >
                  {:else}{cell(contact, key)}{/if}
                </td>
              {/each}
              <td
                ><a href={resolve(`/contacts/${contact.id}`)}>Open</a> ·
                <a href={resolve(`/contacts/${contact.id}/edit`)}>Edit</a></td
              >
            </tr>
          {:else}<tr><td colspan={selected.length + 1}>No contacts on this page.</td></tr>{/each}
        </tbody>
      </table>
    </div>
    <div class="pagination">
      <span class="v2-sub"
        >Showing {data.contacts.length ? data.offset + 1 : 0}–{data.contacts.length
          ? data.offset + data.contacts.length
          : 0} of {count(data.totals.count)}</span
      >
      {#if data.offset > 0}<a
          class="v2-btn"
          href={link({ offset: String(Math.max(0, data.offset - data.pageSize)) })}>Previous</a
        >{/if}
      {#if data.offset + data.pageSize < data.totals.count}<a
          class="v2-btn"
          href={link({ offset: String(data.offset + data.pageSize) })}>Next</a
        >{/if}
    </div>
  {/if}
</div>

<style>
  .card-dates {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 5px;
    margin-top: 16px;
    text-align: right;
    font-size: 11px;
    color: #666;
  }
  .stage-time {
    color: #a94312;
    background: #fff0e5;
    padding: 4px 8px;
    border-radius: 5px;
    font-weight: 600;
  }

  .view-toolbar,
  .view-toolbar nav,
  .pagination {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .view-toolbar {
    justify-content: space-between;
    padding: 12px 24px;
  }
  .columns-picker {
    margin: 0 24px 16px;
    padding: 16px;
    border: 1px solid #d6d7d9;
    border-radius: 8px;
  }
  .column-options {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 12px;
    margin: 16px 0;
  }
  .column-options label {
    display: flex;
    gap: 8px;
    align-items: center;
    font-size: 13px;
  }
  .contact-cell {
    max-width: 300px;
    white-space: normal;
    overflow-wrap: anywhere;
  }
  .pagination {
    padding: 20px 24px;
  }
  .contact-board {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    overflow-x: auto;
    padding: 16px 24px 32px;
    min-height: 400px;
  }
  .stage-column {
    flex: 0 0 290px;
    background: #f5f5f3;
    border: 1px solid #dededb;
    border-radius: 10px;
    padding: 12px;
  }
  .stage-column header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
  }
  .stage-column h2 {
    font-size: 14px;
    font-weight: 650;
    margin: 0;
  }
  .contact-card {
    background: white;
    border: 1px solid #dededb;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 12px;
  }
  .card-name {
    display: flex;
    align-items: center;
    gap: 8px;
    color: inherit;
    text-decoration: none;
    overflow-wrap: anywhere;
  }
  dl {
    display: grid;
    grid-template-columns: 55px minmax(0, 1fr);
    gap: 7px;
    font-size: 12px;
    margin: 16px 0;
  }
  dt {
    color: #666;
  }
  dd {
    margin: 0;
    overflow-wrap: anywhere;
  }
  footer {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
  }
</style>
