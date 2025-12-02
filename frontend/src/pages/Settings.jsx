import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardHeader,
  IconButton,
  Alert,
  CircularProgress,
  AppBar,
  Toolbar,
  Divider,
  Chip,
} from '@mui/material';
import {
  ArrowBack,
  Save,
  Restaurant,
  Videocam,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import axios from 'axios';

const Settings = () => {
  const navigate = useNavigate();
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    try {
      const response = await axios.get('/api/v1/dashboard/cameras/');
      setCameras(response.data);
      setLoading(false);
    } catch (err) {
      setError('Gagal memuat data kamera');
      setLoading(false);
      console.error(err);
    }
  };

  const handleRtspUrlChange = (cameraId, value) => {
    setCameras((prev) =>
      prev.map((cam) => (cam.id === cameraId ? { ...cam, rtsp_url: value } : cam))
    );
  };

  const handleRoiSettingsChange = (cameraId, value) => {
    try {
      const parsed = JSON.parse(value);
      setCameras((prev) =>
        prev.map((cam) => (cam.id === cameraId ? { ...cam, roi_settings: parsed } : cam))
      );
    } catch (err) {
      // Invalid JSON, but we'll let the user continue typing
    }
  };

  const handleSave = async (cameraId) => {
    setSaving((prev) => ({ ...prev, [cameraId]: true }));
    setError('');
    setSuccess('');

    const camera = cameras.find((c) => c.id === cameraId);
    if (!camera) return;

    try {
      const updateData = {
        rtsp_url: camera.rtsp_url,
        roi_settings: camera.roi_settings,
      };

      await axios.put(`/api/v1/cameras/${cameraId}`, updateData);
      setSuccess(`Pengaturan kamera ${camera.name} berhasil disimpan`);
      setSaving((prev) => ({ ...prev, [cameraId]: false }));
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Gagal menyimpan pengaturan');
      setSaving((prev) => ({ ...prev, [cameraId]: false }));
    }
  };

  const getAreaTypeLabel = (areaType) => {
    const labels = {
      ENTRANCE: 'Pintu Masuk',
      DINING: 'Area Makan',
      CASHIER: 'Kasir',
      KITCHEN: 'Dapur',
    };
    return labels[areaType] || areaType;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      <AppBar position="sticky" sx={{ backgroundColor: '#2c3e50' }}>
        <Toolbar>
          <IconButton edge="start" color="inherit" onClick={() => navigate('/dashboard')} sx={{ mr: 2 }}>
            <ArrowBack />
          </IconButton>
          <Restaurant sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Pengaturan Kamera
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
          Konfigurasi Kamera
        </Typography>

        <Grid container spacing={3}>
          {cameras.map((camera) => (
            <Grid item xs={12} key={camera.id}>
              <Card>
                <CardHeader
                  avatar={<Videocam color="primary" />}
                  title={camera.name}
                  subheader={
                    <Box display="flex" gap={1} alignItems="center" mt={1}>
                      <Chip label={getAreaTypeLabel(camera.area_type)} size="small" />
                      <Chip
                        label={camera.status}
                        size="small"
                        color={
                          camera.status === 'ONLINE'
                            ? 'success'
                            : camera.status === 'WARNING'
                            ? 'warning'
                            : 'error'
                        }
                      />
                    </Box>
                  }
                />
                <Divider />
                <CardContent>
                  <Grid container spacing={3}>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="RTSP URL"
                        value={camera.rtsp_url || ''}
                        onChange={(e) => handleRtspUrlChange(camera.id, e.target.value)}
                        placeholder="rtsp://username:password@ip:port/stream"
                        helperText="Masukkan URL stream RTSP untuk kamera ini"
                        variant="outlined"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="ROI Settings (JSON)"
                        value={JSON.stringify(camera.roi_settings || {}, null, 2)}
                        onChange={(e) => handleRoiSettingsChange(camera.id, e.target.value)}
                        multiline
                        rows={6}
                        helperText="Format JSON untuk pengaturan Region of Interest (ROI)"
                        variant="outlined"
                        sx={{
                          '& .MuiInputBase-input': {
                            fontFamily: 'monospace',
                            fontSize: '0.875rem',
                          },
                        }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Box display="flex" justifyContent="flex-end">
                        <Button
                          variant="contained"
                          startIcon={saving[camera.id] ? <CircularProgress size={20} /> : <Save />}
                          onClick={() => handleSave(camera.id)}
                          disabled={saving[camera.id]}
                        >
                          {saving[camera.id] ? 'Menyimpan...' : 'Simpan Pengaturan'}
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {cameras.length === 0 && (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <SettingsIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Tidak ada kamera yang terdaftar
            </Typography>
          </Paper>
        )}

        {/* ROI Settings Help */}
        <Paper sx={{ p: 3, mt: 4, backgroundColor: '#f8f9fa' }}>
          <Typography variant="h6" gutterBottom>
            Panduan ROI Settings
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            ROI (Region of Interest) Settings digunakan untuk menentukan area deteksi pada kamera.
            Format JSON yang didukung:
          </Typography>
          <Box
            component="pre"
            sx={{
              backgroundColor: '#fff',
              p: 2,
              borderRadius: 1,
              overflow: 'auto',
              fontSize: '0.875rem',
            }}
          >
            {`// Untuk ENTRANCE (Line Zone):
{
  "type": "LINE",
  "start": [x1, y1],
  "end": [x2, y2]
}

// Untuk DINING (Polygon Zone):
{
  "type": "POLYGON",
  "points": [[x1, y1], [x2, y2], [x3, y3], ...]
}

// Untuk CASHIER/KITCHEN (Rectangle Zone):
{
  "type": "RECTANGLE",
  "x": 100,
  "y": 100,
  "width": 500,
  "height": 300
}`}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default Settings;

