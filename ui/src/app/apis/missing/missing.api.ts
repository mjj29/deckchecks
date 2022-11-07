export interface IMissingPlayer {
	player: string,
	table: bigint
}
export interface IMissing {
	missing: Array<IMissingPlayer>,
	extra: Array<string>
}
