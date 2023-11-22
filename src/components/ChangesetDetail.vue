<script setup lang="ts">
import { useChangesetStore } from '@/stores/changesets';
const changesetData = useChangesetStore();
import { useUserStore } from '@/stores/user';
const userData = useUserStore();
import { useQuery } from '@vue/apollo-composable'
import gql from 'graphql-tag'
import { computed } from 'vue'

const { result, loading, error, refetch, onResult } = useQuery(gql`
query MyQuery($csid: Int!) {
	getChangesetDetails(csid: $csid) {
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
	}
}`, () => ({
		csid: changesetData.currentChangeset,
		}))

const changeset_details = computed(() => result.value?.getChangesetDetails ?? false)

function resolveChangeset() {
	fetch(`http://127.0.0.1:8000/resolve?uid=${userData.userID}&csid=${changesetData.currentChangeset}`)
}

const achaviChangeset = computed(() => {
	return `https://overpass-api.de/achavi/?changeset=${changesetData.currentChangeset}&relations=true`
})

</script>

<template>
	<div :v-if="changeset_details" class="changeset-detail">
		<h1>Changeset {{ changesetData.currentChangeset }}</h1>
		<span>by {{ changeset_details.username }} on {{ changeset_details.ts }}</span>
		<p>View on:
			<a :href="`https://www.openstreetmap.org/changeset/${changesetData.currentChangesetClass.csid}`">OSM.org</a>
			<a :href="`https://osmcha.org/changesets/${changesetData.currentChangeset}`">OSMCha</a>
		</p>
		<p class="flags">
			<span class="needs-reply" v-if="changesetData.currentChangesetClass.hasResponse">Needs Reply</span>
			<span class="needs-escalation" v-else-if="changesetData.currentChangesetClass.hasNewChangesets">Needs Escalation</span>
		</p>
		<section class="discussion"> 
			<h2>Discussion</h2>
			<div v-for="comment in changeset_details['discussion']" :key="comment['ts']">
				<p class="metadata">Comment from <a :href="`https://www.openstreetmap.org/user/${comment.username}`">{{ comment.username }}</a> at {{ comment.ts }}</p>
				<p class="comment-text">{{ comment.comment }}</p>
			</div>
			<section class="changeset-viewer">
				<iframe :src="achaviChangeset"></iframe>
			</section>
			<section class="comment">
				<p>Add comment to changeset:</p>
				<textarea></textarea>
				<button @click="resolveChangeset">Resolve changeset</button>
			</section>
		</section>
		
	</div>
</template>

<style>
	.comment-text {
		white-space: pre;
		text-wrap: wrap;
	}
	.changeset-viewer iframe {
		width: 100%;
		height: 600px;
	}
</style>