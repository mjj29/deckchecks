export interface IPairingPlayer {
	name: string,
	score: int,
	checks: List<int>
}
export interface ITableRound {
	round: int,
	players: List<ITablePlayer>
}
export interface ITable {
	number: int,
	table: List<ITableRound>
}
