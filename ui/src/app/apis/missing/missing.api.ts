export interface IMissingPlayer {
	player: string,
	table: int
}
export interface IMissing {
	missing: List<IMissingPlayer>,
	extra: List<string>
}
