import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import {
  Assignment,
  CheckCircle,
  Cancel,
  PendingActions,
  Speed,
  Warning,
} from "@mui/icons-material";
import { auditAPI } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

const AuditorDashboard = ({ onShowSnackbar }) => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalReviewed: 0,
    confirmedFraud: 0,
    falsePositives: 0,
    averageReviewTime: 0,
    pendingReview: 0,
    highRiskItems: 0,
  });
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Load audit statistics (handle errors gracefully)
      try {
        const statsResponse = await auditAPI.getAuditStats();
        const backendStats = statsResponse.data.stats || statsResponse.data;
        
        // Map backend snake_case to frontend camelCase
        setStats({
          totalReviewed: backendStats.total_reviewed || 0,
          confirmedFraud: backendStats.confirmed_fraud || 0,
          falsePositives: backendStats.false_positives || 0,
          averageReviewTime: backendStats.average_review_time_minutes || 0,
          pendingReview: backendStats.pending_review || 0,
          highRiskItems: backendStats.high_risk_items || 0,
        });
      } catch (statsError) {
        console.warn("Stats API not available:", statsError);
        // Keep default stats if API fails
      }

      // Load my assignments (latest cases)
      try {
        const assignmentsResponse = await auditAPI.getMyAssignments({ 
          limit: 10,
          offset: 0
          // No status filter - show all cases, sorted by latest
        });
        setAssignments(assignmentsResponse.data.assignments || []);
      } catch (assignmentError) {
        console.warn("Assignments API not available:", assignmentError);
        setAssignments([]);
      }
      
    } catch (error) {
      console.error("Error loading dashboard data:", error);
      onShowSnackbar?.("Some dashboard data could not be loaded", "warning");
    } finally {
      setLoading(false);
    }
  }, [onShowSnackbar]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case "high":
        return "error";
      case "medium":
        return "warning";
      case "low":
        return "success";
      default:
        return "default";
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case "completed":
        return "success";
      case "in_progress":
        return "primary";
      case "assigned":
        return "warning";
      default:
        return "default";
    }
  };

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

  const reviewRate = stats.totalReviewed > 0 
    ? ((stats.confirmedFraud / stats.totalReviewed) * 100).toFixed(1)
    : 0;

  const accuracyRate = stats.totalReviewed > 0
    ? (((stats.totalReviewed - stats.falsePositives) / stats.totalReviewed) * 100).toFixed(1)
    : 0;

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography
          variant='h4'
          sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
        >
          Analyst Dashboard
        </Typography>
        <Typography variant='body1' color='text.secondary'>
          Welcome back, {user?.first_name}! Here's your case review overview and performance metrics.
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
                    bgcolor: "#e3f2fd",
                    color: "#1976d2",
                    mr: 2,
                  }}
                >
                  <Assignment sx={{ fontSize: 24 }} />
                </Box>
                <Typography
                  variant='h6'
                  sx={{ fontWeight: "bold", color: "#424242" }}
                >
                  Total Reviewed
                </Typography>
              </Box>
              <Typography
                variant='h3'
                sx={{ fontWeight: "bold", color: "#1976d2", mb: 1 }}
              >
                {stats.totalReviewed}
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Cases reviewed by you
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
                  <PendingActions sx={{ fontSize: 24 }} />
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
                Awaiting your review
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
                {reviewRate}% fraud detection rate
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
                    bgcolor: "#e8f5e9",
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
                  False Positives
                </Typography>
              </Box>
              <Typography
                variant='h3'
                sx={{ fontWeight: "bold", color: "#388e3c", mb: 1 }}
              >
                {stats.falsePositives}
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                {accuracyRate}% accuracy rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ borderRadius: 2, boxShadow: 2, p: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
              <Speed sx={{ fontSize: 28, color: "#1976d2", mr: 1 }} />
              <Typography
                variant='h6'
                sx={{ fontWeight: "bold", color: "#424242" }}
              >
                Average Review Time
              </Typography>
            </Box>
            <Typography
              variant='h2'
              sx={{ fontWeight: "bold", color: "#1976d2", mb: 1 }}
            >
              {stats.averageReviewTime}
              <Typography
                component='span'
                variant='h6'
                sx={{ color: "text.secondary", ml: 1 }}
              >
                minutes
              </Typography>
            </Typography>
            <Typography variant='body2' color='text.secondary'>
              Per case review
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ borderRadius: 2, boxShadow: 2, p: 3 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
              <Warning sx={{ fontSize: 28, color: "#d32f2f", mr: 1 }} />
              <Typography
                variant='h6'
                sx={{ fontWeight: "bold", color: "#424242" }}
              >
                High-Risk Items
              </Typography>
            </Box>
            <Typography
              variant='h2'
              sx={{ fontWeight: "bold", color: "#d32f2f", mb: 1 }}
            >
              {stats.highRiskItems}
            </Typography>
            <Typography variant='body2' color='text.secondary'>
              Requiring immediate attention
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Latest Cases */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ borderRadius: 2, boxShadow: 2, overflow: "hidden" }}>
            <Box sx={{ p: 3, borderBottom: "1px solid #e0e0e0" }}>
              <Typography
                variant='h6'
                sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
              >
                Latest Cases
              </Typography>
              <Typography variant='body2' color='text.secondary'>
                Your most recently assigned cases
              </Typography>
            </Box>

            {assignments.length === 0 ? (
              <Box sx={{ p: 4, textAlign: "center" }}>
                <Assignment sx={{ fontSize: 48, color: "#bdbdbd", mb: 2 }} />
                <Typography variant='h6' color='text.secondary'>
                  No cases assigned
                </Typography>
                <Typography variant='body2' color='text.secondary'>
                  You're all caught up! Check back later for new cases.
                </Typography>
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: "bold" }}>Case ID</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>Type</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>Priority</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>Assigned</TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>Due Date</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {assignments.map((assignment) => (
                      <TableRow
                        key={assignment.id}
                        hover
                        sx={{ cursor: "pointer" }}
                      >
                        <TableCell>
                          <Typography
                            variant='body2'
                            sx={{ fontWeight: "medium" }}
                          >
                            {assignment.flagged_item_id?.substring(0, 8)}...
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={assignment.item_type || "N/A"}
                            size='small'
                            variant='outlined'
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={assignment.priority || "Medium"}
                            size='small'
                            color={getPriorityColor(assignment.priority)}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={assignment.status || "Assigned"}
                            size='small'
                            color={getStatusColor(assignment.status)}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant='body2' color='text.secondary'>
                            {assignment.assigned_at
                              ? new Date(assignment.assigned_at).toLocaleDateString()
                              : "N/A"}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant='body2' color='text.secondary'>
                            {assignment.due_date
                              ? new Date(assignment.due_date).toLocaleDateString()
                              : "No deadline"}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AuditorDashboard;

