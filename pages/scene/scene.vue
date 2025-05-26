<template>
	<view class="container">
		<view class="scene-header">
			<image class="scene-image" :src="scene.icon"></image>
			<text class="scene-title">{{scene.name}}</text>
		</view>
		
		<view class="scene-content">
			<view class="section">
				<view class="section-title">场景介绍</view>
				<view class="section-content">
					<text>{{scene.description}}</text>
				</view>
			</view>
			
			<view class="section">
				<view class="section-title">学习目标</view>
				<view class="section-content">
					<text>{{scene.goal}}</text>
				</view>
			</view>
			
			<view class="section tips">
				<view class="section-title">练习提示</view>
				<view class="section-content">
					<text>1. 请确保在安静的环境中进行练习</text>
					<text>2. 语音交流时请使用清晰的普通话</text>
					<text>3. 练习过程中可随时点击"结束"按钮退出</text>
				</view>
			</view>
		</view>
		
		<view class="action-buttons">
			<button class="start-btn" @click="startPractice">开始练习</button>
			<button class="back-btn" @click="goBack">返回</button>
		</view>
	</view>
</template>

<script>
	import config from '@/config.js'
	
	export default {
		data() {
			return {
                apiBaseUrl: config.apiBaseUrl,
				sceneId: 0,
				scene: {
					id: 0,
					name: '',
					description: '',
					goal: '',
					icon: ''
				}
			}
		},
		onLoad(options) {
			// 获取场景ID
			if (options.id) {
				this.sceneId = parseInt(options.id);
				this.getSceneDetail();
			}
		},
		methods: {
			getSceneDetail() {
				// 从服务器获取场景详情
				// 这里使用模拟数据
				const scenes = [
                    {
                    	id: 0,
                    	name: '核苷酸产品介绍',
                    	description: '你是一位珍奥双迪的保健品销售，正在对保健品持怀疑态度且较为节俭的中老年客户，重点推广核苷酸产品',
                    	goal: '通过科学依据和产品优势打消客户疑虑，促使选择购买珍奥的核苷酸产品。',
                    	icon: this.apiBaseUrl+'/uploads/static/scene1.png'
                    },
					{
						id: 1,
						name: '新客户开发',
						description: '针对首次接触的潜在客户，学习如何有效地介绍产品和建立信任。本场景模拟与一位对产品完全陌生的客户进行初次沟通，你需要通过有效的自我介绍和产品展示，引起客户的兴趣。',
						goal: '学习如何快速建立与新客户的信任关系，引起客户对产品的兴趣，为后续的深入交流奠定基础。',
						icon: this.apiBaseUrl+'/uploads/static/scene1.png'
					},
					{
						id: 2,
						name: '异议处理',
						description: '学习如何面对客户提出的各种异议，并有效地进行回应。在销售过程中，客户常常会提出各种疑问和异议，本场景将帮助你学习如何处理这些问题，并将潜在的阻碍转化为销售机会。',
						goal: '掌握处理客户异议的技巧，将异议转化为销售机会，提高客户的购买意愿。',
						icon: this.apiBaseUrl+'/uploads/static/scene2.png'
					},
					{
						id: 3,
						name: '产品推荐',
						description: '根据客户需求，推荐最合适的产品，提高销售成功率。本场景模拟客户已经表明了自己的需求，你需要基于这些需求，向客户推荐最合适的产品。',
						goal: '学习如何精准分析客户需求，进行有针对性的产品推荐，提高客户满意度和购买几率。',
						icon: this.apiBaseUrl+'/uploads/static/scene3.png'
					},
					{
						id: 4,
						name: '成交技巧',
						description: '学习如何引导客户做出购买决定，顺利完成销售。本场景模拟客户已经对产品有较高兴趣，但尚未做出购买决定的情况，你需要运用成交技巧，促使客户完成购买。',
						goal: '掌握成交的时机把握和话术技巧，提高成交率，顺利完成销售过程。',
						icon: this.apiBaseUrl+'/uploads/static/scene4.png'
					}
				];
				
				const foundScene = scenes.find(item => item.id === this.sceneId);
				if (foundScene) {
					this.scene = foundScene;
				} else {
					uni.showToast({
						title: '场景不存在',
						icon: 'none'
					});
					setTimeout(() => {
						uni.navigateBack();
					}, 1500);
				}
				
				// 实际项目中应该使用API请求
				// uni.request({
				//   url: `http://your-api-url/scenes/${this.sceneId}`,
				//   success: (res) => {
				//     this.scene = res.data;
				//   },
				//   fail: () => {
				//     uni.showToast({
				//       title: '获取场景信息失败',
				//       icon: 'none'
				//     });
				//   }
				// });
			},
			startPractice() {
				// 跳转到聊天练习页面
				uni.navigateTo({
					url: `/pages/chat/chat?sceneId=${this.sceneId}`
				});
			},
			goBack() {
				uni.navigateBack();
			}
		}
	}
</script>

<style>
	.container {
		padding: 30rpx;
		display: flex;
		flex-direction: column;
		height: 100vh;
		box-sizing: border-box;
	}
	
	.scene-header {
		display: flex;
		flex-direction: column;
		align-items: center;
		margin-bottom: 40rpx;
		padding: 20rpx;
	}
	
	.scene-image {
		width: 150rpx;
		height: 150rpx;
		margin-bottom: 20rpx;
	}
	
	.scene-title {
		font-size: 40rpx;
		font-weight: bold;
	}
	
	.scene-content {
		flex: 1;
		background-color: #f8f8f8;
		border-radius: 12rpx;
		padding: 30rpx;
		margin-bottom: 30rpx;
		overflow-y: auto;
	}
	
	.section {
		margin-bottom: 30rpx;
	}
	
	.section-title {
		font-size: 32rpx;
		font-weight: bold;
		margin-bottom: 15rpx;
		color: #333;
	}
	
	.section-content {
		font-size: 28rpx;
		color: #666;
		line-height: 1.5;
	}
	
	.tips {
		background-color: rgba(255, 230, 230, 0.3);
		padding: 20rpx;
		border-radius: 8rpx;
		border-left: 6rpx solid #ff6666;
	}
	
	.tips .section-content text {
		display: block;
		margin-bottom: 10rpx;
	}
	
	.action-buttons {
		display: flex;
		justify-content: space-between;
	}
	
	.start-btn, .back-btn {
		width: 45%;
		height: 80rpx;
		line-height: 80rpx;
		text-align: center;
		border-radius: 40rpx;
		font-size: 30rpx;
	}
	
	.start-btn {
		background-color: #10b981;
		color: #fff;
	}
	
	.back-btn {
		background-color: #f2f2f2;
		color: #333;
	}
</style> 