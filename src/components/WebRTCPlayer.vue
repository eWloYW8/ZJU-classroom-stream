<template>
  <video ref="videoElement" autoplay playsinline webkit-playsinline controls></video>
</template>

<script>
import { JSWebrtc } from '../jswebrtc.min.js';

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
      player: null
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
      if (this.player) {
        this.player.destroy();
      }

      const url = `webrtc://mcloudpush.cmc.zju.edu.cn/live/${this.streamId}`;
      this.player = new JSWebrtc.Player(url, {
        video: this.$refs.videoElement,
        autoplay: true
      });
    },
    destroyPlayer() {
      if (this.player) {
        this.player.destroy();
        this.player = null;
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