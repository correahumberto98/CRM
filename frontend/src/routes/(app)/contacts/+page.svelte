<script>
  import { resolve } from '$app/paths';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  let dragging = $state('');
  let insertionIndex = $state(-1);
  /** @type {HTMLCanvasElement | null} */
  let dragPreview = null;
  let suppressSort = false;
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
  let ready = $state(false);
  /** @type {Record<string, number>} */
  let widths = $state({});
  let orderedFields = $derived(
    selected
      .map((key) => fields.find((field) => field[0] === key))
      .filter((field) => field !== undefined)
  );
  let pickerFields = $derived([
    ...orderedFields,
    ...fields.filter(([key]) => !selected.includes(key))
  ]);
  let totalWidth = $derived(selected.reduce((sum, key) => sum + (widths[key] ?? 160), 120));
  const widthKey = 'crm.contacts.widths.v1';
  const storageKey = 'crm.contacts.columns.v1';
  onMount(() => {
    const timer = setInterval(() => {
      clock = Date.now();
    }, 60000);
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey) ?? 'null');
      if (Array.isArray(saved)) {
        const valid = [...new Set(saved.filter((key) => fields.some((field) => field[0] === key)))];
        if (valid.length) selected = valid;
      }
    } catch {
      /* Browser storage is optional. */
    }
    try {
      const savedWidths = JSON.parse(localStorage.getItem(widthKey) ?? '{}');
      for (const [key] of fields) {
        if (
          typeof savedWidths?.[key] === 'number' &&
          Number.isFinite(savedWidths[key]) &&
          savedWidths[key] >= 60
        )
          widths[key] = savedWidths[key];
      }
    } catch {
      /* Stored layout is optional. */
    }
    ready = true;
    return () => {
      clearInterval(timer);
      dragPreview?.remove();
    };
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
  /** @param {string} key @param {number} direction */
  function moveColumn(key, direction) {
    const next = [...selected];
    const index = next.indexOf(key);
    const target = index + direction;
    if (index < 0 || target < 0 || target >= next.length) return;
    next.splice(index, 1);
    next.splice(target, 0, key);
    saveColumns(next);
  }
  /** @param {DragEvent} event @param {string} key */
  function startColumnDrag(event, key) {
    dragging = key;
    insertionIndex = selected.indexOf(key);
    suppressSort = true;
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', key);
      createDragPreview(event, key);
    }
  }
  /** @param {DragEvent} event @param {string} key */
  function createDragPreview(event, key) {
    dragPreview?.remove();
    const header = /** @type {HTMLElement} */ (event.currentTarget).closest('th');
    const table = header?.closest('table');
    const width = Math.min(widths[key] ?? 160, 480);
    const height = Math.min(table?.getBoundingClientRect().height ?? 200, 480);
    const canvas = document.createElement('canvas');
    canvas.width = width + 40;
    canvas.height = height + 40;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.shadowColor = 'rgba(15, 23, 42, 0.3)';
    ctx.shadowBlur = 14;
    ctx.shadowOffsetY = 6;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(20, 20, width, height);
    ctx.shadowColor = 'transparent';
    ctx.fillStyle = '#eaf3ff';
    ctx.fillRect(20, 20, width, 42);
    ctx.strokeStyle = '#3b82f6';
    ctx.strokeRect(20.5, 20.5, width - 1, height - 1);
    ctx.save();
    ctx.beginPath();
    ctx.rect(30, 20, width - 20, height);
    ctx.clip();
    const font = getComputedStyle(document.body).fontFamily;
    ctx.font = `600 13px ${font}`;
    ctx.fillStyle = '#1e3a5f';
    ctx.fillText(fields.find((field) => field[0] === key)?.[1] ?? key, 34, 46);
    ctx.font = `14px ${font}`;
    ctx.fillStyle = '#334155';
    for (let index = 0; index < data.contacts.length && 84 + index * 44 < height + 20; index++) {
      ctx.fillText(
        String(cell(data.contacts[index], key)).replace(/\s+/g, ' '),
        34,
        84 + index * 44
      );
      ctx.strokeStyle = '#e2e8f0';
      ctx.beginPath();
      ctx.moveTo(20, 104 + index * 44);
      ctx.lineTo(width + 20, 104 + index * 44);
      ctx.stroke();
    }
    ctx.restore();
    canvas.style.cssText = 'position:fixed;left:-10000px;top:0;pointer-events:none;';
    document.body.appendChild(canvas);
    dragPreview = canvas;
    event.dataTransfer?.setDragImage(
      canvas,
      Math.min(
        width / 2 + 20,
        Math.max(20, event.clientX - (header?.getBoundingClientRect().left ?? event.clientX) + 20)
      ),
      36
    );
  }
  /** @param {DragEvent} event */
  function previewPosition(event) {
    if (!dragging) return;
    event.preventDefault();
    if (event.dataTransfer) event.dataTransfer.dropEffect = 'move';
    const region = /** @type {HTMLElement} */ (event.currentTarget);
    const headers = Array.from(region.querySelectorAll('th[data-column]'));
    const index = headers.findIndex((header) => {
      const rect = header.getBoundingClientRect();
      return event.clientX < rect.left + rect.width / 2;
    });
    insertionIndex = index < 0 ? selected.length : index;
    const bounds = region.getBoundingClientRect();
    if (event.clientX > bounds.right - 30) region.scrollLeft += 18;
    else if (event.clientX < bounds.left + 30) region.scrollLeft -= 18;
  }
  /** @param {DragEvent} event */
  function dropColumn(event) {
    if (!dragging) return;
    previewPosition(event);
    const source = selected.indexOf(dragging);
    if (source >= 0 && insertionIndex >= 0) {
      const next = selected.filter((key) => key !== dragging);
      next.splice(insertionIndex > source ? insertionIndex - 1 : insertionIndex, 0, dragging);
      saveColumns(next);
    }
    finishDrag();
  }
  /** @param {DragEvent} event */
  function leaveColumns(event) {
    const region = /** @type {HTMLElement} */ (event.currentTarget);
    if (!region.contains(/** @type {Node | null} */ (event.relatedTarget))) insertionIndex = -1;
  }
  function finishDrag() {
    dragging = '';
    insertionIndex = -1;
    dragPreview?.remove();
    dragPreview = null;
    setTimeout(() => {
      suppressSort = false;
    }, 250);
  }
  /** @param {string} key */
  function sortBy(key) {
    if (suppressSort) return;
    const direction =
      page.url.searchParams.get('sort') === key && page.url.searchParams.get('direction') !== 'desc'
        ? 'desc'
        : 'asc';
    goto(link({ sort: key, direction, offset: null }));
  }
  function saveWidths() {
    try {
      localStorage.setItem(widthKey, JSON.stringify(widths));
    } catch {
      /* Keep session layout. */
    }
  }
  /** @param {string} key @param {number} width */
  function resizeColumn(key, width) {
    if (!Number.isFinite(width)) return;
    widths[key] = Math.max(60, Math.round(width));
    saveWidths();
  }
  /** @param {string} key */
  function fitColumn(key) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    if (!context) return 160;
    context.font = '600 13px ' + getComputedStyle(document.body).fontFamily;
    const label = fields.find((field) => field[0] === key)?.[1] ?? key;
    let size = context.measureText(label).width;
    context.font = '600 14px ' + getComputedStyle(document.body).fontFamily;
    for (const contact of data.contacts) {
      size = Math.max(
        size,
        context.measureText(String(cell(contact, key)).replace(/\s+/g, ' ')).width
      );
    }
    return Math.max(96, Math.ceil(size) + 40);
  }
  $effect(() => {
    if (!ready || data.view !== 'list') return;
    let changed = false;
    for (const key of selected) {
      if (!widths[key]) {
        widths[key] = fitColumn(key);
        changed = true;
      }
    }
    if (changed) saveWidths();
  });
  function fitVisible() {
    for (const key of selected) widths[key] = fitColumn(key);
    saveWidths();
  }
  /** @param {PointerEvent} event @param {string} key */
  function startResize(event, key) {
    if (event.button !== 0) return;
    event.preventDefault();
    const handle = /** @type {HTMLElement} */ (event.currentTarget);
    const startX = event.clientX;
    const startWidth = widths[key] ?? 160;
    handle.setPointerCapture(event.pointerId);
    const move = (/** @type {PointerEvent} */ e) => {
      widths[key] = Math.max(60, Math.round(startWidth + e.clientX - startX));
    };
    const end = () => {
      handle.removeEventListener('pointermove', move);
      handle.removeEventListener('pointerup', end);
      handle.removeEventListener('pointercancel', end);
      handle.removeEventListener('lostpointercapture', end);
      saveWidths();
    };
    handle.addEventListener('pointermove', move);
    handle.addEventListener('pointerup', end);
    handle.addEventListener('pointercancel', end);
    handle.addEventListener('lostpointercapture', end);
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
    <p class="v2-sub">
      Choose the fields to show. Drag column headers to change their order. Saved in this browser.
    </p>
    <div class="column-options">
      {#each pickerFields as [key, label] (key)}
        <div class="column-setting">
          <label
            ><input
              type="checkbox"
              checked={selected.includes(key)}
              disabled={selected.length === 1 && selected.includes(key)}
              onchange={() => toggleColumn(key)}
            />{label}</label
          >
        </div>
      {/each}
    </div>
    <button class="v2-btn" onclick={() => saveColumns([...defaults])}
      >Restore default columns</button
    >
    <button class="v2-btn" onclick={fitVisible}>Fit widths to content</button>
    <button class="v2-btn" onclick={() => (configuring = false)}>Done</button>
  </fieldset>
{/if}
<FilterBar
  page="contacts"
  url={page.url}
  people={data.people}
  tags={data.tags}
  meId={data.meId}
  meta={data.view === 'list' && page.url.searchParams.get('sort')
    ? `Sorted by ${fields.find(([key]) => key === page.url.searchParams.get('sort'))?.[1] ?? 'column'} · ${page.url.searchParams.get('direction') === 'desc' ? 'descending' : 'ascending'}`
    : 'Most recently added first'}
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
    <p class="v2-sub table-hint">
      Click a header to sort; drag its name to reorder. Drag the right edge to resize.
    </p>
    <!-- svelte-ignore a11y_no_noninteractive_tabindex (Keyboard users need to focus this overflow region to scroll the table.) -->
    <div
      class="contact-table-scroll"
      ondragover={previewPosition}
      ondrop={dropColumn}
      ondragleave={leaveColumns}
      role="region"
      aria-label="Contact list, horizontally scrollable"
      tabindex="0"
    >
      <table class="contact-grid" style:width={`${totalWidth}px`}>
        <colgroup
          >{#each orderedFields as [key]}<col style:width={`${widths[key] ?? 160}px`} />{/each}<col
            style:width="120px"
          /></colgroup
        >
        <thead
          ><tr>
            {#each orderedFields as [key, label] (key)}
              <th
                scope="col"
                data-column={key}
                class:drag-source={dragging === key}
                class:insert-before={dragging !== '' && insertionIndex === selected.indexOf(key)}
                class:insert-after={dragging !== '' &&
                  insertionIndex === selected.length &&
                  selected.indexOf(key) === selected.length - 1}
                aria-sort={page.url.searchParams.get('sort') === key
                  ? page.url.searchParams.get('direction') === 'desc'
                    ? 'descending'
                    : 'ascending'
                  : 'none'}
              >
                <button
                  class="column-heading"
                  class:dragging={dragging === key}
                  draggable="true"
                  title="Click to sort; drag to reorder. Alt + arrow keys also move the column."
                  onclick={() => sortBy(key)}
                  ondragstart={(event) => startColumnDrag(event, key)}
                  ondragend={finishDrag}
                  onkeydown={(event) => {
                    if (event.altKey && ['ArrowLeft', 'ArrowRight'].includes(event.key)) {
                      event.preventDefault();
                      moveColumn(key, event.key === 'ArrowLeft' ? -1 : 1);
                    }
                  }}
                >
                  {label}{page.url.searchParams.get('sort') === key
                    ? page.url.searchParams.get('direction') === 'desc'
                      ? ' ↓'
                      : ' ↑'
                    : ''}
                </button>
                <button
                  class="resize-handle"
                  aria-label={`Resize ${label}`}
                  title="Drag to resize; arrow keys adjust width; double-click to fit content"
                  onpointerdown={(event) => startResize(event, key)}
                  ondblclick={() => resizeColumn(key, fitColumn(key))}
                  onkeydown={(event) => {
                    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
                      event.preventDefault();
                      resizeColumn(
                        key,
                        (widths[key] ?? 160) + (event.key === 'ArrowRight' ? 10 : -10)
                      );
                    }
                  }}
                ></button>
              </th>
            {/each}<th scope="col">Actions</th>
          </tr></thead
        >
        <tbody>
          {#each data.contacts as contact (contact.id)}
            <tr>
              {#each orderedFields as [key] (key)}
                <td
                  class="contact-cell"
                  title={String(cell(contact, key))}
                  class:drag-source={dragging === key}
                  class:insert-before={dragging !== '' && insertionIndex === selected.indexOf(key)}
                  class:insert-after={dragging !== '' &&
                    insertionIndex === selected.length &&
                    selected.indexOf(key) === selected.length - 1}
                >
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
  .contact-grid .drag-source {
    background: #eff6ff;
    opacity: 0.5;
  }
  .contact-grid .insert-before {
    box-shadow: inset 3px 0 0 #2563eb;
  }
  .contact-grid .insert-after {
    box-shadow: inset -3px 0 0 #2563eb;
  }

  .column-setting {
    border: 1px solid var(--v2-line);
    border-radius: 6px;
    padding: 10px;
    min-width: 0;
  }
  .table-hint {
    padding: 0 24px;
    font-size: 12px;
  }
  .contact-table-scroll {
    overflow: auto;
    max-width: 100%;
    min-width: 0;
    margin: 0 24px 18px;
    border: 1px solid var(--v2-line);
    border-radius: 8px;
  }
  .contact-grid {
    table-layout: fixed;
    border-collapse: collapse;
    background: var(--v2-card);
    font-size: 14px;
  }
  .contact-grid th,
  .contact-grid td {
    box-sizing: border-box;
    padding: 10px 14px;
    text-align: left;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    border-right: 1px solid var(--v2-line-soft);
    border-bottom: 1px solid var(--v2-line-soft);
  }
  .contact-grid th {
    position: relative;
    font-size: 13px;
    font-weight: 600;
    color: var(--v2-slate);
  }
  .column-heading {
    width: 100%;
    border: 0;
    padding: 0;
    text-align: left;
    font: inherit;
    color: inherit;
    background: transparent;
    cursor: grab;

    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .contact-grid td {
    height: 44px;
  }
  .contact-grid tbody tr:hover {
    background: var(--v2-hover);
  }
  .contact-cell > a {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .contact-grid a {
    color: inherit;
  }
  .column-heading.dragging {
    opacity: 0.4;
  }
  .resize-handle {
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 9px;
    border: 0;
    padding: 0;
    background: transparent;
    cursor: col-resize;
    touch-action: none;
  }
  .resize-handle:hover,
  .resize-handle:focus-visible {
    background: var(--v2-slate);
    opacity: 0.45;
  }

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
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
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
