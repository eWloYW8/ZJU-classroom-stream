<template>
  <div class="app">
    <div class="header">
      <h1>ZJU Classroom Stream</h1>
      <a href="https://github.com/eWloYW8/ZJU-classroom-stream" class="github-corner" target="_blank" rel="noopener noreferrer">
        <i class="fab fa-github github-icon"></i>
        <span class="github-text">eWloYW8/ZJU-classroom-stream</span>
      </a>
    </div>

    <div class="container">
      <div class="sidebar">
        <div class="search-box">
          <i class="fas fa-search search-icon"></i>
          <input type="text" class="search-input" placeholder="Type Classroom" v-model="searchQuery" />
        </div>
        <ul class="channel-list">
          <li v-for="channel in filteredChannels" :key="channel.id" 
              :class="['channel-item', { active: currentChannel === channel.id }]"
              @click="selectChannel(channel)">
            <span class="channel-name">{{ channel.name }}</span>
            <button :class="['pin-btn', { pinned: isPinned(channel.name) }]"
                    @click.stop="togglePin(channel.name)"
                    title="置顶/取消置顶">
              <i class="fas fa-thumbtack"></i>
            </button>
          </li>
          <li v-if="loading" class="loading-text">Loading...</li>
          <li v-if="errorMessage" class="error-text">{{ errorMessage }}</li>
        </ul>
      </div>

      <div class="video-container">
        <div class="mode-toggle">
          <span>播放方式：</span>
          <div class="mode-buttons">
            <button :class="['mode-btn', { active: currentMode === 'hls' }]" 
                    @click="switchMode('hls')" title="HLS 播放">
              📺 HLS
            </button>
            <button :class="['mode-btn', { active: currentMode === 'flv' }]" 
                    @click="switchMode('flv')" title="FLV 播放">
              📺 FLV
            </button>
            <button :class="['mode-btn']" 
                    @click="openRTMPStream" title="RTMP 播放">
              📺 RTMP
            </button>
            <button :class="['mode-btn', { active: currentMode === 'webrtc' }]" 
                    @click="switchMode('webrtc')" title="WebRTC 播放">
              🔴 WebRTC
            </button>
          </div>
        </div>
        
        <div class="play-hint">
          <i class="fas fa-circle-info"></i>
          同一教室可能只有一种播放方式可用，无法播放时请手动切换播放方式。
        </div>

        <HLSPlayer v-if="currentMode === 'hls' && currentChannel" :streamId="currentChannel" />
        <FLVPlayer v-else-if="currentMode === 'flv' && currentChannel" :streamId="currentChannel" />
        <WebRTCPlayer v-else-if="currentMode === 'webrtc' && currentChannel" :streamId="currentChannel" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import HLSPlayer from './components/HLSPlayer.vue';
import WebRTCPlayer from './components/WebRTCPlayer.vue';
import FLVPlayer from './components/FLVPlayer.vue';
import CryptoJS from 'crypto-js';

const STORAGE_KEY = 'zju_pinned_channels';

