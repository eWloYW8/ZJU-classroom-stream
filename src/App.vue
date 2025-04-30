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
            {{ channel.name }}
          </li>
          <li v-if="loading" class="loading-text">Loading...</li>
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
import { ref, computed, onMounted } from 'vue';
import HLSPlayer from './components/HLSPlayer.vue';
import WebRTCPlayer from './components/WebRTCPlayer.vue';
import FLVPlayer from './components/FLVPlayer.vue';

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

    const filteredChannels = computed(() => {
      if (!searchQuery.value) return channels.value;
      const query = searchQuery.value.toLowerCase();
      return channels.value.filter(channel => 
        channel.name.toLowerCase().includes(query)
      );
    });

    const loadChannels = async () => {
      try {
        loading.value = true;

        // 加载基础频道数据
        const response = await fetch('/stream_db.json');
        let channelData = await response.json();

        // 对频道名称进行排序
        channelData = Object.keys(channelData)
          .sort()
          .reduce((sorted, key) => {
            sorted[key] = channelData[key];
            return sorted;
          }, {});

        // 尝试加载扩展数据
        try {
          const response_extended = await fetch("https://mcloudpush.cmc.zju.edu.cn:10443/streams");
          if (response_extended.ok) {
            const data = await response_extended.json();

            // 添加未在基础数据中的流
            data.streams.forEach(stream => {
              const streamKey = Object.keys(stream)[0];
              if (!Object.values(channelData).includes(streamKey)) {
                channelData[`Unknown: ${streamKey}`] = streamKey;
              }
            });
          } else {
            console.warn(`Extended fetch failed with status: ${response_extended.status}`);
          }
        } catch (error) {
          console.error('Error fetching extended data:', error);
        }

        // 转换数据格式
        channels.value = Object.entries(channelData).map(([name, id]) => ({ name, id }));

        loading.value = false;
      } catch (error) {
        console.error('Failed to load channels:', error);
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
      loadChannels();
    });

    return {
      channels,
      currentChannel,
      currentMode,
      searchQuery,
      loading,
      filteredChannels,
      selectChannel,
      switchMode,
      openRTMPStream
    };
  }
};
</script>

<style>
/* 样式将继承自 style.css */
</style> 