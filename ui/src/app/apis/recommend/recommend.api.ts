export interface IRecommendPlayer {
	name: string,
	score: int,
	checks: List<int>
}
export interface IRecommend {
	table: int,
	players: List<IRecommendPlayer>
}
export interface IRecommonds {
	recommendations: List<IRecommend>,
	random: List<IRecommend>
}
