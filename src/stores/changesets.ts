import { reactive, ref } from 'vue'
import { defineStore } from 'pinia'
import { Changeset } from '@/classes/Changeset'

export const useChangesetStore = defineStore('changesets', () => {
  const currentChangeset = ref(0)
  const watchedChangesets: Map<number, Changeset> = reactive(new Map<number, Changeset>())

  return { currentChangeset, watchedChangesets }
})