<template>
	<view class="container">
		<view class="report-header">
			<text class="report-title">练习报告</text>
			<text class="scene-name">{{sceneName}}</text>
		</view>
		
		<view class="report-content">
			<!-- 整体评分 -->
			<view class="score-section">
				<view class="overall-score">
					<text class="score-value">{{report.overall}}</text>
					<text class="score-label">总体评分</text>
				</view>
				
				<!-- 五维度评分雷达图 -->
				<view class="radar-chart">
					<canvas canvas-id="radarChart" id="radarChart" class="radar-canvas"></canvas>
				</view> 
				
				<!-- 各项评分 -->
				<view class="dimension-scores">
					<view class="dimension-item" v-for="(item, index) in report.dimensions" :key="index">
						<view class="dimension-bar-wrapper">
							<view class="dimension-name">{{item.name}}</view>
							<view class="dimension-bar-container">
								<view class="dimension-bar" :style="{width: item.score + '%'}">
									<text class="dimension-score">{{item.score}}</text>
								</view>
							</view>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 详细分析 -->
			<view class="analysis-section">
				<view class="section-title">详细分析</view>
				
				<view class="analysis-item" v-for="(item, index) in report.analysis" :key="index">
					<view class="analysis-header">
						<view class="analysis-title">{{item.title}}</view>
						<view class="analysis-score">{{item.score}}分</view>
					</view>
					<view class="analysis-content">
						<text>{{item.content}}</text>
					</view>
				</view>
			</view>
			
			<!-- 改进建议 -->
			<view class="suggestion-section">
				<view class="section-title">改进建议</view>
				
				<view class="suggestion-list">
					<view class="suggestion-item" v-for="(item, index) in report.suggestions" :key="index">
						<view class="suggestion-icon">{{index + 1}}</view>
						<view class="suggestion-content">
							<text>{{item}}</text>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<view class="action-buttons">
			<button class="share-btn" @click="shareReport">分享报告</button>
			<button class="back-btn" @click="backToHome">返回首页</button>
		</view>
	</view>
</template>

