<script setup lang="ts">
import { Discussion } from '@/classes/Discussion';
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
const changesetId = changesetData.currentChangeset
const userName = "testing"
const timestamp = new Date()
const discussions = new Set<Discussion>()
discussions.add(new Discussion('testing3', new Date(), "testing hi"))
</script>

<template>
  <h1>Changeset {{ changesetId }}</h1>
  <span>by {{ userName }} on {{ timestamp.toISOString() }}</span>
  <section class="discussion"> 
    <h2>Discussion</h2>
    <div v-for="discussion in discussions.keys()" :key="discussion.timestamp.toISOString()">
      <span class="username">{{ discussion.userName }} at {{ discussion.timestamp.toISOString() }} said:</span>
      <p>{{ discussion.message }}</p>
    </div>
  </section>
  <section class="changeset-viewer">
  </section>
</template>