export default {
  name: 'App',
  components: {
    HLSPlayer,
    WebRTCPlayer,
    FLVPlayer
  },
  setup() {
    const channels = ref([]);
    const currentChannel = ref(null);
    const currentMode = ref('hls');
    const searchQuery = ref('');
    const loading = ref(true);
    const pinnedChannels = ref([]);
    const errorMessage = ref(null);

    // 检查频道是否已置顶
    const isPinned = (channelName) => pinnedChannels.value.includes(channelName);

    // 切换置顶状态
    const togglePin = (channelName) => {
      const index = pinnedChannels.value.indexOf(channelName);
      if (index > -1) {
        // 已置顶，取消
        pinnedChannels.value.splice(index, 1);
      } else {
        // 未置顶，添加
        pinnedChannels.value.push(channelName);
      }
    };

    // 过滤和排序频道列表
    const filteredChannels = computed(() => {
      const query = searchQuery.value.toLowerCase();
      const filtered = channels.value.filter(channel => 
        channel.name.toLowerCase().includes(query)
      );

      // 排序：置顶的在前，非置顶的在后
      // 在置顶/非置顶内部，保持原有的字母顺序
      return filtered.sort((a, b) => {
        const isAPinned = isPinned(a.name);
        const isBPinned = isPinned(b.name);

        if (isAPinned && !isBPinned) {
          return -1; // a (pinned) comes before b (unpinned)
        }
        if (!isAPinned && isBPinned) {
          return 1; // b (pinned) comes before a (unpinned)
        }
        // 如果两者置顶状态相同，保持原有的字母顺序
        // (channels.value 已经预先排序)
        return 0;
      });
    });

    const loadChannels = async () => {
      try {
        loading.value = true;
        errorMessage.value = null;

        let password;
        try {
          const keyResponse = await fetch('https://file.cc98.org/v4-upload/d/2025/1024/4f1xlql3.dat');
          if (!keyResponse.ok) {
            throw new Error(`HTTP error ${keyResponse.status}`);
          }
          password = await keyResponse.text();
        } catch (keyError) {
          console.error('Key fetch failed:', keyError);
          throw new Error('KEY_FETCH_FAILED');
        }

        const dataResponse = await fetch('/stream_db.enc');
        if (!dataResponse.ok) throw new Error(`Failed to fetch data (status: ${dataResponse.status})`);
        const encryptedBase64 = await dataResponse.text();

        const key = CryptoJS.SHA256(password);
        
        const encryptedData = CryptoJS.enc.Base64.parse(encryptedBase64);
        
        const iv = CryptoJS.lib.WordArray.create(encryptedData.words.slice(0, 4), 16);
        const ciphertext = CryptoJS.lib.WordArray.create(encryptedData.words.slice(4), encryptedData.sigBytes - 16);

        const decrypted = CryptoJS.AES.decrypt(
          { ciphertext: ciphertext },
          key,
          {
            iv: iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
          }
        );

        const decryptedText = decrypted.toString(CryptoJS.enc.Utf8);
        if (!decryptedText) {
          throw new Error('Decryption failed. Check key or data integrity.');
        }

        let channelData = JSON.parse(decryptedText);

        channelData = Object.keys(channelData)
          .sort()
          .reduce((sorted, key) => {
            sorted[key] = channelData[key];
            return sorted;
          }, {});

        channels.value = Object.entries(channelData).map(([name, id]) => ({ name, id }));

        loading.value = false;
      } catch (error) {
        console.error('Failed to load channels:', error);
        if (error.message === 'KEY_FETCH_FAILED') {
          errorMessage.value = '不在校园网环境下';
        } else {
          errorMessage.value = '加载失败，请稍后重试。';
        }
        loading.value = false;
      }
    };

    const selectChannel = (channel) => {
      currentChannel.value = channel.id;
    };

    const switchMode = (mode) => {
      currentMode.value = mode;
    };

    const openRTMPStream = () => {
      if (currentChannel.value) {
        window.open(`rtmp://livepgc.cmc.zju.edu.cn/pgc/${currentChannel.value}`);
      } else {
        console.warn('No channel selected for RTMP playback.');
      }
    };

    onMounted(() => {
      // 从 localStorage 加载置顶列表
      const storedPins = localStorage.getItem(STORAGE_KEY);
      if (storedPins) {
        try {
          pinnedChannels.value = JSON.parse(storedPins);
        } catch (e) {
          console.error('Failed to parse pinned channels:', e);
          localStorage.removeItem(STORAGE_KEY);
        }
      }
      loadChannels();
    });

    // 监听置顶列表的变化，并保存到 localStorage
    watch(pinnedChannels, (newPins) => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newPins));
    }, { deep: true });

    return {
      channels,
      currentChannel,
      currentMode,
      searchQuery,
      loading,
      filteredChannels,
      selectChannel,
      switchMode,
      openRTMPStream,
      isPinned,
      togglePin,
      errorMessage
    };
  }
};
</script>

<style>
/* 样式将继承自 style.css */
</style>