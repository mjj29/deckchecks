export interface IPairingPlayer {
	name: string,
	score: bigint
}
export interface IPairing {
	table: bigint,
	players: Array<IPairingPlayer>
}
export interface IPairings {
	round: bigint,
	pairings: Array<IPairing>
}
