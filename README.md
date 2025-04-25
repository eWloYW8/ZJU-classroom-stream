# ZJU Classroom Stream

A web-based platform that provides live streaming of classroom sessions at Zhejiang University.

## Features

- **Live Streaming**: Watch live classroom sessions in real-time.
- **Searchable Channel List**: Quickly find classrooms using the search functionality.
- **Auto-updated Stream Data**: Stream data is automatically updated every hour using GitHub Actions.

  [![Update Stream Data](https://github.com/eWloYW8/ZJU-classroom-stream/actions/workflows/update.yml/badge.svg)](https://github.com/eWloYW8/ZJU-classroom-stream/actions/workflows/update.yml)
- **Responsive Design**: Optimized for both desktop and mobile devices.

## GitHub Pages

[https://zjustream.p5s.fun](https://zjustream.p5s.fun)


## Deploy

1. Clone the repository:
   ```bash
   git clone https://github.com/eWloYW8/ZJU-classroom-stream.git
   cd ZJU-classroom-stream
   ```

2. Install Python dependencies:
   ```bash
   python -m pip install --upgrade pip
   pip install requests beautifulsoup4
   ```

3. Set environment variables for authentication:
   ```bash
   export ZJUAM_USERNAME=your_username
   export ZJUAM_PASSWORD=your_password
   ```

4. Run the scraper to update the stream database:
   ```bash
   python update_db.py
   ```

5. Serve the project locally using any static file server. For example:
   ```bash
   python -m http.server
   ```

6. Open the project in your browser:
   ```
   http://localhost:8000
   ```

## Usage

1. Open the web application in your browser.
2. Use the search bar to find a classroom by name.
3. Select a classroom from the list to start streaming.
4. Switch between HLS and WebRTC modes using the toggle buttons.

## Project Structure

- **`update_db.py`**: Python script to fetch and update live stream data.
- **`stream_db.json`**: JSON file storing the mapping of classroom names to stream IDs.
- **`static/`**: Contains static assets like CSS, JavaScript, and HTML files.
- **`index.html`**: Main entry point for the web application.
- **`.github/workflows/update.yml`**: GitHub Actions workflow for automatically updating the stream database.

## Deployment

To deploy the project, you can use any static hosting service like GitHub Pages, Netlify, or Vercel. Ensure that the `stream_db.json` file is regularly updated using the provided GitHub Actions workflow.

## GitHub Actions

The project includes a GitHub Actions workflow (`.github/workflows/update.yml`) to automatically update the `stream_db.json` file every hour. To enable this:

1. Add the following secrets to your repository:
   - `ZJUAM_USERNAME`: Your Zhejiang University username.
   - `ZJUAM_PASSWORD`: Your Zhejiang University password.

2. The workflow will run on schedule and commit updates to the repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [HLS.js](https://github.com/video-dev/hls.js) for HLS streaming.
- [JSWebrtc](https://github.com/kernelj/jswebrtc) for WebRTC streaming.

## Disclaimer
This project is provided for educational and informational purposes only. The author is not responsible for any misuse or damage caused by this project. Use it at your own risk.

The copyright of the live videos belongs to Zhejiang University.