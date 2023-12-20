import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', () => {
	const userID = ref(11548585)
	const oauthID = "qFeGC16EFxzSLHyEljEJkSxMcwsuI9E9Wt269xFB5BY";
	const oauthSecret = "eFpgb4m82XAPUdepOW_tM66mu9Ny3csBFVL4oUGJ6rU"
	const userModalID = ref(0)

	return { userID, oauthID, oauthSecret, userModalID }
})