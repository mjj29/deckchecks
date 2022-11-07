export interface ITopPlayer {
	name: string,
	score: bigint,
	checks: Array<bigint>
}
export interface ITopTable {
	table: bigint,
	livestatus: string,
	players: Array<ITopPlayer>
}
export interface ITop {
	top: Array<ITopTable>
}
