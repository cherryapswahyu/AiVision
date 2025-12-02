import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Typography,
  Chip,
  IconButton,
  AppBar,
  Toolbar,
  Button,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Restaurant,
  Settings,
  Logout,
  Refresh,
  Videocam,
  People,
  AccessTime,
  TrendingUp,
  CleaningServices,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const Dashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [analytics, setAnalytics] = useState({
    occupancy: 0,
    waitTime: 0,
    transactions: 0,
    tablesToClean: 0,
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/v1/dashboard/cameras/');
      setCameras(response.data);
      
      // Calculate analytics from camera data
      let totalOccupancy = 0;
      let totalWaitTime = 0;
      let totalTransactions = 0;
      let totalTablesToClean = 0;
      let cameraCount = 0;

      response.data.forEach((camera) => {
        if (camera.latest_log) {
          const log = camera.latest_log;
          
          if (log.occupancy_percentage) {
            totalOccupancy += log.occupancy_percentage;
            cameraCount++;
          }
          if (log.average_wait_time_minutes) {
            totalWaitTime += log.average_wait_time_minutes;
          }
          if (log.transactions_per_hour) {
            totalTransactions += log.transactions_per_hour;
          }
          if (log.tables_to_clean) {
            totalTablesToClean += log.tables_to_clean;
          }
        }
      });

      setAnalytics({
        occupancy: cameraCount > 0 ? Math.round(totalOccupancy / cameraCount) : 0,
        waitTime: Math.round(totalWaitTime),
        transactions: totalTransactions,
        tablesToClean: totalTablesToClean,
      });

      setLoading(false);
      setError('');
    } catch (err) {
      setError('Gagal memuat data dashboard');
      setLoading(false);
      console.error(err);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ONLINE':
        return 'success';
      case 'WARNING':
        return 'warning';
      case 'OFFLINE':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ONLINE':
        return <CheckCircle />;
      case 'WARNING':
        return <Warning />;
      case 'OFFLINE':
        return <ErrorIcon />;
      default:
        return null;
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

  const getAreaTypeIcon = (areaType) => {
    switch (areaType) {
      case 'ENTRANCE':
        return '🚪';
      case 'DINING':
        return '🍽️';
      case 'CASHIER':
        return '💰';
      case 'KITCHEN':
        return '👨‍🍳';
      default:
        return '📹';
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('id-ID', { hour12: false });
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
      {/* Header */}
      <AppBar position="sticky" sx={{ backgroundColor: '#2c3e50' }}>
        <Toolbar>
          <Restaurant sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Dashboard AI Restoran Cerdas
          </Typography>
          <Typography variant="body2" sx={{ mr: 3 }}>
            {formatTime(currentTime)}
          </Typography>
          <Button
            color="inherit"
            startIcon={<Settings />}
            onClick={() => navigate('/settings')}
            sx={{ mr: 1 }}
          >
            Pengaturan
          </Button>
          <Button color="inherit" startIcon={<Logout />} onClick={logout}>
            Keluar
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ py: 3 }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Analytics Overview */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      Kapasitas Terisi
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" color="primary">
                      {analytics.occupancy}%
                    </Typography>
                  </Box>
                  <People sx={{ fontSize: 48, color: '#3498db' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      Rata-rata Waktu Tunggu
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" color="error">
                      {analytics.waitTime}m
                    </Typography>
                  </Box>
                  <AccessTime sx={{ fontSize: 48, color: '#e74c3c' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      Transaksi/Jam
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" color="success.main">
                      {analytics.transactions}
                    </Typography>
                  </Box>
                  <TrendingUp sx={{ fontSize: 48, color: '#2ecc71' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      Meja Perlu Dibersihkan
                    </Typography>
                    <Typography variant="h4" fontWeight="bold" color="warning.main">
                      {analytics.tablesToClean}
                    </Typography>
                  </Box>
                  <CleaningServices sx={{ fontSize: 48, color: '#f39c12' }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Camera Grid */}
        <Grid container spacing={3}>
          {cameras.map((camera) => (
            <Grid item xs={12} md={6} key={camera.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardHeader
                  avatar={<Typography variant="h5">{getAreaTypeIcon(camera.area_type)}</Typography>}
                  title={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="h6">{camera.name}</Typography>
                      <Chip
                        icon={getStatusIcon(camera.status)}
                        label={camera.status}
                        color={getStatusColor(camera.status)}
                        size="small"
                      />
                    </Box>
                  }
                  subheader={getAreaTypeLabel(camera.area_type)}
                  action={
                    <IconButton onClick={fetchDashboardData} size="small">
                      <Refresh />
                    </IconButton>
                  }
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  {/* Camera Snapshot Placeholder */}
                  <Paper
                    sx={{
                      height: 250,
                      backgroundColor: '#000',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                      position: 'relative',
                      overflow: 'hidden',
                    }}
                  >
                    <Box
                      sx={{
                        position: 'absolute',
                        top: 10,
                        right: 10,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        color: 'white',
                        px: 1,
                        py: 0.5,
                        borderRadius: 1,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5,
                      }}
                    >
                      <Videocam fontSize="small" />
                      <Typography variant="caption">AI Active</Typography>
                    </Box>
                    {camera.latest_log?.person_count && (
                      <Box
                        sx={{
                          position: 'absolute',
                          bottom: 10,
                          left: 10,
                          backgroundColor: 'success.main',
                          color: 'white',
                          px: 2,
                          py: 1,
                          borderRadius: 2,
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5,
                        }}
                      >
                        <People fontSize="small" />
                        <Typography variant="body2" fontWeight="bold">
                          {camera.latest_log.person_count}
                        </Typography>
                      </Box>
                    )}
                    <Box textAlign="center" color="white">
                      <Videocam sx={{ fontSize: 60, mb: 1 }} />
                      <Typography>Live Feed - {getAreaTypeLabel(camera.area_type)}</Typography>
                      {camera.latest_log && (
                        <Typography variant="caption">
                          AI mendeteksi: {camera.latest_log.person_count || 0} orang
                        </Typography>
                      )}
                    </Box>
                  </Paper>

                  {/* Analytics */}
                  {camera.latest_log && (
                    <Box>
                      {camera.area_type === 'ENTRANCE' && (
                        <>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Orang Masuk (60m):</Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {camera.latest_log.people_entered || 0}
                            </Typography>
                          </Box>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Rata-rata Waktu Tunggu:</Typography>
                            <Typography variant="body2" fontWeight="bold" color="success.main">
                              {camera.latest_log.average_wait_time_minutes || 0} menit
                            </Typography>
                          </Box>
                        </>
                      )}
                      {camera.area_type === 'DINING' && (
                        <>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Kapasitas Terisi:</Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {camera.latest_log.occupancy_percentage || 0}%
                            </Typography>
                          </Box>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Meja Tersedia:</Typography>
                            <Typography variant="body2" fontWeight="bold" color="success.main">
                              {camera.latest_log.available_tables || 0}
                            </Typography>
                          </Box>
                        </>
                      )}
                      {camera.area_type === 'CASHIER' && (
                        <>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Panjang Antrian:</Typography>
                            <Typography variant="body2" fontWeight="bold" color="error">
                              {camera.latest_log.queue_length || 0} orang
                            </Typography>
                          </Box>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Waktu Tunggu Rata-rata:</Typography>
                            <Typography variant="body2" fontWeight="bold" color="error">
                              {camera.latest_log.average_wait_time_minutes || 0} menit
                            </Typography>
                          </Box>
                        </>
                      )}
                      {camera.area_type === 'KITCHEN' && (
                        <>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Staf Aktif:</Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {camera.latest_log.staff_active_count || 0}/
                              {camera.latest_log.staff_total_scheduled || 0}
                            </Typography>
                          </Box>
                          <Box display="flex" justifyContent="space-between" mb={1}>
                            <Typography variant="body2">Pesanan Aktif:</Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {camera.latest_log.active_orders || 0}
                            </Typography>
                          </Box>
                        </>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {cameras.length === 0 && !loading && (
          <Paper sx={{ p: 4, textAlign: 'center', mt: 3 }}>
            <Typography variant="h6" color="text.secondary">
              Tidak ada kamera yang terdaftar
            </Typography>
          </Paper>
        )}
      </Container>
    </Box>
  );
};

export default Dashboard;