<script>
	import uCharts from '@/uni_modules/qiun-data-charts/js_sdk/u-charts/u-charts.js';
	import config from '@/config.js'
	
	export default {
		data() {
			return {
				radarSize: 300, // 默认
				sceneId: 0,
				sceneName: '',
				apiBaseUrl: config.apiBaseUrl,
				report: {
					overall: 85,
					dimensions: [
						{ name: '语言组织能力', score: 80 },
						{ name: '说服力', score: 75 },
						{ name: '流利度', score: 90 },
						{ name: '准确度', score: 85 },
						{ name: '语言表达', score: 83 }
					],
					analysis: [
						{
							title: '语言组织能力',
							score: 80,
							content: '您的语言组织整体较好，能够按照逻辑顺序表达自己的观点。但在某些回答中，内容结构可以更紧凑，减少不必要的铺垫。建议在回答前先在心中整理好要点，按照"总-分-总"的结构进行表达。'
						},
						{
							title: '说服力',
							score: 75,
							content: '您在阐述产品优势时的说服力有待提高。建议增加具体数据和案例支持，让客户更容易接受您的观点。例如"我们的产品帮助A公司在一个月内提升了销售额30%"这样的具体例子会更有说服力。'
						},
						{
							title: '流利度',
							score: 90,
							content: '您的语速适中，表达流畅，很少出现停顿或冗余词。在4次回答中，仅有1次出现了明显的停顿，整体流利度表现优秀。语速为每分钟约175个字，处于理想范围。'
						},
						{
							title: '准确度',
							score: 85,
							content: '您对产品特性的描述基本准确，能够清晰地传达核心价值。但在解释某些技术细节时有轻微的不准确。建议进一步熟悉产品的技术规格和核心参数，确保所有描述都完全准确。'
						},
						{
							title: '语言表达',
							score: 83,
							content: '您的语言表达整体清晰，用词专业，能够使用行业术语增强专业感。但有时用词略显重复，可以通过丰富词汇量来增加表达的多样性。建议多积累专业词汇，尤其是能精准描述产品价值的关键词。'
						}
					],
					suggestions: [
						'在回答客户问题前，可以先简短重复一下客户的问题，表明您理解了他们的需求，如"关于您提到的价格问题..."',
						'增加具体案例和数据支持，提高说服力。可以准备2-3个成功案例，在合适的时机分享。',
						'适当使用反问句引导客户思考，如"您是否考虑过长期使用后的总体成本？"这样的问题可以引导客户从新的角度看问题。',
						'在谈到产品优势时，可以结合客户所处的行业情况，使建议更有针对性。',
						'练习如何简洁有力地总结对话内容，在每个销售环节结束时进行小结，帮助客户和自己明确当前进展。'
					]
				}
			}
		},
		onLoad(options) {
			if (options.sceneId) {
				this.sceneId = parseInt(options.sceneId);
				this.getReportData();
			}
		},
		onReady() {
			const sysInfo = uni.getSystemInfoSync();
			this.radarSize = Math.floor(sysInfo.windowWidth * 0.9);
			this.initRadarChart();
		},
		methods: {
			initRadarChart() {
				const ctx = uni.createCanvasContext('radarChart', this);
				const size = this.radarSize || 300;
				const radarChart = new uCharts({
					type: 'radar',
					context: ctx,
					width: size,
					height: size,
					categories: this.report.dimensions.map(item => item.name),
					series: [{
						name: '评分',
						data: this.report.dimensions.map(item => item.score)
					}],
					animation: true,
					background: '#FFFFFF',
					padding: [size * 0.13, size * 0.13, size * 0.13, size * 0.13], // 13% padding，减小让图更居中
					legend: {
						show: false
					},
					radar: {
						gridType: 'radar',
						gridColor: '#ddd',
						gridCount: 4,
						labelColor: '#333',
						labelFontSize: Math.floor(size * 0.055), // 稍大
						splitArea: {
							show: true,
							areaStyle: {
								color: ['rgba(16,185,129,0.1)', 'rgba(16,185,129,0.2)', 'rgba(16,185,129,0.3)', 'rgba(16,185,129,0.4)']
							}
						},
						dataLabel: true,
						dataLabelColor: '#10b981',
						dataLabelFontSize: Math.floor(size * 0.045) // 稍大
					},
					extra: {
						radar: {
							linearType: 'custom',
							labelShow: true
						}
					}
				});
			},
			getReportData() {
				// 获取场景名称
				const sceneNames = {
                    0:'核苷酸介绍',
					1: '新客户开发',
					2: '异议处理',
					3: '产品推荐',
					4: '成交技巧'
				};
				this.sceneName = sceneNames[this.sceneId] || '未知场景';
				
				// 获取报告数据
				const reportId = uni.getStorageSync('latestReportId');
				if (reportId) {
					uni.showLoading({
						title: '加载报告...'
					});
					
					uni.request({
						url: `${this.apiBaseUrl}/reports/${reportId}`,
						success: (res) => {
							if (res.data) {
								console.log('获取报告成功:', res.data);
								
								// 格式化报告数据
								const reportData = res.data;
								const formattedReport = {
									overall: reportData.overall,
									dimensions: [
										{ name: '语言组织能力', score: reportData.dimensions.languageOrganization || 0 },
										{ name: '说服力', score: reportData.dimensions.persuasiveness || 0 },
										{ name: '流利度', score: reportData.dimensions.fluency || 0 },
										{ name: '准确度', score: reportData.dimensions.accuracy || 0 },
										{ name: '语言表达', score: reportData.dimensions.expression || 0 }
									],
									analysis: [
										{
											title: '语言组织能力',
											score: reportData.analysis.languageOrganization?.score || 0,
											content: reportData.analysis.languageOrganization?.content || ''
										},
										{
											title: '说服力',
											score: reportData.analysis.persuasiveness?.score || 0,
											content: reportData.analysis.persuasiveness?.content || ''
										},
										{
											title: '流利度',
											score: reportData.analysis.fluency?.score || 0,
											content: reportData.analysis.fluency?.content || ''
										},
										{
											title: '准确度',
											score: reportData.analysis.accuracy?.score || 0,
											content: reportData.analysis.accuracy?.content || ''
										},
										{
											title: '语言表达',
											score: reportData.analysis.expression?.score || 0,
											content: reportData.analysis.expression?.content || ''
										}
									],
									suggestions: reportData.suggestions || []
								};
								
								this.report = formattedReport;
								this.initRadarChart();
							}
						},
						fail: (err) => {
							console.error('获取报告失败:', err);
							uni.showToast({
								title: '获取报告失败',
								icon: 'none'
							});
						},
						complete: () => {
							uni.hideLoading();
						}
					});
				}
			},
			shareReport() {
				uni.showToast({
					title: '分享功能开发中',
					icon: 'none'
				});
			},
			backToHome() {
				uni.reLaunch({
					url: '/pages/index/index'
				});
			}
		}
	}
