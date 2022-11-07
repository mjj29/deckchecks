export interface IRecommendPlayer {
	name: string,
	score: bigint,
	checks: Array<bigint>
}
export interface IRecommend {
	table: bigint,
	players: Array<IRecommendPlayer>
}
export interface IRecommends {
	recommendations: Array<IRecommend>,
	random: Array<IRecommend>
}
