import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Button,
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Link,
} from "@mui/material";
import {
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Palette as PaletteIcon,
  Save as SaveIcon,
  OpenInNew as OpenInNewIcon,
  Monitor as MonitorIcon,
} from "@mui/icons-material";

const SettingsPage = ({ onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState({
    notifications: true,
    darkMode: false,
    autoRefresh: true,
  });

  const handleSettingChange = (setting, value) => {
    setSettings((prev) => ({
      ...prev,
      [setting]: value,
    }));
  };

  const handleSaveSettings = () => {
    // In a real implementation, this would save to backend
    onShowSnackbar("Settings saved successfully", "success");
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: "auto", p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant='h4'
          sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
        >
          Settings
        </Typography>
        <Typography variant='body1' color='text.secondary'>
          Manage your application preferences and system configuration.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* System Status Link */}
        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 2, boxShadow: 1, height: "100%" }}>
            <CardContent sx={{ textAlign: "center", py: 4 }}>
              <MonitorIcon sx={{ fontSize: 48, color: "#1976d2", mb: 2 }} />
              <Button
                variant='contained'
                startIcon={<OpenInNewIcon />}
                component={Link}
                href='/status'
                target='_blank'
                sx={{
                  bgcolor: "#1976d2",
                  "&:hover": { bgcolor: "#1565c0" },
                  borderRadius: 2,
                  px: 3,
                  py: 1.5,
                  fontWeight: "bold",
                }}
              >
                System Status
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Application Settings */}
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: 2, boxShadow: 1, height: "100%" }}>
            <CardContent>
              <Typography
                variant='h6'
                sx={{ fontWeight: "bold", color: "#424242", mb: 3 }}
              >
                Application Settings
              </Typography>

              <Grid container spacing={3}>
                {/* Notifications */}
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <NotificationsIcon sx={{ mr: 1, color: "#1976d2" }} />
                    <Typography variant='subtitle1' sx={{ fontWeight: "bold" }}>
                      Notifications
                    </Typography>
                  </Box>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notifications}
                        onChange={(e) =>
                          handleSettingChange("notifications", e.target.checked)
                        }
                      />
                    }
                    label='Enable notifications'
                  />
                  <Typography
                    variant='caption'
                    color='text.secondary'
                    display='block'
                  >
                    Show alerts for system events and updates
                  </Typography>
                </Grid>

                {/* Theme */}
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                    <PaletteIcon sx={{ mr: 1, color: "#1976d2" }} />
                    <Typography variant='subtitle1' sx={{ fontWeight: "bold" }}>
                      Appearance
                    </Typography>
                  </Box>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.darkMode}
                        onChange={(e) =>
                          handleSettingChange("darkMode", e.target.checked)
                        }
                      />
                    }
                    label='Dark mode'
                  />
                  <Typography
                    variant='caption'
                    color='text.secondary'
                    display='block'
                  >
                    Switch to dark theme interface
                  </Typography>
                </Grid>

                {/* Auto Refresh */}
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.autoRefresh}
                        onChange={(e) =>
                          handleSettingChange("autoRefresh", e.target.checked)
                        }
                      />
                    }
                    label='Auto-refresh data'
                  />
                  <Typography
                    variant='caption'
                    color='text.secondary'
                    display='block'
                  >
                    Automatically refresh data every 30 seconds
                  </Typography>
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />

              <Button
                variant='contained'
                startIcon={<SaveIcon />}
                onClick={handleSaveSettings}
                fullWidth
                sx={{
                  bgcolor: "#1976d2",
                  "&:hover": { bgcolor: "#1565c0" },
                  borderRadius: 2,
                  py: 1.5,
                  fontWeight: "bold",
                }}
              >
                Save Settings
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SettingsPage;
