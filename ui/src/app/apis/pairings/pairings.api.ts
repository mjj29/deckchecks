export interface IPairingPlayer {
	name: string,
	score: int
}
export interface IPairing {
	table: int,
	players: List<IPairingPlayer>
}
export interface IPairings {
	round: int,
	pairings: List<IPairing>
}
