import { ref } from 'vue'
import { defineStore } from 'pinia'
import { osmAuth } from 'osm-auth'


export const useUserStore = defineStore('user', () => {
	const userID = ref(0)
	const username = ref('')
	const accessToken = ref(window.localStorage.getItem('https://www.openstreetmap.orgoauth2_access_token') || '')
	const auth = osmAuth({
		client_id: "qFeGC16EFxzSLHyEljEJkSxMcwsuI9E9Wt269xFB5BY",
		redirect_uri: window.location.origin + '/login',
		scope: "read_prefs write_diary write_api",
		auto: true,
		singlepage: true,
	});

	function getAuthDetails() {
		auth.fetch('https://www.openstreetmap.org/api/0.6/user/details.json')
			.then(response => response.json())
			.then(rjson => {
				userID.value = rjson.user.id;
				username.value = rjson.user.display_name;
				accessToken.value = window.localStorage.getItem('https://www.openstreetmap.orgoauth2_access_token') || ''
			})
	}

	if (accessToken.value !== '') {
		auth.preauth({"access_token": accessToken.value})
		getAuthDetails()
	}

	return { userID, username, accessToken, auth, getAuthDetails }
})