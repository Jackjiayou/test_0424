<template>
	<view class="container">
		<!-- 视频播放区域 -->
		<view class="video-container">
			<video 
				class="video-player" 
				:src="videoUrl" 
				autoplay 
				loop
				:controls="false"
				object-fit="contain"
				:style="{ width: '100%', height: '100%' }"
				@error="handleVideoError"
				@loadstart="handleVideoLoadStart"
				@loadeddata="handleVideoLoaded"
				@ended="handleVideoEnded"
			></video>
		</view>
		
		<!-- 聊天区域 -->
		<view class="chat-container">
			<scroll-view 
				class="chat-list" 
				scroll-y 
				:scroll-top="scrollTop"
				@scrolltoupper="loadMoreMessages"
			>
				<view v-for="(msg, index) in messages" :key="index" class="message-item" :class="msg.type">
					<view class="message-content">{{msg.content}}</view>
				</view>
			</scroll-view>
			
			<!-- 输入区域 -->
			<view class="input-area">
				<input 
					class="input-box" 
					v-model="inputMessage" 
					placeholder="请输入您的问题" 
					@confirm="sendMessage"
				/>
				<button class="send-btn" @click="sendMessage">发送</button>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				apiBaseUrl: 'http://localhost:8000',
				//apiBaseUrl: 'https://ai.dl-dd.com',
				videoUrl: '', // 默认视频
				messages: [
					{
						type: 'assistant',
						content: '你好，我是珍迪助手，可以问我健康养生相关问题。'
					}
				], // 聊天记录
				inputMessage: '', // 输入框内容
				scrollTop: 0, // 滚动位置
				isVideoLoading: false, // 视频加载状态
				pendingVideoUrl: '', // 待播放的新视频URL
			}
		},
		onLoad() {
			// 设置初始视频
			this.videoUrl = this.apiBaseUrl + '/uploads/download/tp3.mp4';
		},
		methods: {
			// 获取随机默认视频
			getRandomDefaultVideo() {
				const videos = ['tp1.mp4', 'tp2.mp4', 'tp3.mp4'];
				const randomIndex = Math.floor(Math.random() * videos.length);
				return this.apiBaseUrl + '/uploads/download/' + videos[randomIndex];
			},
			
			// 处理视频错误
			handleVideoError(e) {
				console.error('视频加载错误:', e);
				// 如果是默认视频加载失败，尝试加载备用视频
				if (this.videoUrl.includes('hi.mp4')) {
					console.log('hi.mp4加载失败，切换到tp1.mp4');
					this.videoUrl = this.apiBaseUrl + '/uploads/download/tp1.mp4';
				}
				uni.showToast({
					title: '视频加载失败',
					icon: 'none'
				});
			},
			
			// 视频开始加载
			handleVideoLoadStart() {
				this.isVideoLoading = true;
			},
			
			// 视频加载完成
			handleVideoLoaded() {
				this.isVideoLoading = false;
			},
			
			// 处理视频播放结束
			async handleVideoEnded() {
				console.log('视频播放结束，当前视频:', this.videoUrl);
				console.log('待播放视频:', this.pendingVideoUrl);
				
				if (this.pendingVideoUrl) {
					console.log('切换到新视频:', this.pendingVideoUrl);
					this.videoUrl = this.pendingVideoUrl;
					this.pendingVideoUrl = '';
				} else {
					// 任何视频播放结束后，如果没有待播放视频，就切换到随机默认视频
					const defaultVideo = this.getRandomDefaultVideo();
					console.log('视频播放结束，切换到随机默认视频:', defaultVideo);
					this.videoUrl = defaultVideo;
				}
			},
			
			// 发送消息
			async sendMessage() {
				if (!this.inputMessage.trim()) return;
				
				// 添加用户消息
				this.messages.push({
					type: 'user',
					content: this.inputMessage
				});
				
				// 清空输入框
				const userMessage = this.inputMessage;
				this.inputMessage = '';
				
				// 滚动到底部
				this.scrollToBottom();
				
				try {
					// 调用后端接口合成视频
					const res = await uni.request({
						url: this.apiBaseUrl + '/synthesize',
						method: 'POST',
						data: {
							text: userMessage,
							messages: JSON.stringify(this.messages)
						},
						header: {
							'content-type': 'application/x-www-form-urlencoded'
						},
						timeout: 180000  // 设置超时时间为3分钟
					});
					
					if (res.data && res.data.videoUrl) {
						// 保存新的视频URL，等待当前视频播放完成后更新
						const newVideoUrl = res.data.videoUrl;
						console.log('新视频URL:', newVideoUrl);
						
						// 检查视频URL是否可访问
						try {
							const checkRes = await uni.request({
								url: newVideoUrl,
								method: 'HEAD'
							});
							
							if (checkRes.statusCode === 200) {
								this.pendingVideoUrl = newVideoUrl;
							} else {
								throw new Error('视频文件不可访问');
							}
						} catch (error) {
							console.error('视频URL检查失败:', error);
							uni.showToast({
								title: '视频文件不可访问',
								icon: 'none'
							});
							// 使用随机默认视频
							this.pendingVideoUrl = this.getRandomDefaultVideo();
							return;
						}
						
						// 添加机器人回复
						this.messages.push({
							type: 'assistant',
							content: res.data.text || '已为您生成视频回复'
						});
					} else {
						// 如果没有返回视频URL，使用随机默认视频
						console.log('没有返回视频URL，使用随机默认视频');
						this.pendingVideoUrl = this.getRandomDefaultVideo();
					}
				} catch (error) {
					console.error('发送消息失败:', error);
					uni.showToast({
						title: '发送失败，请重试',
						icon: 'none'
					});
					// 发生错误时使用随机默认视频
					console.log('发生错误，使用随机默认视频');
					this.pendingVideoUrl = this.getRandomDefaultVideo();
				}
				
				// 滚动到底部
				this.scrollToBottom();
			},
			
			// 滚动到底部
			scrollToBottom() {
				setTimeout(() => {
					this.scrollTop = 9999999;
				}, 100);
			},
			
			// 加载更多消息
			loadMoreMessages() {
				// TODO: 实现加载历史消息
			}
		}
	}
