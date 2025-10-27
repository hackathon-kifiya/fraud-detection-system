import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Button,
  Tabs,
  Tab,
} from "@mui/material";
import {
  Security,
  TrendingUp,
  Warning,
  CheckCircle,
  Cancel,
  Assessment,
  AccountBalance,
  CreditCard,
  Person,
  Payment,
} from "@mui/icons-material";
import { flaggedAPI } from "../services/api";

const Dashboard = ({ onShowSnackbar }) => {
  const [stats, setStats] = useState({
    totalFlagged: 0,
    pendingReview: 0,
    confirmedFraud: 0,
    verifiedSafe: 0,
    highRiskCount: 0,
    flaggedByType: {},
    recentActivity: [],
  });
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState(0);

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await flaggedAPI.getStats();
      setStats(response.data);
    } catch (error) {
      // If stats API is not available, use empty values
      console.warn("Stats API not available, using empty values");
      setStats({
        totalFlagged: 0,
        pendingReview: 0,
        confirmedFraud: 0,
        verifiedSafe: 0,
        highRiskCount: 0,
        flaggedByType: {},
        recentActivity: [],
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  // Icon mapping for different data types
  const iconMapping = {
    transactions: AccountBalance,
    loan_requests: CreditCard,
    credit_history: Assessment,
    kyc: Person,
    repayments: Payment,
  };

  // Color mapping for different data types
  const colorMapping = {
    transactions: "#1976d2",
    loan_requests: "#388e3c",
    credit_history: "#f57c00",
    kyc: "#7b1fa2",
    repayments: "#d32f2f",
  };

  // Helper function to format label from key
  const formatLabel = (key) => {
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Dynamically generate fraud detection types from stats
  const fraudDetectionTypes = Object.keys(stats.flaggedByType || {}).map(key => ({
    key: key,
    label: formatLabel(key),
    icon: iconMapping[key] || Assessment, // Default icon if not mapped
    color: colorMapping[key] || "#757575", // Default color if not mapped
  }));

  if (loading) {
    return (
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          minHeight: 400,
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography
          variant='h4'
          sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
        >
          Fraud Detection Dashboard
        </Typography>
        <Typography variant='body1' color='text.secondary'>
          Overview of fraud detection system performance and flagged items
          across all data types.
        </Typography>
      </Box>

      {/* Main Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 2, height: "100%" }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 2,
                    bgcolor: "#ffebee",
                    color: "#d32f2f",
                    mr: 2,
                  }}
                >
                  <Security sx={{ fontSize: 24 }} />
                </Box>
                <Typography
                  variant='h6'
                  sx={{ fontWeight: "bold", color: "#424242" }}
                >
                  Total Flagged
                </Typography>
              </Box>
              <Typography
                variant='h3'
                sx={{ fontWeight: "bold", color: "#d32f2f", mb: 1 }}
              >
                {stats.totalFlagged}
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Items requiring review
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 2, height: "100%" }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 2,
                    bgcolor: "#fff3e0",
                    color: "#f57c00",
                    mr: 2,
                  }}
                >
                  <Warning sx={{ fontSize: 24 }} />
                </Box>
                <Typography
                  variant='h6'
                  sx={{ fontWeight: "bold", color: "#424242" }}
                >
                  Pending Review
                </Typography>
              </Box>
              <Typography
                variant='h3'
                sx={{ fontWeight: "bold", color: "#f57c00", mb: 1 }}
              >
                {stats.pendingReview}
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Awaiting verification
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 2, height: "100%" }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 2,
                    bgcolor: "#ffebee",
                    color: "#d32f2f",
                    mr: 2,
                  }}
                >
                  <Cancel sx={{ fontSize: 24 }} />
                </Box>
                <Typography
                  variant='h6'
                  sx={{ fontWeight: "bold", color: "#424242" }}
                >
                  Confirmed Fraud
                </Typography>
              </Box>
              <Typography
                variant='h3'
                sx={{ fontWeight: "bold", color: "#d32f2f", mb: 1 }}
              >
                {stats.confirmedFraud}
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Verified fraudulent items
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 2, height: "100%" }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <Box
                  sx={{
                    p: 1,
                    borderRadius: 2,
                    bgcolor: "#e8f5e8",
                    color: "#388e3c",
                    mr: 2,
                  }}
                >
                  <CheckCircle sx={{ fontSize: 24 }} />
                </Box>
                <Typography
                  variant='h6'
                  sx={{ fontWeight: "bold", color: "#424242" }}
                >
                  Verified Safe
                </Typography>
              </Box>
              <Typography
                variant='h3'
                sx={{ fontWeight: "bold", color: "#388e3c", mb: 1 }}
              >
                {stats.verifiedSafe}
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Legitimate transactions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detection Types Overview with Tabs */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Paper sx={{ borderRadius: 2, boxShadow: 2, overflow: "hidden" }}>
            <Box sx={{ p: 3, borderBottom: "1px solid #e0e0e0" }}>
              <Typography
                variant='h6'
                sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
              >
                Fraud Detection by Data Type
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Flagged items breakdown across different data categories
              </Typography>
            </Box>

            <Box>
              <Tabs
                value={selectedTab}
                onChange={(e, newValue) => setSelectedTab(newValue)}
                variant="scrollable"
                scrollButtons="auto"
                sx={{
                  borderBottom: "1px solid #e0e0e0",
                  "& .MuiTab-root": {
                    textTransform: "capitalize",
                    fontWeight: 500,
                    fontSize: "0.875rem",
                  },
                  "& .Mui-selected": {
                    fontWeight: "bold",
                  },
                }}
              >
                {fraudDetectionTypes.map((type) => (
                  <Tab
                    key={type.key}
                    label={
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                        <type.icon sx={{ fontSize: 20 }} />
                        <span>{type.label}</span>
                      </Box>
                    }
                  />
                ))}
              </Tabs>
            </Box>

            <Box sx={{ p: 2 }}>
              {fraudDetectionTypes.map((type, index) => {
                const IconComponent = type.icon;
                const count = stats.flaggedByType?.[type.key] || 0;
                const percentage = stats.totalFlagged > 0 
                  ? ((count / stats.totalFlagged) * 100).toFixed(1) 
                  : 0;

                return (
                  <Box
                    key={type.key}
                    sx={{ display: selectedTab === index ? "block" : "none" }}
                  >
                    <Card
                      sx={{
                        borderRadius: 2,
                        boxShadow: 1,
                        bgcolor: "#ffffff",
                        border: "1px solid #e0e0e0",
                      }}
                    >
                      <CardContent sx={{ p: 2, "&:last-child": { pb: 2 } }}>
                        <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                          <Box
                            sx={{
                              p: 1.5,
                              borderRadius: 2,
                              bgcolor: "#f5f5f5",
                              mr: 2,
                            }}
                          >
                            <IconComponent sx={{ fontSize: 32, color: "#757575" }} />
                          </Box>
                          <Box>
                            <Typography
                              variant='h6'
                              sx={{ fontWeight: "bold", color: "#424242" }}
                            >
                              {type.label}
                            </Typography>
                            <Typography variant='body2' color='text.secondary'>
                              Flagged Items
                            </Typography>
                          </Box>
                        </Box>
                        <Typography
                          variant='h2'
                          sx={{
                            fontWeight: "bold",
                            color: "#424242",
                            mb: 0.5,
                          }}
                        >
                          {count}
                        </Typography>
                        <Typography variant='body2' color='text.secondary'>
                          {percentage}% of total flagged items
                        </Typography>
                      </CardContent>
                    </Card>
                  </Box>
                );
              })}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
