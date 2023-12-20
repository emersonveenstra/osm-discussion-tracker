<template>
	<section class="help-page">
		<h1>Intro</h1>
		<p>OSM Discussion Tracker is a web application to keep track of and follow up on changeset discussions, for both teaching new (or old!) users and curbing vandalism in OSM.</p>
		<p>Once logged in, the left sidebar displays a list of your watched changesets. By default, a watched changeset is a changeset you have commented on or a changeset of yours that someone else commented on. Changesets can also be watched by importing OSMCha RSS feeds, and manually by going to a changeset's URL (e.g. https://osmdiscussiontracker.com/#1000000 to view changeset 1000000) and changing the status.</p>
		<h2>Changeset detail</h2>
		<p>Clicking a changeset in the sidebar or going to a changeset URL will display the changeset detail page, showing all the information about the changeset.</p>
		<h3>Change Status</h3>
		<p>You can change the status of a changeset on either the changeset detail page, or selecting the changeset(s) in the sidebar. Changesets can be in one of 4 states:</p>
		<ul>
			<li>Unwatched: The default, will not show up on your sidebar</li>
			<li>Watched: The changeset will show up on the sidebar</li>
			<li>Snoozed: The changeset will be hidden from the sidebar (unless you use the filter to show them) for a specified number of days, then will return to the watched state</li>
			<li>Resolved: The changeset will be hidden from the sidebar (unless you use the filter to show them)</li>
		</ul>
		<blockquote>For both snoozed and resolved changesets, if a user comments on the changeset, it will revert to the watched state.</blockquote>
		<h3>Changeset Comment/Note</h3>
		<p>On a changeset page, you can add a comment or note. Adding a comment will add a standard OSM comment to the changeset, then either snooze or resolve the changeset. Adding a note will display the note in ODT, but not create a comment. Notes are <b>PUBLIC</b> and viewable by anyone logged into ODT, so please use them only for notes about escalations and other relevant information and do not use the notes as a way to avoid engaging users.</p>
		<h3>Flag Changeset</h3>
		<p>Flagging a changeset is a quick way to mark it as malicious. The option to flag changesets is only available after you've written a changeset, to avoid using the flagging system as a way to avoid engaging users. Flagging a changeset shows up for all users, and a list of flagged changesets shows up in a user's page. Because of this, only flag changesets that are malicious vandalism, do not flag changesets for honest mistakes or accidental vandalism. Admins have the ability to remove flags from a changeset, please respect their decision</p>
		<h2>Sidebar</h2>
		<p>When the sidebar first loads, it displays a list of all your watched changesets, sorted by recent activity.</p>
		<h3>Filtering</h3>
		<p>You can show/hide snoozed and resolved changesets using the Filter dropdown. Clicking on a changeset will display the changeset detail page. Selecting the checkbox of one or more changesets will display the option to change the status of the selected changeset(s). Currently there's a limit of 200 changesets displayed, to avoid overloading the server.</p>
		<h3>Flags</h3>
		<p>If a changeset has any flags, they are displayed below the comment.</p>
		<h2>User page</h2>
		<p>Clicking on a username on the changeset detail page will bring up details about a user.</p>
		<h3>User notes</h3>
		<p>Adding a user note will display in the notes section. As with changeset notes, these are PUBLIC to any logged in user, so please only use them for collaboration about escalations and vandalism.</p>
	</section>
</template>