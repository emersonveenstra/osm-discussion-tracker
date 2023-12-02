<script setup lang="ts">
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
import { useUserStore } from '@/stores/user';
const userData = useUserStore();
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'
import { computed, ref } from 'vue'

const { result, loading, error, refetch, onResult } = useQuery(gql`
query MyQuery($csid: Int!, $uid: Int!) {
	getChangesetDetails(csid: $csid, uid: $uid) {
		csid
		uid
		username
		ts
		comment
		discussion {
			username
			ts
			comment
		}
		status
	}
}`, () => ({
	csid: changesetData.currentChangeset,
	uid: userData.userID,
}))

const changeset_details = computed(() => result.value?.getChangesetDetails ?? false)

const status = ref(changeset_details.value.status);
const statusText = computed(() => result.value?.getChangesetDetails.status ?? false)

const achaviChangeset = computed(() => {
	return `https://overpass-api.de/achavi/?changeset=${changesetData.currentChangeset}&relations=true`
})

function commentChangeset() {
	fetch(`http://127.0.0.1:8000/resolve?uid=${userData.userID}&csid=${changesetData.currentChangeset}`)
}

async function updateChangeset(status_value: string) {
	const data = {
		uid: userData.userID,
		csid: changesetData.currentChangeset,
		status: 'resolve',
		snoozeUntil: null
	}
	let url = `http://127.0.0.1:8000/${status_value}`;
	if (status_value === 'snooze') {
		const currentTime = new Date();
		const daysToSnooze = parseInt(document.getElementById('daysToSnooze')?.value ?? '0', 10);
		currentTime.setTime(currentTime.getTime() + (daysToSnooze * 86400 * 1000))
		data.snoozeUntil = currentTime.toISOString();
		data.status = 'snooze'
		url = "http://127.0.0.1:8000/resolve"
	}
	console.log(data)
	try {
		const response = await fetch(url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify(data),
		});

		const result = await response.json();
		console.log("Success:", result);
		refetch()
	} catch (error) {
		console.error("Error:", error);
	}
}

</script>

<template>
	<div :v-if="!loading" class="changeset-detail">
		<div class="header">
			<h1>Changeset {{ changesetData.currentChangeset }}</h1>
			<a :href="`https://www.openstreetmap.org/changeset/${changesetData.currentChangesetClass.csid}`">OSM.org</a>
			<a :href="`https://osmcha.org/changesets/${changesetData.currentChangeset}`">OSMCha</a>
		</div>
		<span>by {{ changeset_details.username }} on {{ changeset_details.ts }}Z</span>
		<p>{{ changeset_details.comment }}</p>
		<section class="discussion"> 
			<h2>Discussion</h2>
			<div class="comment-wrap" v-for="comment in changeset_details['discussion']" :key="comment['ts']">
				<p class="metadata">Comment from <a :href="`https://www.openstreetmap.org/user/${comment.username}`">{{ comment.username }}</a> at {{ comment.ts.replace('T', ' ') }}Z</p>
				<p class="comment-text">{{ comment.comment }}</p>
			</div>
			<section class="comment">
				<textarea></textarea>
				<button @click="commentChangeset">Comment</button>
			</section>
			<section class="actions">
				<h2>Status: {{ statusText }}</h2>
				<select v-model="status">
					<option value="unresolve">Watch</option>
					<option value="resolve">Resolve</option>
					<option value="snooze">Snooze</option>
				</select>
				<span v-if="status == 'snooze'">for <input id="daysToSnooze" type="number" value="3"> days</span>
				<button @click="updateChangeset(status)" :disabled="status === ''">Update</button>
			</section>
			<section class="changeset-viewer">
				<iframe :src="achaviChangeset"></iframe>
			</section>
		</section>
	</div>
</template>

<style>
	.changeset-detail {
		padding: 0 1em;
	}
	.header * {
		display: inline-block;
		vertical-align: middle;
	}
	.header a {
		padding-left: 10px;
	}
	.discussion {
		margin-top: 30px;
	}
	.comment-wrap {
		padding: 10px 0;
	}
	.metadata {
		font-size: 0.75em;
	}
	.comment-text {
		white-space: pre;
		text-wrap: wrap;
		padding-left: 10px;
	}
	.comment textarea {
		width: 100%;
		height: 100px;
		display: block;
	}
	.comment button, .actions button {
		margin-top: 10px;
		appearance: none;
		border: none;
		padding: 10px 20px;
	}
	.actions {
		padding-top: 20px;
	}
	.actions p {
		padding-bottom: 10px;
	}
	.actions label {
		display: block;
	}
	.changeset-viewer {
		margin-top: 40px;
	}
	.changeset-viewer iframe {
		width: 100%;
		height: 600px;
	}
</style>