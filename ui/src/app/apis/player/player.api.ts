export interface IPlayer {
	tables: List<string>,
	name: string,
	buildtable: int,
	listid: string,
	score: int,
	checks: List<int>
}
export interface IPlayers {
	player: List<IPlayer>
}
