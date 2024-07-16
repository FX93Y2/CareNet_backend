const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '..', '.env') });

const app = express();

// Enable CORS for all routes
app.use(cors());

app.get('/api/config', (req, res) => {
  res.json({
    arcgisApiKey: process.env.ARCGIS_API_KEY,
    arcgisPortalUrl: process.env.ARCGIS_PORTAL_URL,
  });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`Proxy server running on port ${PORT}`));