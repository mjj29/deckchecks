export interface IPairingPlayer {
	name: string,
	score: number
}
export interface IPairing {
	table: number,
	players: Array<IPairingPlayer>
}
export interface IPairings {
	round: number,
	pairings: Array<IPairing>
}
