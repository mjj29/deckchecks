export interface IPlayer {
	tables: Array<string>,
	name: string,
	buildtable: bigint,
	listid: string,
	score: bigint,
	checks: Array<bigint>
}
export interface IPlayers {
	player: Array<IPlayer>
}
