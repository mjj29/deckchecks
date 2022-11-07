export interface ITopPlayer {
	name: string,
	score: int,
	checks: List<int>
}
export interface ITopTable {
	table: int,
	livestatus: string,
	players: List<ITopPlayer>
}
export interface ITop {
	top: List<ITopTable>
}