</script>

<style>
	.container {
		padding: 30rpx;
		display: flex;
		flex-direction: column;
		min-height: 100vh;
		box-sizing: border-box;
		background-color: #f5f5f5;
	}
	
	.report-header {
		background-color: #10b981;
		color: #fff;
		padding: 40rpx 30rpx;
		border-radius: 12rpx 12rpx 0 0;
		text-align: center;
		margin-bottom: 20rpx;
	}
	
	.report-title {
		font-size: 40rpx;
		font-weight: bold;
		margin-bottom: 10rpx;
		display: block;
	}
	
	.scene-name {
		font-size: 28rpx;
	}
	
	.report-content {
		flex: 1;
	}
	
	.score-section {
		background-color: #fff;
		border-radius: 12rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
	}
	
	.overall-score {
		text-align: center;
		margin-bottom: 30rpx;
	}
	
	.score-value {
		font-size: 80rpx;
		font-weight: bold;
		color: #10b981;
	}
	
	.score-label {
		font-size: 28rpx;
		color: #666;
		display: block;
	}
	
	.radar-chart {
		width: 90vw;
		height: 90vw;
		max-width: 700px;
		max-height: 700px;
		margin: 0 auto 30rpx auto;
		display: flex;
		justify-content: center;
		align-items: center;
	}
	
	.radar-canvas {
		width: 100%;
		height: 100%;
	}
	
	.dimension-scores {
		margin-top: 20rpx;
	}
	
	.dimension-item {
		margin-bottom: 15rpx;
	}
	
	.dimension-bar-wrapper {
		display: flex;
		align-items: center;
	}
	
	.dimension-name {
		width: 200rpx;
		font-size: 28rpx;
		color: #333;
	}
	
	.dimension-bar-container {
		flex: 1;
		height: 40rpx;
		background-color: #e0e0e0;
		border-radius: 20rpx;
		overflow: hidden;
	}
	
	.dimension-bar {
		height: 100%;
		background-color: #10b981;
		border-radius: 20rpx;
		display: flex;
		align-items: center;
		justify-content: flex-end;
		padding-right: 10rpx;
	}
	
	.dimension-score {
		color: #fff;
		font-size: 24rpx;
	}
	
	.analysis-section, .suggestion-section {
		background-color: #fff;
		border-radius: 12rpx;
		padding: 30rpx;
		margin-bottom: 20rpx;
	}
	
	.section-title {
		font-size: 32rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
		border-left: 6rpx solid #10b981;
		padding-left: 15rpx;
	}
	
	.analysis-item {
		margin-bottom: 30rpx;
		border-bottom: 1rpx solid #eee;
		padding-bottom: 20rpx;
	}
	
	.analysis-item:last-child {
		border-bottom: none;
		margin-bottom: 0;
		padding-bottom: 0;
	}
	
	.analysis-header { 
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 10rpx;
	}
	
	.analysis-title {
		font-size: 30rpx;
		font-weight: bold;
		color: #333;
	}
	
	.analysis-score {
		font-size: 30rpx;
		color: #10b981;
		font-weight: bold;
	}
	
	.analysis-content {
		font-size: 28rpx;
		color: #666;
		line-height: 1.5;
	}
	
	.suggestion-list {
		padding: 10rpx 0;
	}
	
	.suggestion-item {
		display: flex;
		margin-bottom: 20rpx;
	}
	
	.suggestion-icon {
		width: 50rpx;
		height: 50rpx;
		background-color: #10b981;
		color: #fff;
		border-radius: 25rpx;
		display: flex;
		justify-content: center;
		align-items: center;
		font-size: 28rpx;
		margin-right: 20rpx;
		flex-shrink: 0;
	}
	
	.suggestion-content {
		flex: 1;
		font-size: 28rpx;
		color: #666;
		line-height: 1.5;
	}
	
	.action-buttons {
		display: flex;
		justify-content: space-between;
		margin-top: 30rpx;
	}
	
	.share-btn, .back-btn {
		width: 48%;
		height: 80rpx;
		line-height: 80rpx;
		text-align: center;
		border-radius: 40rpx;
		font-size: 30rpx;
	}
	
	.share-btn {
		background-color: #10b981;
		color: #fff;
	}
	
	.back-btn {
		background-color: #f2f2f2;
		color: #333;
	}
</style> 