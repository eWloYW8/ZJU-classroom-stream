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
      hls: null
    };
  },
  mounted() {
    this.initPlayer();
  },
  beforeUnmount() {
    this.destroyPlayer();
  },
  methods: {
    initPlayer() {
      if (this.hls) {
        this.hls.destroy();
        this.hls = null;
      }

      const streamUrl = `https://livepgc.cmc.zju.edu.cn/pgc/${this.streamId}.m3u8`;
      
      if (Hls.isSupported()) {
        this.hls = new Hls();
        this.hls.loadSource(streamUrl);
        this.hls.attachMedia(this.$refs.videoElement);
        this.hls.on(Hls.Events.MANIFEST_PARSED, () => {
          this.$refs.videoElement.play();
        });
      } else if (this.$refs.videoElement.canPlayType('application/vnd.apple.mpegurl')) {
        this.$refs.videoElement.src = streamUrl;
        this.$refs.videoElement.addEventListener('loadedmetadata', () => {
          this.$refs.videoElement.play();
        });
      }
    },
    destroyPlayer() {
      if (this.hls) {
        this.hls.destroy();
        this.hls = null;
      }
    }
  },
  watch: {
    streamId() {
      this.initPlayer();
    }
  }
};
</script> 