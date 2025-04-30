<template>
  <video ref="videoElement" autoplay playsinline webkit-playsinline controls></video>
</template>

<script>
export default {
  name: 'WebRTCPlayer',
  props: {
    streamId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      player: null,
      isPlaying: false,
      retryCount: 0,
      maxRetries: 3,
      retryTimeout: null
    };
  },
  mounted() {
    this.initPlayer();
  },
  beforeUnmount() {
    this.cleanup();
  },
  methods: {
    cleanup() {
      if (this.retryTimeout) {
        clearTimeout(this.retryTimeout);
        this.retryTimeout = null;
      }
      this.destroyPlayer();
    },
    async initPlayer() {
      try {
        this.cleanup();
        
        const url = `webrtc://mcloudpush.cmc.zju.edu.cn/live/${this.streamId}`;
        this.player = new JSWebrtc.Player(url, {
          video: this.$refs.videoElement,
          autoplay: true,
          onPlay: () => {
            this.isPlaying = true;
            this.retryCount = 0;
          },
          onPause: () => {
            this.isPlaying = false;
          },
          onError: (player, error) => {
            console.error('WebRTC player error:', error);
            this.handlePlaybackError();
          }
        });
      } catch (error) {
        console.error('Failed to initialize player:', error);
        this.handlePlaybackError();
      }
    },
    destroyPlayer() {
      if (this.player) {
        try {
          // 先暂停视频元素
          if (this.$refs.videoElement) {
            this.$refs.videoElement.pause();
            this.$refs.videoElement.srcObject = null;
          }
          
          // 停止并销毁播放器
          this.player.stop();
          this.player.destroy();
          this.player = null;
          this.isPlaying = false;
        } catch (error) {
          console.error('Error destroying player:', error);
        }
      }
    },
    handlePlaybackError() {
      this.isPlaying = false;
      
      if (this.retryCount < this.maxRetries) {
        this.retryCount++;
        console.log(`Retrying playback (attempt ${this.retryCount}/${this.maxRetries})`);
        
        // 使用指数退避策略进行重试
        const delay = Math.min(1000 * Math.pow(2, this.retryCount), 10000);
        this.retryTimeout = setTimeout(() => {
          this.initPlayer();
        }, delay);
      } else {
        console.error('Max retry attempts reached');
      }
    },
    handleError(event) {
      console.error('Video element error:', event);
      this.handlePlaybackError();
    },
    handleLoadedMetadata() {
      // 确保视频元素准备好后再尝试播放
      if (this.player && !this.isPlaying) {
        this.$refs.videoElement.play().catch(error => {
          console.error('Failed to play video:', error);
          this.handlePlaybackError();
        });
      }
    }
  },
  watch: {
    streamId: {
      handler() {
        this.retryCount = 0;
        this.initPlayer();
      },
      immediate: true
    }
  }
};
</script>
