<script setup lang="ts">
	import { useUserStore } from '@/stores/user';
	const userData = useUserStore();

	async function triggerAuth() {
		userData.auth.fetch('https://www.openstreetmap.org/api/0.6/user/details.json')
			.then(response => response.json())
			.then(rjson => {
				console.log([rjson.user.id, rjson.user.display_name])
				userData.userID = rjson.user.id
				userData.username = rjson.user.display_name
			})
	}
</script>
<template>
	<section>
		<h1>ODT</h1>
	</section>
	<section class="login" v-if="userData.access_token === ''">
		<button @click="triggerAuth" class="trigger-login">Please Login to OSM</button>
	</section>
</template>