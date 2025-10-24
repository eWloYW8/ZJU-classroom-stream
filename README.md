# ZJU Classroom Stream

A web-based platform that provides live streaming of classroom sessions at Zhejiang University.

## Features

- **Live Streaming**: Watch live classroom sessions in real-time.
- **Searchable Channel List**: Quickly find classrooms using the search functionality.
- **Auto-updated Stream Data**: Stream data is automatically updated every hour using GitHub Actions.

  [![Update Stream Data](https://github.com/eWloYW8/ZJU-classroom-stream/actions/workflows/update.yml/badge.svg)](https://github.com/eWloYW8/ZJU-classroom-stream/actions/workflows/update.yml)

## GitHub Pages

[https://zjustream.p5s.fun](https://zjustream.p5s.fun)

[![Deploy to GitHub Pages](https://github.com/eWloYW8/ZJU-classroom-stream/actions/workflows/deploy.yml/badge.svg)](https://github.com/eWloYW8/ZJU-classroom-stream/actions/workflows/deploy.yml)

## Deploy

1. Clone the repository:
   ```bash
   git clone https://github.com/eWloYW8/ZJU-classroom-stream.git
   cd ZJU-classroom-stream
   ```

2. Install frontend dependencies:
   ```bash
   pnpm install
   ```

3. Build the project:
   ```bash
   pnpm run build
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
   pnpm install -g serve
   serve -s dist
   ```
   Then open:
   ```
   http://localhost:3000
   ```

## Deployment

You can deploy the `dist/` folder to any static hosting service, such as GitHub Pages, Netlify, or Vercel.  
Ensure that the `stream_db.json` file is updated regularly using the provided GitHub Actions workflow.

## GitHub Actions

The project includes a GitHub Actions workflow (`.github/workflows/update.yml`) to automatically update the `stream_db.json` file every hour.  
To enable this:

1. Add the following secrets to your GitHub repository:
   - `ZJUAM_USERNAME`: Your Zhejiang University username.
   - `ZJUAM_PASSWORD`: Your Zhejiang University password.

2. The workflow will automatically run on schedule and commit updates.

## Disclaimer

This project is provided for educational and informational purposes only.  
The author is not responsible for any misuse or damage caused by this project. Use it at your own risk.

The copyright of the live videos belongs to Zhejiang University.
