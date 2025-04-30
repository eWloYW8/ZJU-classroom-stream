<template>
    <video ref="videoElement" autoplay playsinline webkit-playsinline controls></video>
  </template>
  
  <script>
  import flvjs from 'flv.js';
  
  export default {
    name: 'FLVPlayer',
    props: {
      streamId: {
        type: String,
        required: true
      }
    },
    data() {
      return {
        flvPlayer: null,
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
      buildStreamUrl() {
        return `http://livepgc.cmc.zju.edu.cn/pgc/${this.streamId}.flv`;
      },
      async initPlayer() {
        try {
          this.cleanup();
          
          if (flvjs.isSupported()) {
            const video = this.$refs.videoElement;
            const url = this.buildStreamUrl();
            
            this.flvPlayer = flvjs.createPlayer({
              type: "flv",
              isLive: true,
              url: url
            });
  
            this.flvPlayer.attachMediaElement(video);
            this.flvPlayer.load();
  
            // 监听媒体数据加载完成事件
            this.flvPlayer.on(flvjs.Events.METADATA_ARRIVED, () => {
              this.isPlaying = true;
              this.retryCount = 0;
            });
  
            // 处理播放错误
            this.flvPlayer.on(flvjs.Events.ERROR, (errType, errDetail) => {
              console.error('FLV error:', errType, errDetail);
              this.handlePlaybackError();
            });
  
            // 尝试自动播放
            video.play().catch(error => {
              console.error('Autoplay failed:', error);
              this.handlePlaybackError();
            });
  
          } else {
            console.error('FLV is not supported');
            this.handlePlaybackError();
          }
        } catch (error) {
          console.error('Player init failed:', error);
          this.handlePlaybackError();
        }
      },
      destroyPlayer() {
        if (this.flvPlayer) {
          try {
            this.flvPlayer.pause();
            this.flvPlayer.unload();
            this.flvPlayer.detachMediaElement();
            this.flvPlayer.destroy();
            this.flvPlayer = null;
            this.isPlaying = false;
          } catch (error) {
            console.error('Destroy player failed:', error);
          }
        }
      },
      handlePlaybackError() {
        this.isPlaying = false;
        
        if (this.retryCount < this.maxRetries) {
          this.retryCount++;
          console.log(`Retrying... (${this.retryCount}/${this.maxRetries})`);
          
          const delay = Math.min(2000 * this.retryCount, 10000);
          this.retryTimeout = setTimeout(this.initPlayer, delay);
        } else {
          console.error('Maximum retries reached');
          this.$emit('error', '播放失败，请检查流地址或网络连接');
        }
      }
    },
    watch: {
      streamId() {
        this.retryCount = 0;
        this.initPlayer();
      },
      streamType() {
        this.retryCount = 0;
        this.initPlayer();
      }
    }
  };
  </script>