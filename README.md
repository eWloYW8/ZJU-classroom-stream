# ZJU Classroom Stream

A web-based platform that provides live streaming of classroom sessions at Zhejiang University.

## Features

- **Live Streaming**: Watch live classroom sessions in real-time.
- **Searchable Channel List**: Quickly find classrooms using the search functionality.
- **Auto-updated Stream Data**: Stream data is automatically updated every hour using GitHub Actions.

  [![Update Stream Data](https://github.com/eWloYW8/ZJU-classroom-stream/actions/workflows/update.yml/badge.svg)](https://github.com/eWloYW8/ZJU-classroom-stream/actions/workflows/update.yml)
- **Responsive Design**: Optimized for both desktop and mobile devices.
- **Modern Frontend**: Built with Vue 3, Webpack, and npm for efficient development and deployment.

## GitHub Pages

[https://zjustream.p5s.fun](https://zjustream.p5s.fun)

## Deploy

1. Clone the repository:
   ```bash
   git clone https://github.com/eWloYW8/ZJU-classroom-stream.git
   cd ZJU-classroom-stream
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Build the project:
   ```bash
   npm run build
   ```
   The production-ready static files will be generated in the `dist/` folder.

4. Install Python dependencies (for stream database update):
   ```bash
   python -m pip install --upgrade pip
   pip install requests beautifulsoup4
   ```

5. Set environment variables for authentication:
   ```bash
   export ZJUAM_USERNAME=your_username
   export ZJUAM_PASSWORD=your_password
   ```

6. Run the scraper to update the stream database:
   ```bash
   python update_db.py
   ```

7. Serve the built project locally (optional for testing):
   ```bash
   npm install -g serve
   serve -s dist
   ```
   Then open:
   ```
   http://localhost:3000
   ```

## Usage

1. Open the deployed web application in your browser.
2. Use the search bar to find a classroom by name.
3. Select a classroom from the list to start streaming.
4. Switch between HLS and WebRTC modes using the toggle buttons.

## Development

To start a local development server with hot reload:

```bash
npm run dev
```

This will start the application at `http://localhost:5173` (default Vite dev server port if using Vite, or if you stick to Webpack, the default Webpack dev server port, e.g., `http://localhost:8080`).

## Deployment

You can deploy the `dist/` folder to any static hosting service, such as GitHub Pages, Netlify, or Vercel.  
Ensure that the `stream_db.json` file is updated regularly using the provided GitHub Actions workflow.

> **Tip**: On GitHub Pages, you can configure the deployment source as the `dist/` folder from the `gh-pages` branch.

## GitHub Actions

The project includes a GitHub Actions workflow (`.github/workflows/update.yml`) to automatically update the `stream_db.json` file every hour.  
To enable this:

1. Add the following secrets to your GitHub repository:
   - `ZJUAM_USERNAME`: Your Zhejiang University username.
   - `ZJUAM_PASSWORD`: Your Zhejiang University password.

2. The workflow will automatically run on schedule and commit updates.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Vue.js](https://vuejs.org/) for the frontend framework.
- [Webpack](https://webpack.js.org/) for module bundling.
- [HLS.js](https://github.com/video-dev/hls.js) for HLS streaming.
- [JSWebrtc](https://github.com/kernelj/jswebrtc) for WebRTC streaming.

## Disclaimer

This project is provided for educational and informational purposes only.  
The author is not responsible for any misuse or damage caused by this project. Use it at your own risk.

The copyright of the live videos belongs to Zhejiang University.
