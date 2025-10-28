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
        
        <div class="top-controls-wrapper">
          
          <div class="mode-toggle control-card">
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
          
          <div class="recording-controls control-card">
            <button @click="toggleRecording" 
                    :class="['record-btn', { 'is-recording': isRecording }]"
                    :disabled="!currentChannel || (currentMode !== 'hls' && currentMode !== 'flv')">
              <i :class="['fas', isRecording ? 'fa-stop' : 'fa-circle']"></i>
              {{ isRecording ? '停止截取' : '开始截取' }}
            </button>
            <div v-if="isRecording" class="recording-status">
              <span>正在截取 ({{ currentRecordingMode.toUpperCase() }})</span>
              <span>大小: <strong>{{ (recordingFileSize / 1024 / 1024).toFixed(2) }} MB</strong></span>
              <span>时长: <strong>{{ recordingDuration }}</strong></span>
            </div>
            <div v-else class="record-hint">
              <i class="fas fa-info-circle"></i>
              请选择 HLS 或 FLV 模式以开始截取。
            </div>
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
// [Script 部分与您提供的代码完全相同，保持不变]
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
    const currentClassroomName = ref(null);
    const currentMode = ref('hls');
    const searchQuery = ref('');
    const loading = ref(true);
    const pinnedChannels = ref([]);
    const errorMessage = ref(null);

    const isRecording = ref(false);
    const recordingStartTime = ref(null);
    const recordingDuration = ref('00:00:00');
    const recordingFileSize = ref(0);
    const recordingChunks = ref([]);
    const recordingTimer = ref(null);
    const abortController = ref(null);
    const currentRecordingMode = ref(null);
    const hlsSegmentUrls = ref(new Set()); // 存储已下载的HLS分片
    const hlsPoller = ref(null); // HLS 轮询器

    const isPinned = (channelName) => pinnedChannels.value.includes(channelName);

    const togglePin = (channelName) => {
      const index = pinnedChannels.value.indexOf(channelName);
      if (index > -1) {
        pinnedChannels.value.splice(index, 1);
      } else {
        pinnedChannels.value.push(channelName);
      }
    };

    const filteredChannels = computed(() => {
      const query = searchQuery.value.toLowerCase();
      const filtered = channels.value.filter(channel => 
        channel.name.toLowerCase().includes(query)
      );

      return filtered.sort((a, b) => {
        const isAPinned = isPinned(a.name);
        const isBPinned = isPinned(b.name);
        if (isAPinned && !isBPinned) return -1;
        if (!isAPinned && isBPinned) return 1;
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
          if (!keyResponse.ok) throw new Error(`HTTP error ${keyResponse.status}`);
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
          { ciphertext: ciphertext }, key,
          { iv: iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }
        );

        const decryptedText = decrypted.toString(CryptoJS.enc.Utf8);
        if (!decryptedText) {
          throw new Error('Decryption failed.');
        }

        let channelData = JSON.parse(decryptedText);
        channelData = Object.keys(channelData).sort().reduce((sorted, key) => {
          sorted[key] = channelData[key];
          return sorted;
        }, {});

        channels.value = Object.entries(channelData).map(([name, id]) => ({ name, id }));
        loading.value = false;
      } catch (error) {
        console.error('Failed to load channels:', error);
        errorMessage.value = error.message === 'KEY_FETCH_FAILED' ? '不在校园网环境下' : '加载失败，请稍后重试。';
        loading.value = false;
      }
    };

    const selectChannel = (channel) => {
      if (isRecording.value) {
        alert('请先停止当前的截取任务！');
        return;
      }
      currentChannel.value = channel.id;
      currentClassroomName.value = channel.name;
    };

    const switchMode = (mode) => {
      if (isRecording.value) {
        alert('请先停止当前的截取任务！');
        return;
      }
      currentMode.value = mode;
    };

    const openRTMPStream = () => {
      if (currentChannel.value) {
        window.open(`rtmp://livepgc.cmc.zju.edu.cn/pgc/${currentChannel.value}`);
      }
    };

    const formatDate = (date) => {
      return date.getFullYear().toString() +
        (date.getMonth() + 1).toString().padStart(2, '0') +
        date.getDate().toString().padStart(2, '0') +
        date.getHours().toString().padStart(2, '0') +
        date.getMinutes().toString().padStart(2, '0') +
        date.getSeconds().toString().padStart(2, '0');
    };

    const getFileName = (name, start, end, ext) => {
      const startStr = formatDate(start);
      const endStr = formatDate(end);
      const saneName = name.replace(/[^a-zA-Z0-9\u4e00-\u9fa5_-]/g, '_');
      return `${saneName}_${startStr}_${endStr}.${ext}`;
    };

    const updateDuration = () => {
      const now = Date.now();
      const durationMs = now - recordingStartTime.value.getTime();
      const seconds = Math.floor((durationMs / 1000) % 60).toString().padStart(2, '0');
      const minutes = Math.floor((durationMs / (1000 * 60)) % 60).toString().padStart(2, '0');
      const hours = Math.floor(durationMs / (1000 * 60 * 60)).toString().padStart(2, '0');
      recordingDuration.value = `${hours}:${minutes}:${seconds}`;
    };

    const startHLSRecording = () => {
      abortController.value = new AbortController();
      hlsSegmentUrls.value.clear();
      pollHLSPlaylist();
    };

    const pollHLSPlaylist = async () => {
      if (!isRecording.value) return;

      const hlsBaseUrl = `https://livepgc.cmc.zju.edu.cn/pgc/${currentChannel.value}.m3u8`;
      const hlsSegmentBase = `https://livepgc.cmc.zju.edu.cn/pgc/`;

      try {
        const response = await fetch(hlsBaseUrl, { 
          signal: abortController.value.signal, 
          cache: 'no-store' 
        });
        if (!response.ok) throw new Error('Playlist fetch error');
        
        const playlistText = await response.text();
        const lines = playlistText.split('\n');
        const segmentUrls = lines.filter(line => line.endsWith('.ts'));

        for (const url of segmentUrls) {
          if (!isRecording.value) break;
          if (!hlsSegmentUrls.value.has(url)) {
            await fetchHLSSegment(hlsSegmentBase + url, url);
          }
        }

        if (isRecording.value) {
          hlsPoller.value = setTimeout(pollHLSPlaylist, 2000);
        }
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('HLS playlist poll error:', error);
          if (isRecording.value) {
            hlsPoller.value = setTimeout(pollHLSPlaylist, 5000);
          }
        }
      }
    };

    const fetchHLSSegment = async (fullUrl, segmentName) => {
      try {
        hlsSegmentUrls.value.add(segmentName);
        const response = await fetch(fullUrl, { signal: abortController.value.signal });
        if (!response.ok) throw new Error(`Segment fetch error: ${response.statusText}`);
        
        const data = await response.arrayBuffer();
        const chunk = new Uint8Array(data);
        
        recordingChunks.value.push(chunk);
        recordingFileSize.value += chunk.length;
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.warn('Failed to fetch HLS segment:', fullUrl, error);
          hlsSegmentUrls.value.delete(segmentName);
        }
      }
    };

    const startFLVRecording = async () => {
      try {
        abortController.value = new AbortController();
        const flvUrl = `https://livepgc.cmc.zju.edu.cn/pgc/${currentChannel.value}.flv`;
        const response = await fetch(flvUrl, { signal: abortController.value.signal });

        if (!response.ok) throw new Error(`Fetch error: ${response.statusText}`);
        const reader = response.body.getReader();

        while (isRecording.value) {
          const { done, value } = await reader.read();
          if (done) break;
          
          recordingChunks.value.push(value);
          recordingFileSize.value += value.length;
        }

        reader.releaseLock();
      } catch (error) {
        if (error.name === 'AbortError') {
          console.log('FLV recording aborted by user.');
        } else {
          console.error('FLV recording error:', error);
          alert('FLV 截取失败: ' + error.message);
          stopRecording(true);
        }
      }
    };

    const startRecording = () => {
      if (!currentChannel.value || (currentMode.value !== 'hls' && currentMode.value !== 'flv')) {
        alert('请先选择一个教室，并确保播放模式为 HLS 或 FLV。');
        return;
      }

      isRecording.value = true;
      currentRecordingMode.value = currentMode.value;
      recordingStartTime.value = new Date();
      recordingFileSize.value = 0;
      recordingDuration.value = '00:00:00';
      recordingChunks.value = [];
      
      recordingTimer.value = setInterval(updateDuration, 1000);

      if (currentRecordingMode.value === 'flv') {
        startFLVRecording();
      } else if (currentRecordingMode.value === 'hls') {
        startHLSRecording();
      }
    };

    const stopRecording = (failed = false) => {
      if (!isRecording.value) return;
      isRecording.value = false;
      const endTime = new Date();
      
      if (recordingTimer.value) clearInterval(recordingTimer.value);
      if (hlsPoller.value) clearTimeout(hlsPoller.value);
      
      if (abortController.value) {
        abortController.value.abort();
        abortController.value = null;
      }

      if (failed || recordingChunks.value.length === 0) {
        console.log('Recording stopped. No data to save.');
        recordingChunks.value = [];
        return;
      }

      const ext = currentRecordingMode.value === 'flv' ? 'flv' : 'ts';
      const mimeType = currentRecordingMode.value === 'flv' ? 'video/x-flv' : 'video/mp2t';
      
      const fileName = getFileName(
        currentClassroomName.value || 'classroom',
        recordingStartTime.value,
        endTime,
        ext
      );

      const blob = new Blob(recordingChunks.value, { type: mimeType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      recordingChunks.value = [];
    };

    const toggleRecording = () => {
      if (isRecording.value) {
        stopRecording();
      } else {
        startRecording();
      }
    };


    onMounted(() => {
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
      errorMessage,
      isRecording,
      recordingFileSize,
      recordingDuration,
      currentRecordingMode,
      toggleRecording
    };
  }
};
</script>