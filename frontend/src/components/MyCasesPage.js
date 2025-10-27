import React, { useState, useEffect, useCallback } from "react";
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Card,
  CardContent,
  Divider,
  Tabs,
  Tab,
  TextField,
  Alert,
} from "@mui/material";
import {
  Calculate as CalculateIcon,
  Visibility as ViewIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
} from "@mui/icons-material";
import { auditAPI } from "../services/api";

const MyCasesPage = ({ onShowSnackbar }) => {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const [reviewNote, setReviewNote] = useState("");
  const [classification, setClassification] = useState("");
  const [showRawJson, setShowRawJson] = useState(false);
  
  // Pagination state
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);

  const loadMyCases = useCallback(async () => {
    try {
      setLoading(true);
      const offset = page * limit;
      const response = await auditAPI.getMyAssignments({
        limit,
        offset,
      });
      setCases(response.data.assignments || []);
      setTotal(response.data.total || 0);
    } catch (error) {
      console.error("Error loading cases:", error);
      onShowSnackbar?.("Failed to load cases", "error");
      setCases([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [page, limit, onShowSnackbar]);

  useEffect(() => {
    loadMyCases();
  }, [loadMyCases]);

  const handleViewDetails = async (caseItem) => {
    try {
      // Fetch detailed information including original data and evaluation results
      const response = await auditAPI.getFlaggedItemDetail(
        caseItem.flagged_item_id
      );
      setSelectedCase(response.data);
      setDetailDialogOpen(true);
      setSelectedTab(0);
    } catch (error) {
      console.error("Error loading case details:", error);
      onShowSnackbar?.("Failed to load case details", "error");
    }
  };

  const handleCloseDialog = () => {
    setDetailDialogOpen(false);
    setSelectedCase(null);
    setReviewNote("");
    setClassification("");
  };

  const handleClassifyCase = async () => {
    if (!classification) {
      onShowSnackbar?.("Please select a classification", "warning");
      return;
    }

    try {
      await auditAPI.classifyFlaggedItem(selectedCase.id, {
        classification,
        notes: reviewNote,
      });
      onShowSnackbar?.("Case classified successfully", "success");
      handleCloseDialog();
      loadMyCases(); // Reload cases
    } catch (error) {
      console.error("Error classifying case:", error);
      onShowSnackbar?.("Failed to classify case", "error");
    }
  };

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

  const renderOriginalData = () => {
    if (!selectedCase?.original_data) {
      return <Typography color="text.secondary">No data available</Typography>;
    }

    // If original_data is a string (JSON), parse it
    let data = selectedCase.original_data;
    if (typeof data === "string") {
      try {
        data = JSON.parse(data);
      } catch (e) {
        // Keep as string if parsing fails
      }
    }

    // If we have parsed JSON, format it nicely
    if (typeof data === "object" && data !== null) {
      return (
        <Box>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: "bold", color: "#1976d2" }}>
            Original {selectedCase.type?.toUpperCase()} Data
          </Typography>
          <Paper
            sx={{
              p: 2,
              backgroundColor: "#f5f5f5",
              borderRadius: 1,
            }}
          >
            <Grid container spacing={2}>
              {Object.entries(data).map(([key, value]) => (
                <Grid item xs={12} sm={6} key={key}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: "block", mb: 0.5 }}>
                    {key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: "medium" }}>
                    {typeof value === "object" ? JSON.stringify(value, null, 2) : String(value)}
                  </Typography>
                </Grid>
              ))}
            </Grid>
          </Paper>
          
          {/* Raw JSON view toggle */}
          <Button 
            size="small" 
            onClick={() => setShowRawJson(!showRawJson)}
            sx={{ mt: 2 }}
          >
            {showRawJson ? "Hide" : "Show"} Raw JSON
          </Button>
          
          {showRawJson && (
            <pre
              style={{
                backgroundColor: "#f5f5f5",
                padding: "16px",
                borderRadius: "4px",
                overflow: "auto",
                maxHeight: "400px",
                marginTop: "8px",
              }}
            >
              {JSON.stringify(data, null, 2)}
            </pre>
          )}
        </Box>
      );
    }

    return (
      <Box>
        <pre
          style={{
            backgroundColor: "#f5f5f5",
            padding: "16px",
            borderRadius: "4px",
            overflow: "auto",
            maxHeight: "400px",
          }}
        >
          {JSON.stringify(data, null, 2)}
        </pre>
      </Box>
    );
  };

  const renderEvaluationResults = () => {
    if (!selectedCase) return null;

    console.log("Selected case for evaluation:", selectedCase);
    
    // Get scores from the selected case - try multiple possible field names
    let ruleEngineScore = selectedCase.rule_engine_score ?? selectedCase.ruleEngineScore;
    let mlScore = selectedCase.ml_score ?? selectedCase.mlScore;
    let anomalyScore = selectedCase.anomaly_score ?? selectedCase.anomalyScore;
    const overallRiskScore = selectedCase.risk_score ?? selectedCase.riskScore;
    
    // Try to parse scores from details field if not in main fields
    if ((!ruleEngineScore && ruleEngineScore !== 0) || (!mlScore && mlScore !== 0) || (!anomalyScore && anomalyScore !== 0)) {
      try {
        if (selectedCase.details && typeof selectedCase.details === 'string') {
          const detailsObj = JSON.parse(selectedCase.details);
          if (detailsObj.rule_engine_score !== undefined) ruleEngineScore = detailsObj.rule_engine_score;
          if (detailsObj.anomaly_score !== undefined) anomalyScore = detailsObj.anomaly_score;
          if (detailsObj.predictive_score !== undefined) mlScore = detailsObj.predictive_score;
          if (detailsObj.ml_score !== undefined) mlScore = detailsObj.ml_score;
        }
      } catch (e) {
        console.error("Could not parse details field:", e);
      }
    }
    
    console.log("Scores found:", { ruleEngineScore, mlScore, anomalyScore, overallRiskScore });

    return (
      <Box>
        <Typography variant="h6" sx={{ mb: 3, fontWeight: "bold" }}>
          Engine Evaluation Results
        </Typography>
        
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {/* Overall Risk Score */}
          <Grid item xs={12}>
            <Card sx={{ backgroundColor: "#f5f5f5" }}>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <Box>
                    <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                      Overall Risk Score
                    </Typography>
                    <Typography variant="h2" sx={{ fontWeight: "bold", color: 
                      overallRiskScore >= 80 ? "#d32f2f" : 
                      overallRiskScore >= 60 ? "#f57c00" : 
                      "#1976d2" 
                    }}>
                      {overallRiskScore?.toFixed(1) || "N/A"}
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: "right" }}>
                    <Typography variant="body2" color="text.secondary">
                      {overallRiskScore >= 80 ? "🔴 Critical Risk" : 
                       overallRiskScore >= 60 ? "🟠 High Risk" : 
                       overallRiskScore >= 40 ? "🟡 Medium Risk" : "🟢 Low Risk"}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Rule Engine Score */}
          <Grid item xs={12} md={4}>
            <Card sx={{ height: "100%", borderLeft: "4px solid #1976d2" }}>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <CheckCircleIcon sx={{ mr: 1, color: "#1976d2" }} />
                  <Typography variant="h6">Rule Engine</Typography>
                </Box>
                <Divider sx={{ mb: 2 }} />
                {(ruleEngineScore !== null && ruleEngineScore !== undefined && !isNaN(ruleEngineScore)) ? (
                  <>
                    <Typography variant="h3" sx={{ color: "#1976d2", mb: 1 }}>
                      {ruleEngineScore.toFixed(1)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Rules matched and violated
                    </Typography>
                    <Alert severity={ruleEngineScore >= 90 ? "error" : ruleEngineScore >= 70 ? "warning" : "info"} sx={{ mt: 2 }}>
                      {ruleEngineScore >= 90 ? "Multiple high-severity rules triggered" :
                       ruleEngineScore >= 70 ? "Several suspicious patterns detected" :
                       "Minor anomalies detected"}
                    </Alert>
                  </>
                ) : (
                  <Typography color="text.secondary">
                    No rule engine evaluation available
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Anomaly Detection Score */}
          <Grid item xs={12} md={4}>
            <Card sx={{ height: "100%", borderLeft: "4px solid #f57c00" }}>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <WarningIcon sx={{ mr: 1, color: "#f57c00" }} />
                  <Typography variant="h6">Anomaly Detection</Typography>
                </Box>
                <Divider sx={{ mb: 2 }} />
                {(anomalyScore !== null && anomalyScore !== undefined && !isNaN(anomalyScore)) ? (
                  <>
                    <Typography variant="h3" sx={{ color: "#f57c00", mb: 1 }}>
                      {anomalyScore.toFixed(1)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Behavioral anomaly score
                    </Typography>
                    <Alert severity={anomalyScore >= 90 ? "error" : anomalyScore >= 70 ? "warning" : "info"} sx={{ mt: 2 }}>
                      {anomalyScore >= 90 ? "Highly unusual behavior patterns" :
                       anomalyScore >= 70 ? "Significant behavioral deviations" :
                       "Normal behavioral patterns"}
                    </Alert>
                  </>
                ) : (
                  <Typography color="text.secondary">
                    No anomaly detection evaluation available
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* ML Model Score */}
          <Grid item xs={12} md={4}>
            <Card sx={{ height: "100%", borderLeft: "4px solid #d32f2f" }}>
              <CardContent>
                <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                  <CancelIcon sx={{ mr: 1, color: "#d32f2f" }} />
                  <Typography variant="h6">ML Prediction</Typography>
                </Box>
                <Divider sx={{ mb: 2 }} />
                {(mlScore !== null && mlScore !== undefined && !isNaN(mlScore)) ? (
                  <>
                    <Typography variant="h3" sx={{ color: "#d32f2f", mb: 1 }}>
                      {mlScore.toFixed(1)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Machine learning fraud probability
                    </Typography>
                    <Alert severity={mlScore >= 90 ? "error" : mlScore >= 70 ? "warning" : "info"} sx={{ mt: 2 }}>
                      {mlScore >= 90 ? "High fraud probability detected" :
                       mlScore >= 70 ? "Moderate fraud risk" :
                       "Low fraud probability"}
                    </Alert>
                  </>
                ) : (
                  <Typography color="text.secondary">
                    No ML model evaluation available
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Details Field (if contains additional info) */}
        {selectedCase.details && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: "bold" }}>
                Additional Evaluation Details
              </Typography>
              <Typography variant="body2" component="pre" sx={{ 
                backgroundColor: "#f5f5f5", 
                p: 2, 
                borderRadius: 1,
                fontSize: "0.875rem",
                overflow: "auto",
                maxHeight: 200,
              }}>
                {typeof selectedCase.details === "string" 
                  ? selectedCase.details 
                  : JSON.stringify(selectedCase.details, null, 2)}
              </Typography>
            </CardContent>
          </Card>
        )}

        {/* Decision Aggregation Breakdown */}
        {selectedCase.breakdown && (
          <Card sx={{ mt: 3, borderLeft: "4px solid #ff9800" }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
                <CalculateIcon sx={{ mr: 1, color: "#ff9800" }} />
                <Typography variant="h6">Score Aggregation</Typography>
              </Box>
              <Divider sx={{ mb: 3 }} />
              
              <Grid container spacing={3}>
                {/* Rule Engine Breakdown */}
                <Grid item xs={12} md={4}>
                  <Card variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Rule Engine
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 1 }}>
                      {(selectedCase.breakdown.rule_engine?.score * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Weight: {selectedCase.breakdown.rule_engine?.weight}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Contribution: {selectedCase.breakdown.rule_engine?.contribution.toFixed(2)}
                    </Typography>
                  </Card>
                </Grid>

                {/* Anomaly Detection Breakdown */}
                <Grid item xs={12} md={4}>
                  <Card variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Anomaly Detection
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 1 }}>
                      {(selectedCase.breakdown.anomaly_detection?.score * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Weight: {selectedCase.breakdown.anomaly_detection?.weight}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Contribution: {selectedCase.breakdown.anomaly_detection?.contribution.toFixed(2)}
                    </Typography>
                  </Card>
                </Grid>

                {/* Predictive Engine Breakdown */}
                <Grid item xs={12} md={4}>
                  <Card variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      Predictive Engine
                    </Typography>
                    <Typography variant="h5" sx={{ mb: 1 }}>
                      {(selectedCase.breakdown.predictive_engine?.score * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Weight: {selectedCase.breakdown.predictive_engine?.weight}%
                    </Typography>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Contribution: {selectedCase.breakdown.predictive_engine?.contribution.toFixed(2)}
                    </Typography>
                  </Card>
                </Grid>
              </Grid>

              <Box sx={{ mt: 3, p: 2, bgcolor: "grey.100", borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  <strong>Final Score:</strong> {selectedCase.final_score_percent ? (selectedCase.final_score_percent).toFixed(2) : (selectedCase.risk_score * 100).toFixed(2)}%
                </Typography>
                {selectedCase.confidence && (
                  <Typography variant="body2" color="text.secondary">
                    <strong>Confidence:</strong> {(selectedCase.confidence * 100).toFixed(1)}%
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        )}

        {/* Reason for Flagging */}
        {selectedCase.reason && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: "bold" }}>
                Reason for Flagging
              </Typography>
              <Alert severity="warning" sx={{ mb: 1 }}>
                <Typography variant="body1">
                  {selectedCase.reason}
                </Typography>
              </Alert>
            </CardContent>
          </Card>
        )}
      </Box>
    );
  };

  const renderAuditTrail = () => {
    if (!selectedCase?.audit_trail || selectedCase.audit_trail.length === 0) {
      return (
        <Typography color="text.secondary">No audit trail available</Typography>
      );
    }

    return (
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Action</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Timestamp</TableCell>
              <TableCell>Details</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {selectedCase.audit_trail.map((entry, index) => (
              <TableRow key={index}>
                <TableCell>
                  <Chip label={entry.action} size="small" />
                </TableCell>
                <TableCell>{entry.user_id}</TableCell>
                <TableCell>
                  {new Date(entry.timestamp).toLocaleString()}
                </TableCell>
                <TableCell>
                  {entry.old_status && entry.new_status
                    ? `${entry.old_status} → ${entry.new_status}`
                    : "-"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
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

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography
          variant="h4"
          sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
        >
          My Assigned Cases
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Review and classify cases assigned to you with detailed evaluation
          results
        </Typography>
      </Box>

      {/* Cases Table */}
      <Paper sx={{ borderRadius: 2, boxShadow: 2 }}>
        {cases.length === 0 ? (
          <Box sx={{ p: 4, textAlign: "center" }}>
            <Typography variant="h6" color="text.secondary">
              No cases assigned yet
            </Typography>
            <Typography variant="body2" color="text.secondary">
              You're all caught up! Check back later for new assignments.
            </Typography>
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: "bold" }}>Case ID</TableCell>
                  <TableCell sx={{ fontWeight: "bold" }}>Data Type</TableCell>
                  <TableCell sx={{ fontWeight: "bold" }}>Priority</TableCell>
                  <TableCell sx={{ fontWeight: "bold" }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: "bold" }}>Assigned</TableCell>
                  <TableCell sx={{ fontWeight: "bold" }}>Due Date</TableCell>
                  <TableCell sx={{ fontWeight: "bold" }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {cases.map((caseItem) => (
                  <TableRow key={caseItem.id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
                        {caseItem.flagged_item_id?.substring(0, 8)}...
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={caseItem.item_type || "N/A"}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={caseItem.priority || "Medium"}
                        size="small"
                        color={getPriorityColor(caseItem.priority)}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={caseItem.status || "Assigned"}
                        size="small"
                        color={getStatusColor(caseItem.status)}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {caseItem.assigned_at
                          ? new Date(caseItem.assigned_at).toLocaleDateString()
                          : "N/A"}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {caseItem.due_date
                          ? new Date(caseItem.due_date).toLocaleDateString()
                          : "No deadline"}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        color="primary"
                        onClick={() => handleViewDetails(caseItem)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {/* Pagination */}
            {cases.length > 0 && (
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "center",
                  borderTop: "1px solid #e0e0e0",
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 2, p: 2 }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                    }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      Showing {page * limit + 1}-
                      {Math.min((page + 1) * limit, total)} of {total} cases
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      |
                    </Typography>
                    <Typography variant="body2">
                      Page {page + 1} of {Math.ceil(total / limit) || 1}
                    </Typography>
                  </Box>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      disabled={page === 0}
                      onClick={() => setPage(page - 1)}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      disabled={(page + 1) * limit >= total}
                      onClick={() => setPage(page + 1)}
                    >
                      Next
                    </Button>
                  </Box>
                </Box>
              </Box>
            )}
          </TableContainer>
        )}
      </Paper>

      {/* Case Detail Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Typography variant="h6">Case Details</Typography>
            <IconButton onClick={handleCloseDialog}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {selectedCase && (
            <Box>
              {/* Case Information */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Case ID
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{ fontFamily: "monospace", mb: 2 }}
                  >
                    {selectedCase.id}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Data Type
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {selectedCase.type || "N/A"}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Risk Score
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 2 }}>
                    {selectedCase.risk_score?.toFixed(2) || "N/A"}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={selectedCase.status || "Pending"}
                      size="small"
                      color={getStatusColor(selectedCase.status)}
                    />
                  </Box>
                </Grid>
              </Grid>

              <Divider sx={{ my: 3 }} />

              {/* Tabs for Different Sections */}
              <Tabs
                value={selectedTab}
                onChange={(e, newValue) => setSelectedTab(newValue)}
                sx={{ mb: 3 }}
              >
                <Tab label="Submitted Data" />
                <Tab label="Evaluation Results" />
                <Tab label="Audit Trail" />
                <Tab label="Review & Classify" />
              </Tabs>

              {/* Tab Content */}
              <Box>
                {selectedTab === 0 && renderOriginalData()}
                {selectedTab === 1 && renderEvaluationResults()}
                {selectedTab === 2 && renderAuditTrail()}
                {selectedTab === 3 && (
                  <Box>
                    <Alert severity="info" sx={{ mb: 3 }}>
                      Review the case details and classify it as confirmed fraud
                      or false positive
                    </Alert>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Typography
                          variant="subtitle2"
                          sx={{ mb: 1, fontWeight: "bold" }}
                        >
                          Classification
                        </Typography>
                        <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
                          <Button
                            variant={
                              classification === "confirmed"
                                ? "contained"
                                : "outlined"
                            }
                            color="error"
                            onClick={() => setClassification("confirmed")}
                          >
                            Confirmed Fraud
                          </Button>
                          <Button
                            variant={
                              classification === "false_positive"
                                ? "contained"
                                : "outlined"
                            }
                            color="success"
                            onClick={() => setClassification("false_positive")}
                          >
                            False Positive
                          </Button>
                        </Box>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography
                          variant="subtitle2"
                          sx={{ mb: 1, fontWeight: "bold" }}
                        >
                          Review Notes
                        </Typography>
                        <TextField
                          fullWidth
                          multiline
                          rows={4}
                          placeholder="Add your review notes here..."
                          value={reviewNote}
                          onChange={(e) => setReviewNote(e.target.value)}
                        />
                      </Grid>
                    </Grid>
                  </Box>
                )}
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
          {selectedTab === 3 && (
            <Button
              variant="contained"
              onClick={handleClassifyCase}
              disabled={!classification}
            >
              Submit Classification
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MyCasesPage;

