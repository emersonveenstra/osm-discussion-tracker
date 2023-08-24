<script setup lang="ts">
defineProps<{
  changesetId: string,
  userName: string,
  hasResponse: string,
  numChangesetsAfter: string
}>()
</script>

<template>
  <div class="changeset-card {{ (hasResponse === 'true') ? 'has-response' : 'no-response' }}">
	<span class="changeset-id">{{ changesetId }}</span>
	<span class="changeset-userName">{{ userName }}</span>
	<span class="changesets-after">Changesets since you commented: {{ numChangesetsAfter }}</span>
  </div>
</template>
