const videoHLS = document.getElementById('video-player');
const videoWebRTC = document.getElementById('video-webrtc');
let hls = null;
let currentStreamId = null;
let currentPlayer = null;
let currentMode = 'hls';
let allChannels = [];

function initHLSPlayer(streamId) {
    if (hls) hls.destroy();
    videoWebRTC.style.display = 'none';
    videoHLS.style.display = 'block';
    const streamUrl = `https://livepgc.cmc.zju.edu.cn/pgc/${streamId}.m3u8`;
    if (Hls.isSupported()) {
        hls = new Hls();
        hls.loadSource(streamUrl);
        hls.attachMedia(videoHLS);
        hls.on(Hls.Events.MANIFEST_PARSED, () => videoHLS.play());
    } else {
        videoHLS.src = streamUrl;
        videoHLS.addEventListener('loadedmetadata', () => videoHLS.play());
    }
}

function initWebRTCPlayer(streamId) {
    if (currentPlayer) currentPlayer.destroy();
    videoHLS.style.display = 'none';
    videoWebRTC.style.display = 'block';
    const url = `webrtc://mcloudpush.cmc.zju.edu.cn/live/${streamId}`;
    currentPlayer = new JSWebrtc.Player(url, {
        video: videoWebRTC,
        autoplay: true,
        onPlay: () => console.log(`Playing ${streamId}`),
        onError: (err) => alert(`播放失败: ${err.message}`)
    });
}

function updatePlayer(streamId) {
    currentStreamId = streamId;
    if (currentMode === 'hls') {
        initHLSPlayer(streamId);
    } else {
        initWebRTCPlayer(streamId);
    }
}

async function loadChannelList() {
    try {
        document.getElementById('loadingText').style.opacity = 1;

        const res = await fetch('stream_db.json');
        let channels = await res.json();

        channels = Object.keys(channels).sort().reduce((sorted, key) => {
            sorted[key] = channels[key];
            return sorted;
        }, {});

        try {
            const response_extended = await fetch("https://mcloudpush.cmc.zju.edu.cn:10443/streams");
            if (response_extended.ok) {
                const data = await response_extended.json();

                data.streams.forEach(stream => {
                    const streamKey = Object.keys(stream)[0];
                    if (!Object.values(channels).includes(streamKey)) {
                        channels[`Unknown: ${streamKey}`] = streamKey;
                    }
                });
            } else {
                console.warn(`Extended fetch failed with status: ${response_extended.status}`);
            }
        } catch (error) {
            console.error('Error fetching extended data:', error);
        }

        const listEl = document.getElementById('channelList');

        allChannels = Object.entries(channels).map(([name, id]) => {
            const li = document.createElement('li');
            li.className = 'channel-item';
            li.textContent = name;
            li.addEventListener('click', () => {
                document.querySelectorAll('.channel-item').forEach(item => item.classList.remove('active'));
                li.classList.add('active');
                updatePlayer(id);
            });
            listEl.appendChild(li);
            return { name, id, element: li };
        });

        document.getElementById('searchInput').addEventListener('input', (e) => {
            const keyword = e.target.value.toLowerCase().trim();
            allChannels.forEach(item => {
                const match = item.name.toLowerCase().includes(keyword);
                item.element.classList.toggle('hidden', !match);
            });
            const firstVisible = allChannels.find(item => !item.element.classList.contains('hidden'));
            if (firstVisible) firstVisible.element.click();
        });

        if (allChannels.length > 0) allChannels[0].element.click();

        document.getElementById('loadingText').style.opacity = 0;
    } catch (err) {
        console.error(err);
        document.getElementById('loadingText').textContent = '加载失败，请刷新重试。';
    }
}

window.addEventListener('DOMContentLoaded', () => {
    loadChannelList();

    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;
            if (currentStreamId) updatePlayer(currentStreamId);
        });
    });
});