export interface ICheckRound {
	round: bigint,
	players: Array<string>
}
export interface IChecks {
	totalchecked: bigint,
	checks: Array<ICheckRound>
}
