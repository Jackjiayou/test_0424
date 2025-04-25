<template>
	<view class="container">
		<!-- 员工信息区域 -->
		<view class="user-profile">
			<image class="avatar" :src="userInfo.avatar"></image>
			<view class="user-info">
				<text class="username">{{userInfo.name}}</text>
				<text class="practice-count">练习次数: {{userInfo.practiceCount}}</text>
			</view>
		</view>
		
		<!-- 主菜单 -->
		<view class="main-menu">
			<view class="menu-title">练习场景</view>
			<view class="scenes-list">
				<view 
					v-for="(scene, index) in scenes" 
					:key="index" 
					class="scene-item"
					@click="goToScene(scene)">
					<image class="scene-icon" :src="scene.icon"></image>
					<text class="scene-name">{{scene.name}}</text>
				</view>
			</view>
		</view>
		
		<!-- 底部选项卡 -->
		<view class="tab-bar">
			<view class="tab-item active">
				<text class="tab-text">练习场景</text>
			</view>
			<view class="tab-item" @click="goToRanking">
				<text class="tab-text">排行榜</text>
			</view>
			<view class="tab-item" @click="goToRecords">
				<text class="tab-text">练习记录</text>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				userInfo: {
					avatar: '/static/avatar.png',
					name: '张三',
					practiceCount: 12
				},
				scenes: [
					{
						id: 1,
						name: '新客户开发',
						description: '针对首次接触的潜在客户，学习如何有效地介绍产品和建立信任',
						goal: '学习如何快速建立与新客户的信任关系，引起客户对产品的兴趣',
						icon: '/static/scene1.png'
					},
					{
						id: 2,
						name: '异议处理',
						description: '学习如何面对客户提出的各种异议，并有效地进行回应',
						goal: '掌握处理客户异议的技巧，将异议转化为销售机会',
						icon: '/static/scene2.png'
					},
					{
						id: 3,
						name: '产品推荐',
						description: '根据客户需求，推荐最合适的产品，提高销售成功率',
						goal: '学习如何精准分析客户需求，进行有针对性的产品推荐',
						icon: '/static/scene3.png'
					},
					{
						id: 4,
						name: '成交技巧',
						description: '学习如何引导客户做出购买决定，顺利完成销售',
						goal: '掌握成交的时机把握和话术技巧，提高成交率',
						icon: '/static/scene4.png'
					}
				]
			}
		},
		onLoad() {
			// 加载用户信息和场景数据
			this.getUserInfo();
			this.getScenes();
		},
		methods: {
			getUserInfo() {
				// 从服务器获取用户信息
				// 这里使用模拟数据
				// uni.request({
				//   url: 'http://your-api-url/user',
				//   success: (res) => {
				//     this.userInfo = res.data;
				//   }
				// });
			},
			getScenes() {
				// 从服务器获取场景数据
				// 这里使用模拟数据
				// uni.request({
				//   url: 'http://your-api-url/scenes',
				//   success: (res) => {
				//     this.scenes = res.data;
				//   }
				// });
			},
			goToScene(scene) {
				// 跳转到场景详情页
				uni.navigateTo({
					url: `/pages/scene/scene?id=${scene.id}`
				});
			},
			goToRanking() {
				// 跳转到排行榜页面
				uni.showToast({
					title: '排行榜功能开发中',
					icon: 'none'
				});
			},
			goToRecords() {
				// 跳转到练习记录页面
				uni.showToast({
					title: '练习记录功能开发中',
					icon: 'none'
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
		height: 100vh;
		box-sizing: border-box;
	}
	
	.user-profile {
		display: flex;
		align-items: center;
		padding: 20rpx;
		background-color: #f8f8f8;
		border-radius: 12rpx;
		margin-bottom: 30rpx;
	}
	
	.avatar {
		width: 120rpx;
		height: 120rpx;
		border-radius: 60rpx;
		margin-right: 20rpx;
	}
	
	.user-info {
		display: flex;
		flex-direction: column;
	}
	
	.username {
		font-size: 36rpx;
		font-weight: bold;
		margin-bottom: 10rpx;
	}
	
	.practice-count {
		font-size: 28rpx;
		color: #666;
	}
	
	.main-menu {
		flex: 1;
		overflow: hidden;
	}
	
	.menu-title {
		font-size: 32rpx;
		font-weight: bold;
		margin-bottom: 20rpx;
	}
	
	.scenes-list {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
	}
	
	.scene-item {
		width: 48%;
		background-color: #ffffff;
		border-radius: 12rpx;
		padding: 20rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.1);
		display: flex;
		flex-direction: column;
		align-items: center;
	}
	
	.scene-icon {
		width: 100rpx;
		height: 100rpx;
		margin-bottom: 10rpx;
	}
	
	.scene-name {
		font-size: 28rpx;
		text-align: center;
	}
	
	.tab-bar {
		display: flex;
		height: 100rpx;
		border-top: 1rpx solid #eee;
		background-color: #fff;
	}
	
	.tab-item {
		flex: 1;
		display: flex;
		justify-content: center;
		align-items: center;
	}
	
	.active {
		color: #007AFF;
		border-top: 4rpx solid #007AFF;
	}
	
	.tab-text {
		font-size: 28rpx;
	}
</style>
