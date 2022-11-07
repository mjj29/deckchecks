export interface ITablePlayer {
	name: string,
	score: bigint,
	checks: Array<bigint>
}
export interface ITableRound {
	round: bigint,
	players: Array<ITablePlayer>
}
export interface ITable {
	number: bigint,
	table: Array<ITableRound>
}
