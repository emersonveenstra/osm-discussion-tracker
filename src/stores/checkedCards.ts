import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useCheckedCardsStore = defineStore('checkedCards', () => {
	const currentCheckedCards = ref([])

	return { currentCheckedCards }
})