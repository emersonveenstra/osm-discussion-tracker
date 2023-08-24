import type { Discussion } from "./Discussion";

export class Changeset {
	constructor (
		public id: number,
		public userName: string,
		public timestamp: Date,
		public discussion: Set<Discussion>,
		public hasResponse: boolean,
		public numChangesetsAfter: number
	) {}
}