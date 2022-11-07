export interface ICheckRound {
	round: int,
	players: List<string>
}
export interface IChecks {
	totalchecked: int,
	checks: List<ICheckRound>
}
