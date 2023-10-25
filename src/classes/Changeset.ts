export class Changeset {
	constructor (
		public csid: number = 0,
		public username: string = "none",
		public ts: Date = new Date(),
		public hasResponse: boolean = false,
		public hasNewChangesets: boolean = false,
		public lastActivity: Date = new Date()
	) {}
}