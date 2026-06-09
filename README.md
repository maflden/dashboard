# PowerPulse KR - South Korea Real-Time Power Supply & Demand Dashboard


**PowerPulse KR** is a web-based, premium-designed interactive dashboard providing real-time data on South Korea's electric power supply, demand, and electricity generation breakdown by fuel type. Utilizing official open APIs from the Korea Power Exchange (KPX) and the Korea Public Data Portal, it showcases real-time metrics with high-fidelity, interactive visualizations.


---


## ⚡ Key Features


1. **Real-Time Power Supply & Demand Monitoring**
   - **Live Indicators**: Instantly tracks Key Performance Indicators (KPIs) including **Supply Capacity**, **Current Demand**, **Reserve Power**, and **Reserve Rate**.
   - **Glow Alert System**: Color-coded threshold styling reflecting real-time status alerts:
     - 🟢 **Normal**: Reserve Rate > 10%
     - 🟡 **Preparation**: 8% < Reserve Rate ≤ 10%
     - 🟠 **Attention**: 6% < Reserve Rate ≤ 8%
     - 🔴 **Caution**: 4% < Reserve Rate ≤ 6%
     - 🔥 **Alert / Critical**: Reserve Rate ≤ 4%
   - **5-Minute Trend Graph**: An interactive ApexCharts area chart dynamically plotting real-time supply capacity vs. current demand at 5-minute intervals.


2. **Generation by Fuel Type**
   - **Historical Settlement Queries**: Allows users to query historical electricity generation profiles by specific dates.
   - **Fuel Breakdown Ratio**: Visualizes overall daily generation share among Nuclear, Coal, Gas, and Renewables / Others using an interactive Donut chart.
   - **24-Hour Production Trends**: Multi-line/Stacked area chart mapping daily hourly production levels for each fuel type.
   - **Granular Data Grid**: Responsive table representation listing precise MWh numbers for offline auditing.


3. **Built-in CORS Bypass Local Proxy Server**
   - Direct browser calls to Korean OpenAPI endpoints often fail due to CORS policies. This repository includes a Node.js Express proxy to route client requests securely.
   - Robust error classification: Intercepts gateway quotas (e.g., Daily API limits) and normalizes XML/JSON payloads to guarantee client-side stability.
   - Embedded Demo Mode: Allows offline or simulated review with mock data when network issues or API quotas occur.


---


## 🛠️ Technology Stack


- **Frontend**:
  - **Structure & Logic**: HTML5, Vanilla JavaScript (ES6)
  - **Styling**: Vanilla CSS (Modern CSS properties, responsive grids, custom dark-mode glassmorphism variables, neon glow accents)
  - **Visualizations**: [ApexCharts](https://apexcharts.com/) (Rich interactive charting)
  - **Icons**: FontAwesome CDN
- **Backend (API Proxy)**:
  - **Runtime**: Node.js
  - **Framework**: Express.js
  - **HTTP Client**: Axios (for upstream API querying)
  - **Middleware**: CORS


---


## 🚀 Getting Started


Follow the instructions below to run the server and access the dashboard on your local machine.


### Prerequisites
- [Node.js](https://nodejs.org/) installed (v16 or higher recommended).


### Installation
1. Clone the project or navigate to the directory:
   ```bash
   cd /Users/hunte/.gemini/EnergyFund
   ```
2. Install the backend dependencies:
   ```bash
   npm install
   ```


### Run the Server
Start the Express server:
```bash
node server.js
```


Upon starting successfully, you will see the following terminal output:
```text
=============================================================
⚡ South Korea Real-Time Power Supply & Demand Dashboard Local Server Started.
👉 Open your browser and navigate to:
   💻 http://localhost:3000
=============================================================
```


### Accessing the Web Dashboard
Open your browser and navigate to:
👉 **[http://localhost:3000](http://localhost:3000)**


---


## 🔌 API Architecture & Proxy Details


The server acts as an intermediary proxy between the client and public endpoints:
- **Real-Time Supply/Demand API**: `https://openapi.kpx.or.kr/openapi/sukub5mToday/getSukub5mToday`
  - *Proxy Route*: `/api/sukub5mToday`
  - *Format*: XML (Parsed on client-side using `DOMParser`).
- **Generation by Fuel Type API**: `https://apis.data.go.kr/B552115/PvAmountByPwrGen/getPvAmountByPwrGen`
  - *Proxy Route*: `/api/PvAmountByPwrGen`
  - *Format*: JSON (Normalized by `classifyGenPayload` to prevent client parsing errors during API quota issues).


---


## 📄 License & Source Data
- **Data Provider**: Korea Power Exchange (KPX), Korea Public Data Portal
- This project is meant for informational and educational dashboards tracking grid performance.

