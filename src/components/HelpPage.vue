<template>
	<section class="help-page">
		<p>OSM Discussion Tracker is a web application to keep track of and follow up on changeset discussions, for both teaching new (and old!) users and curbing vandalism in OSM.</p>
		<p>Once logged in, the left sidebar displays a list of your watched changesets. By default, a watched changeset is a changeset you have commented on or a changeset of yours that someone else commented on. Changesets can also be watched manually by going to a changeset's URL (e.g. https://osmdiscussiontracker.com/changeset/1000000) and changing the status to Watched.</p>
		<h2>Sidebar</h2>
		<p>When the sidebar first loads, it displays a list of all your watched changesets, sorted by recent activity.</p>
		<h3>Filtering</h3>
		<p>You can show/hide snoozed and resolved changesets using the Filter dropdown. Clicking on a changeset will display the changeset detail page. Selecting the checkbox of one or more changesets will display the option to change the status of the selected changeset(s).</p>
		<h2>Changeset detail</h2>
		<p>Clicking a changeset in the sidebar or going to a changeset URL will display the changeset detail page, showing all the information about the changeset.</p>
		<h3>Change Status</h3>
		<p>You can change the status of a changeset on either the changeset detail page, or selecting the changeset(s) in the sidebar. Changesets can be in one of 4 states:</p>
		<ul>
			<li>Unwatched: The default, will not show up on your sidebar at all</li>
			<li>Watched: The changeset will show up on the sidebar</li>
			<li>Snoozed: The changeset will be hidden from the sidebar for a specified number of days, then will return to the watched state</li>
			<li>Resolved: The changeset will be hidden from the sidebar</li>
		</ul>
		<p>For both snoozed and resolved changesets, if a user comments on the changeset, it will revert to the watched state.</p>
		<h3>Changeset Comment/Note</h3>
		<p>On a changeset page, you can add a comment or note. Adding a comment will add a standard OSM comment to the changeset. Adding a note will display the note in ODT, but not create a comment in OSM. Notes are <b>PUBLIC</b> and viewable by anyone logged into ODT, so please use them only for notes about escalations and other relevant information and do not use the notes as a way to avoid engaging users.</p>
		<h2>Support</h2>
		<p>The main support channel is <a href="https://matrix.to/#/#osmdiscussiontracker:matrix.org">#osmdiscussiontracker:matrix.org</a> on Matrix (all GitHub users can access it via <a href="https://gitter.im">Gitter</a>). I'm also active in the #software channel of the <a href="https://discord.gg/openstreetmap">OSM World Discord</a>, feel free to ping me there.</p>
	</section>
</template>

<style>
	.help-page p, .help-page ul {
		padding-bottom: 10px;
	}

	h1,h2,h3,h4,h5,h6,b {
		font-weight: bold;
	}
</style>