</script>

<style>
	.container {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background: #f5f5f5;
	}
	
	.video-container {
		width: 100%;
		height: 0;
		padding-bottom: 133.33%; /* 4:3 比例的反转，即 3:4 */
		background: #000;
		position: relative;
	}
	
	.video-player {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		object-fit: contain;
	}
	
	.chat-container {
		flex: 1;
		display: flex;
		flex-direction: column;
		background: #fff;
	}
	
	.chat-list {
		flex: 1;
		padding: 20rpx;
	}
	
	.message-item {
		margin-bottom: 20rpx;
		display: flex;
	}
	
	.message-item.user {
		justify-content: flex-end;
	}
	
	.message-content {
		max-width: 70%;
		padding: 20rpx;
		border-radius: 10rpx;
		font-size: 28rpx;
		word-break: break-all;
	}
	
	.user .message-content {
		background: #007AFF;
		color: #fff;
	}
	
	.bot .message-content {
		background: #f0f0f0;
		color: #333;
	}
	
	.input-area {
		padding: 20rpx;
		background: #fff;
		border-top: 1rpx solid #eee;
		display: flex;
		align-items: center;
	}
	
	.input-box {
		flex: 1;
		height: 72rpx;
		background: #f5f5f5;
		border-radius: 36rpx;
		padding: 0 30rpx;
		font-size: 28rpx;
	}
	
	.send-btn {
		margin-left: 20rpx;
		height: 72rpx;
		line-height: 72rpx;
		padding: 0 30rpx;
		background: #1AAD19;
		color: #fff;
		border-radius: 36rpx;
		font-size: 28rpx;
	}
</style> 