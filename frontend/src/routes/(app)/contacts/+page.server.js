import { listContacts, FILTER_FIELDS } from '$lib/server/v2/contacts.js';
import { readFilters, buildFilterQuery } from '$lib/server/v2/filter-params.js';
import { getOrgPeopleAndTeams, resolveMe } from '$lib/server/v2/org-people.js';
import { getTags } from '$lib/server/v2/tags.js';

/**
 * Only filters the API actually applies are forwarded. A parameter that
 * changes the URL and nothing else teaches people the filter bar is decorative.
 *
 * `inactive=1` in the URL is kept from the fixture page, because the question
 * it asks is a good one, but it is answered by the API now (`?is_active=`)
 * rather than by discarding rows after they arrive, which was only ever right
 * on the first page.
 *
 * The pickers are fetched here rather than inside `listContacts` for the same
 * reason as `tickets.js`: a picker fetch folded into the list read would cost
 * a redundant request on every caller that reads contacts for their totals
 * alone.
 *
 * @type {import('./$types').PageServerLoad}
 */
export async function load({ cookies, url, locals }) {
  const params = buildFilterQuery(FILTER_FIELDS, readFilters(url, 'contacts'));
  for (const key of ['search', 'name', 'email', 'phone']) {
    const value = url.searchParams.get(key);
    if (value) params.set(key, value);
  }

  const includeInactive = url.searchParams.get('inactive') === '1';
  if (!includeInactive) params.set('is_active', 'true');

  const view = url.searchParams.get('view') === 'pipeline' ? 'pipeline' : 'list';
  if (view === 'list') {
    params.set('sort', url.searchParams.get('sort') ?? '');
    params.set('direction', url.searchParams.get('direction') === 'desc' ? 'desc' : 'asc');
  }
  const pageSize = 25;
  const offset = Math.max(
    0,
    Math.min(10000000, Number.parseInt(url.searchParams.get('offset') ?? '0') || 0)
  );
  params.set('limit', view === 'pipeline' ? '1' : String(pageSize));
  params.set('offset', view === 'pipeline' ? '0' : String(offset));
  const [{ results, totals, stages }, orgPeople, tagList] = await Promise.all([
    listContacts({ cookies }, params),
    getOrgPeopleAndTeams(cookies),
    // A failed tag fetch should cost the Tag dropdown in the filter bar, not
    // the whole list. Follows the tickets.js pattern; see the note there.
    getTags({ cookies }).catch(() => ({ tags: [] }))
  ]);

  const board =
    view === 'pipeline'
      ? await Promise.all(
          [...stages, { value: 'UNASSIGNED', label: 'No stage' }].map(async (stage) => {
            const stageOffset = Math.max(
              0,
              Math.min(
                10000000,
                Number.parseInt(url.searchParams.get(`${stage.value}_offset`) ?? '0') || 0
              )
            );
            const query = new URLSearchParams(params);
            query.set('stage', stage.value);
            query.set('limit', String(pageSize));
            query.set('offset', String(stageOffset));
            const response = await listContacts({ cookies }, query);
            return {
              ...stage,
              contacts: response.results,
              count: response.totals.count,
              offset: stageOffset
            };
          })
        )
      : [];

  return {
    view,
    board,
    offset,
    pageSize,
    contacts: results,
    totals,
    includeInactive,
    search: params.get('search') ?? '',
    people: orgPeople.people,
    tags: tagList.tags ?? [],
    meId: resolveMe(orgPeople.people, /** @type {any} */ (locals).user?.email)
  };
}
