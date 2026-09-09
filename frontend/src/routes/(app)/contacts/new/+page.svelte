<script>
  import { resolve } from '$app/paths';
  import PageHeader from '$lib/v2/components/PageHeader.svelte';
  import ContactForm from '$lib/components/contacts/ContactForm.svelte';
  import { ChevronRight } from '@lucide/svelte';
  /** @type {{data:any, form:any}} */
  let { data, form } = $props();
</script>

<PageHeader title="New contact" center>
  {#snippet crumb()}<a href={resolve('/contacts')}>Contacts</a><ChevronRight size={12} /><span
      >New</span
    >{/snippet}
</PageHeader>
<div class="v2-scroll v2-pad" style="padding-top:18px">
  <ContactForm {data} result={form} editing={false} />
</div>
