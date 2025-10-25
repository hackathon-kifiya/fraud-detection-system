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

  const loadStats = async () => {
    try {
      setLoading(true);
      const response = await flaggedAPI.getStats();
      setStats(response.data);
    } catch (error) {
      // If stats API is not available, use default values
      console.warn("Stats API not available, using default values");
      setStats({
        totalFlagged: 0,
        pendingReview: 0,
        confirmedFraud: 0,
        verifiedSafe: 0,
        highRiskCount: 0,
        flaggedByType: {
          transactions: 0,
          loan_requests: 0,
          credit_history: 0,
          kyc: 0,
          repayments: 0,
        },
        recentActivity: [],
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const fraudDetectionTypes = [
    {
      key: "transactions",
      label: "Transactions",
      icon: AccountBalance,
      color: "#1976d2",
    },
    {
      key: "loan_requests",
      label: "Loan Requests",
      icon: CreditCard,
      color: "#388e3c",
    },
    {
      key: "credit_history",
      label: "Credit History",
      icon: Assessment,
      color: "#f57c00",
    },
    { key: "kyc", label: "KYC Data", icon: Person, color: "#7b1fa2" },
    { key: "repayments", label: "Repayments", icon: Payment, color: "#d32f2f" },
  ];

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

      {/* Detection Types Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Paper sx={{ borderRadius: 2, boxShadow: 1, overflow: "hidden" }}>
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

            <Box sx={{ p: 3 }}>
              <Grid container spacing={2}>
                {fraudDetectionTypes.map((type) => {
                  const IconComponent = type.icon;
                  const count = stats.flaggedByType?.[type.key] || 0;

                  return (
                    <Grid item xs={12} sm={6} md={4} key={type.key}>
                      <Card
                        sx={{
                          borderRadius: 2,
                          boxShadow: 1,
                          height: "100%",
                          "&:hover": { boxShadow: 3 },
                        }}
                      >
                        <CardContent>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              mb: 2,
                            }}
                          >
                            <Box
                              sx={{
                                p: 1,
                                borderRadius: 2,
                                bgcolor: `${type.color}15`,
                                color: type.color,
                                mr: 2,
                              }}
                            >
                              <IconComponent sx={{ fontSize: 20 }} />
                            </Box>
                            <Typography
                              variant='h6'
                              sx={{ fontWeight: "bold", color: "#424242" }}
                            >
                              {type.label}
                            </Typography>
                          </Box>
                          <Typography
                            variant='h4'
                            sx={{
                              fontWeight: "bold",
                              color: type.color,
                              mb: 1,
                            }}
                          >
                            {count}
                          </Typography>
                          <Typography variant='body2' color='text.secondary'>
                            Flagged items
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  );
                })}
              </Grid>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Quick Actions Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12}>
          <Paper sx={{ borderRadius: 2, boxShadow: 1, overflow: "hidden" }}>
            <Box sx={{ p: 3, borderBottom: "1px solid #e0e0e0" }}>
              <Typography
                variant='h6'
                sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
              >
                Quick Actions
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Access fraud detection modules for different data types
              </Typography>
            </Box>

            <Box sx={{ p: 3 }}>
              <Grid container spacing={2}>
                {fraudDetectionTypes.map((type) => {
                  const IconComponent = type.icon;

                  return (
                    <Grid item xs={12} sm={6} md={4} key={type.key}>
                      <Card
                        sx={{
                          borderRadius: 2,
                          boxShadow: 1,
                          height: "100%",
                          "&:hover": { boxShadow: 3 },
                        }}
                      >
                        <CardContent>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              mb: 2,
                            }}
                          >
                            <Box
                              sx={{
                                p: 1,
                                borderRadius: 2,
                                bgcolor: `${type.color}15`,
                                color: type.color,
                                mr: 2,
                              }}
                            >
                              <IconComponent sx={{ fontSize: 20 }} />
                            </Box>
                            <Typography
                              variant='h6'
                              sx={{ fontWeight: "bold", color: "#424242" }}
                            >
                              {type.label}
                            </Typography>
                          </Box>
                          <Typography
                            variant='body2'
                            color='text.secondary'
                            paragraph
                          >
                            View and manage {type.label.toLowerCase()} fraud
                            detection
                          </Typography>
                          <Button
                            variant='outlined'
                            startIcon={<Security />}
                            href={`/${type.key.replace("_", "-")}`}
                            sx={{
                              borderRadius: 2,
                              px: 3,
                              py: 1,
                              borderColor: type.color,
                              color: type.color,
                              "&:hover": {
                                borderColor: type.color,
                                bgcolor: `${type.color}15`,
                              },
                            }}
                          >
                            Go to {type.label}
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>
                  );
                })}
              </Grid>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
