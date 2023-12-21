<script setup lang="ts">
import { useUserStore } from '@/stores/user';
const userData = useUserStore();
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'
import { computed, ref, type Ref } from 'vue'
import { useRoute, useRouter } from 'vue-router';

const router = useRouter()
const route = useRoute()

const { result, loading, refetch, onResult } = useQuery(gql`
query MyQuery($csid: Int!, $uid: Int!) {
	getChangesetDetails(csid: $csid, uid: $uid) {
		csid
		uid
		username
		ts
		csComment
		comments {
			username
			ts
			text
		}
		notes {
			username
			ts
			text
		}
		flags {
			username
			ts
			text
		}
		status
		statusDate
	}
}`, () => ({
	csid: parseInt(route.params.changeset, 10),
	uid: userData.userID,
}))

const changeset_details = computed(() => result.value?.getChangesetDetails ?? false)

const statusText = computed(() => result.value?.getChangesetDetails.status ?? 'missing')
const status = ref('');

const pendingComments: Ref<string[]> = ref([])

let allComments = computed(() => result.value?.getChangesetDetails.comments ?? []);
let allNotes = computed(() => result.value?.getChangesetDetails.notes ?? []);
let allFlags = computed(() => result.value?.getChangesetDetails.flags ?? []);

onResult(queryResult => {
	if (queryResult.loading)
		return;
	status.value = statusText.value
})
const achaviChangeset = computed(() => {
	return `https://overpass-api.de/achavi/?changeset=${route.params.changeset}&relations=true`
})

async function updateChangeset(status_value: string) {
	const data = {
		uid: userData.userID,
		csid: [route.params.changeset],
		status: status_value,
		snoozeUntil: ''
	}
	if (status_value === 'snoozed') {
		const currentTime = new Date();
		const daysToSnooze = parseInt(document.getElementById('daysToSnooze')?.value ?? '0', 10);
		currentTime.setTime(currentTime.getTime() + (daysToSnooze * 86400 * 1000))
		data.snoozeUntil = currentTime.toISOString();
	}
	console.log(data)
	try {
		const response = await fetch("http://127.0.0.1:8000/status", {
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

async function showUserModal(username: string) {
	router.push(`/user/${username}`)
}

async function submitComment() {
	const newComment = document.querySelector('.comment-textarea')?.value || '';
	pendingComments.value.push(newComment);
}

async function submitNote(isFlag: boolean = false) {
	const newNote = document.querySelector('.comment-textarea')?.value || '';
	const data = {
		csid: route.params.changeset,
		username: userData.username,
		note: newNote,
		isFlag: isFlag
	}
	try {
		const response = await fetch("http://127.0.0.1:8000/addChangesetNote", {
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
			<h1>Changeset {{ route.params.changeset }}</h1>
			<a :href="`https://www.openstreetmap.org/changeset/${route.params.changeset}`">OSM.org</a>
			<p>
				Status:
				<select v-model="status">
					<option value="watched">Watched</option>
					<option value="resolved">Resolved</option>
					<option value="snoozed">Snoozed</option>
					<option value="unwatched">Unwatched</option>
				</select>
				<span v-if="status == 'snoozed'">for <input id="daysToSnooze" type="number" value="3"> days</span>
				<button @click="updateChangeset(status)">Update</button>
			</p>
		</div>
		<span>by <span @click="showUserModal(changeset_details.username)">{{ changeset_details.username }}</span> on {{ changeset_details.ts }}Z</span>
		<p>{{ changeset_details.csComment }}</p>
		<section class="discussion"> 
			<h2>Discussion</h2>
			<div class="flag-section-wrap" v-if="allFlags.length > 0">
				<h3>Flags</h3>
				<div class="flag-wrap" v-for="flag in allFlags" :key="flag['ts']">
					<div class="flag">
						<p class="metadata">Flag from <a :href="`https://www.openstreetmap.org/user/${flag.username}`">{{ flag.username }}</a> at {{ flag.ts.replace('T', ' ') }}Z</p>
						<p class="flag-text">{{ flag.text }}</p>
					</div>
				</div>
			</div>
			<div class="comment-section-wrap" v-if="allComments.length > 0 || pendingComments.length > 0">
				<h3>Comments</h3>
				<div class="comment-wrap" v-for="comment in allComments" :key="comment['ts']">
					<div class="comment">
						<p class="metadata">Comment from <a :href="`https://www.openstreetmap.org/user/${comment.username}`">{{ comment.username }}</a> at {{ comment.ts.replace('T', ' ') }}Z</p>
						<p class="comment-text">{{ comment.text }}</p>
					</div>
				</div>
				<div class="pending-comment-wrap" v-for="comment in pendingComments" :key="comment.length">
					<div class="comment">
						<p class="metadata">Pending comment</p>
						<p class="comment-text">{{ comment }}</p>
					</div>
				</div>
			</div>
			<div class="note-section-wrap" v-if="allNotes.length > 0">
				<h3>Notes</h3>
				<div class="note-wrap" v-for="note in allNotes" :key="note['ts']">
					<div class="note">
						<p class="metadata">Note from <a :href="`https://www.openstreetmap.org/user/${note.username}`">{{ note.username }}</a> at {{ note.ts.replace('T', ' ') }}Z</p>
						<p class="note-text">{{ note.text }}</p>
					</div>
				</div>
			</div>
			<section class="add-comment">
				<textarea class="comment-textarea"></textarea>
				<button class='submit-comment' @click="submitComment()">Comment</button>
				<button class='submit-note' @click="submitNote()">Note</button>
				<button class='submit-flag' @click="submitNote(true)">Flag</button>
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
	.add-comment textarea {
		width: 100%;
		height: 100px;
		display: block;
	}
	.add-comment button, .actions button {
		margin-top: 10px;
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