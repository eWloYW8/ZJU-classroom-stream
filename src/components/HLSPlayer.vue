<template>
  <video ref="videoElement" autoplay playsinline webkit-playsinline controls></video>
</template>

<script>
import Hls from 'hls.js';

export default {
  name: 'HLSPlayer',
  props: {
    streamId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      hls: null,
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
    async cleanup() {
      if (this.retryTimeout) {
        clearTimeout(this.retryTimeout);
        this.retryTimeout = null;
      }
      await this.destroyPlayer();
    },
    async initPlayer() {
      try {
        await this.cleanup();
        
        if (Hls.isSupported()) {
          const video = this.$refs.videoElement;
          const url = `https://livepgc.cmc.zju.edu.cn/pgc/${this.streamId}.m3u8`;
          
          this.hls = new Hls();

          this.hls.loadSource(url);
          this.hls.attachMedia(video);

          this.hls.on(Hls.Events.MANIFEST_PARSED, () => {
            this.isPlaying = true;
            this.retryCount = 0;
            video.play().catch(error => {
              console.error('Failed to play video:', error);
              this.handlePlaybackError();
            });
          });

          this.hls.on(Hls.Events.ERROR, (event, data) => {
            if (data.fatal) {
              switch (data.type) {
                case Hls.ErrorTypes.NETWORK_ERROR:
                  console.error('Network error:', data);
                  this.handlePlaybackError();
                  break;
                case Hls.ErrorTypes.MEDIA_ERROR:
                  console.error('Media error:', data);
                  this.hls.recoverMediaError();
                  break;
                default:
                  console.error('Fatal error:', data);
                  this.handlePlaybackError();
                  break;
              }
            }
          });
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
          // 对于 Safari 浏览器
          video.src = `https://livepgc.cmc.zju.edu.cn/pgc/${this.streamId}.m3u8`;
          video.addEventListener('loadedmetadata', () => {
            this.isPlaying = true;
            this.retryCount = 0;
            video.play().catch(error => {
              console.error('Failed to play video:', error);
              this.handlePlaybackError();
            });
          });
        }
      } catch (error) {
        console.error('Failed to initialize player:', error);
        this.handlePlaybackError();
      }
    },
    async destroyPlayer() {
      if (this.hls) {
        try {
          // 先暂停视频元素
          if (this.$refs.videoElement) {
            this.$refs.videoElement.pause();
            this.$refs.videoElement.src = '';
          }
          
          // 销毁 HLS 实例
          this.hls.destroy();
          this.hls = null;
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
      if (!this.isPlaying) {
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

