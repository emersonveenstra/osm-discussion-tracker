import { computed, reactive, ref } from 'vue'
import { defineStore } from 'pinia'
import { Changeset } from '@/classes/Changeset'

export const useChangesetStore = defineStore('changesets', () => {
	const currentChangeset = ref(0)
	const watchedChangesets: Map<number, Changeset> = reactive(new Map<number, Changeset>())
	const currentChangesetClass = computed(() => watchedChangesets.get(currentChangeset.value) || new Changeset())

	return { currentChangeset, watchedChangesets, currentChangesetClass }
})