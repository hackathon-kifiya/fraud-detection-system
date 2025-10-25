import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Tabs,
  Tab,
  Checkbox,
  Tooltip,
  Avatar,
  Divider,
} from "@mui/material";
import {
  Assignment as AssignmentIcon,
  Person as PersonIcon,
  Cancel as CancelIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  AssignmentTurnedIn as CompletedIcon,
  AssignmentLate as PendingIcon,
  AssignmentReturned as InProgressIcon,
} from "@mui/icons-material";
import { adminAPI } from "../services/api";

const CaseManagementPage = ({ onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [assignments, setAssignments] = useState([]);
  const [unassignedCases, setUnassignedCases] = useState([]);
  const [auditors, setAuditors] = useState([]);
  const [workload, setWorkload] = useState([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedCases, setSelectedCases] = useState([]);
  const [assignmentDialog, setAssignmentDialog] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState(null);
  const [assignmentForm, setAssignmentForm] = useState({
    auditor_id: "",
    priority: "medium",
    due_date: "",
    notes: "",
  });

  // Load data on component mount
  useEffect(() => {
    loadData();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadAssignments(),
        loadUnassignedCases(),
        loadAuditors(),
        loadWorkload(),
      ]);
    } catch (error) {
      onShowSnackbar("Failed to load data: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const loadAssignments = async () => {
    try {
      const response = await adminAPI.getCaseAssignments({
        limit: 100,
        offset: 0,
      });
      setAssignments(response.data.assignments || []);
    } catch (error) {
      console.error("Failed to load assignments:", error);
    }
  };

  const loadUnassignedCases = async () => {
    try {
      const response = await adminAPI.getUnassignedCases({
        limit: 100,
        offset: 0,
      });
      setUnassignedCases(response.data.cases || []);
    } catch (error) {
      console.error("Failed to load unassigned cases:", error);
    }
  };

  const loadAuditors = async () => {
    try {
      const response = await adminAPI.getUsers({ role: "analyst", limit: 100 });
      setAuditors(response.data.users || []);
    } catch (error) {
      console.error("Failed to load auditors:", error);
    }
  };

  const loadWorkload = async () => {
    try {
      const response = await adminAPI.getAuditorWorkload();
      setWorkload(response.data.workload || []);
    } catch (error) {
      console.error("Failed to load workload:", error);
    }
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const handleCaseSelect = (caseId) => {
    setSelectedCases((prev) =>
      prev.includes(caseId)
        ? prev.filter((id) => id !== caseId)
        : [...prev, caseId]
    );
  };

  const handleSelectAll = () => {
    if (selectedCases.length === unassignedCases.length) {
      setSelectedCases([]);
    } else {
      setSelectedCases(unassignedCases.map((case_) => case_.id));
    }
  };

  const handleAssignCases = () => {
    if (selectedCases.length === 0) {
      onShowSnackbar("Please select at least one case", "warning");
      return;
    }
    setAssignmentDialog(true);
  };

  const handleEditAssignment = (assignment) => {
    setEditingAssignment(assignment);
    setAssignmentForm({
      auditor_id: assignment.auditor_id,
      priority: assignment.priority,
      due_date: assignment.due_date ? assignment.due_date.split("T")[0] : "",
      notes: assignment.notes || "",
    });
    setAssignmentDialog(true);
  };

  const handleAssignmentSubmit = async () => {
    try {
      setLoading(true);

      if (editingAssignment) {
        // Update existing assignment
        await adminAPI.updateCaseAssignment(editingAssignment.id, {
          status: editingAssignment.status,
          priority: assignmentForm.priority,
          due_date: assignmentForm.due_date
            ? new Date(assignmentForm.due_date).toISOString()
            : null,
          notes: assignmentForm.notes,
        });
        onShowSnackbar("Assignment updated successfully", "success");
      } else {
        // Create new assignment(s)
        if (selectedCases.length === 1) {
          await adminAPI.assignCase({
            flagged_item_id: selectedCases[0],
            auditor_id: assignmentForm.auditor_id,
            priority: assignmentForm.priority,
            due_date: assignmentForm.due_date
              ? new Date(assignmentForm.due_date).toISOString()
              : null,
            notes: assignmentForm.notes,
          });
        } else {
          await adminAPI.bulkAssignCases({
            flagged_item_ids: selectedCases,
            auditor_id: assignmentForm.auditor_id,
            priority: assignmentForm.priority,
            due_date: assignmentForm.due_date
              ? new Date(assignmentForm.due_date).toISOString()
              : null,
            notes: assignmentForm.notes,
          });
        }
        onShowSnackbar(
          `Successfully assigned ${selectedCases.length} case(s)`,
          "success"
        );
      }

      setAssignmentDialog(false);
      setEditingAssignment(null);
      setAssignmentForm({
        auditor_id: "",
        priority: "medium",
        due_date: "",
        notes: "",
      });
      setSelectedCases([]);
      loadData();
    } catch (error) {
      onShowSnackbar("Failed to assign cases: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveAssignment = async (assignmentId) => {
    if (window.confirm("Are you sure you want to remove this assignment?")) {
      try {
        setLoading(true);
        await adminAPI.deleteCaseAssignment(assignmentId);
        onShowSnackbar("Assignment removed successfully", "success");
        loadData();
      } catch (error) {
        onShowSnackbar(
          "Failed to remove assignment: " + error.message,
          "error"
        );
      } finally {
        setLoading(false);
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "assigned":
        return "warning";
      case "in_progress":
        return "info";
      case "completed":
        return "success";
      case "cancelled":
        return "error";
      default:
        return "default";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "assigned":
        return <PendingIcon />;
      case "in_progress":
        return <InProgressIcon />;
      case "completed":
        return <CompletedIcon />;
      case "cancelled":
        return <CancelIcon />;
      default:
        return <AssignmentIcon />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "low":
        return "success";
      case "medium":
        return "warning";
      case "high":
        return "error";
      case "urgent":
        return "error";
      default:
        return "default";
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "No due date";
    return new Date(dateString).toLocaleDateString();
  };

  const getAuditorName = (auditorId) => {
    const auditor = auditors.find((a) => a.id === auditorId);
    return auditor ? `${auditor.first_name} ${auditor.last_name}` : "Unknown";
  };

  if (loading && assignments.length === 0) {
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
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography
          variant='h4'
          sx={{ fontWeight: "bold", color: "#424242", mb: 1 }}
        >
          Case Management
        </Typography>
        <Typography variant='body1' color='text.secondary'>
          Assign and manage fraud detection cases for auditor review.
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <AssignmentIcon
                  sx={{ fontSize: 24, color: "#1976d2", mr: 1 }}
                />
                <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                  Total Assignments
                </Typography>
              </Box>
              <Typography
                variant='h4'
                sx={{ fontWeight: "bold", color: "#1976d2" }}
              >
                {assignments.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <PendingIcon sx={{ fontSize: 24, color: "#ff9800", mr: 1 }} />
                <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                  Unassigned Cases
                </Typography>
              </Box>
              <Typography
                variant='h4'
                sx={{ fontWeight: "bold", color: "#ff9800" }}
              >
                {unassignedCases.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <CompletedIcon sx={{ fontSize: 24, color: "#4caf50", mr: 1 }} />
                <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                  Completed
                </Typography>
              </Box>
              <Typography
                variant='h4'
                sx={{ fontWeight: "bold", color: "#4caf50" }}
              >
                {assignments.filter((a) => a.status === "completed").length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <PersonIcon sx={{ fontSize: 24, color: "#9c27b0", mr: 1 }} />
                <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                  Active Auditors
                </Typography>
              </Box>
              <Typography
                variant='h4'
                sx={{ fontWeight: "bold", color: "#9c27b0" }}
              >
                {auditors.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ borderRadius: 2, boxShadow: 1, mb: 3 }}>
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: "divider" }}
        >
          <Tab label='Unassigned Cases' />
          <Tab label='All Assignments' />
          <Tab label='Auditor Workload' />
        </Tabs>

        {/* Unassigned Cases Tab */}
        {selectedTab === 0 && (
          <Box sx={{ p: 3 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                Unassigned Cases ({unassignedCases.length})
              </Typography>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Button
                  variant='outlined'
                  startIcon={<RefreshIcon />}
                  onClick={loadData}
                  disabled={loading}
                >
                  Refresh
                </Button>
                <Button
                  variant='contained'
                  startIcon={<AddIcon />}
                  onClick={handleAssignCases}
                  disabled={selectedCases.length === 0}
                  sx={{ bgcolor: "#ff9800", "&:hover": { bgcolor: "#f57c00" } }}
                >
                  Assign Selected ({selectedCases.length})
                </Button>
              </Box>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell padding='checkbox'>
                      <Checkbox
                        checked={
                          selectedCases.length === unassignedCases.length &&
                          unassignedCases.length > 0
                        }
                        indeterminate={
                          selectedCases.length > 0 &&
                          selectedCases.length < unassignedCases.length
                        }
                        onChange={handleSelectAll}
                      />
                    </TableCell>
                    <TableCell>Case ID</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Risk Score</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {unassignedCases.map((case_) => (
                    <TableRow key={case_.id} hover>
                      <TableCell padding='checkbox'>
                        <Checkbox
                          checked={selectedCases.includes(case_.id)}
                          onChange={() => handleCaseSelect(case_.id)}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant='body2' fontFamily='monospace'>
                          {case_.id.substring(0, 8)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={
                            case_.item_type?.replace("_", " ").toUpperCase() ||
                            "Unknown"
                          }
                          size='small'
                          color='primary'
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${case_.risk_score?.toFixed(1) || "N/A"}`}
                          size='small'
                          color={
                            case_.risk_score >= 85
                              ? "error"
                              : case_.risk_score >= 70
                              ? "warning"
                              : "success"
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant='body2' color='text.secondary'>
                          {formatDate(case_.created_at)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title='Assign Case'>
                          <IconButton
                            size='small'
                            onClick={() => {
                              setSelectedCases([case_.id]);
                              setAssignmentDialog(true);
                            }}
                          >
                            <AssignmentIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* All Assignments Tab */}
        {selectedTab === 1 && (
          <Box sx={{ p: 3 }}>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                All Assignments ({assignments.length})
              </Typography>
              <Button
                variant='outlined'
                startIcon={<RefreshIcon />}
                onClick={loadData}
                disabled={loading}
              >
                Refresh
              </Button>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Case ID</TableCell>
                    <TableCell>Auditor</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Due Date</TableCell>
                    <TableCell>Assigned</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {assignments.map((assignment) => (
                    <TableRow key={assignment.id} hover>
                      <TableCell>
                        <Typography variant='body2' fontFamily='monospace'>
                          {assignment.flagged_item_id?.substring(0, 8)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: "flex", alignItems: "center" }}>
                          <Avatar
                            sx={{
                              width: 24,
                              height: 24,
                              mr: 1,
                              bgcolor: "#ff9800",
                            }}
                          >
                            <PersonIcon sx={{ fontSize: 16 }} />
                          </Avatar>
                          <Typography variant='body2'>
                            {getAuditorName(assignment.auditor_id)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getStatusIcon(assignment.status)}
                          label={assignment.status
                            ?.replace("_", " ")
                            .toUpperCase()}
                          size='small'
                          color={getStatusColor(assignment.status)}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={assignment.priority?.toUpperCase()}
                          size='small'
                          color={getPriorityColor(assignment.priority)}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant='body2' color='text.secondary'>
                          {formatDate(assignment.due_date)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant='body2' color='text.secondary'>
                          {formatDate(assignment.assigned_at)}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: "flex", gap: 0.5 }}>
                          <Tooltip title='Edit Assignment'>
                            <IconButton
                              size='small'
                              onClick={() => handleEditAssignment(assignment)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title='Remove Assignment'>
                            <IconButton
                              size='small'
                              onClick={() =>
                                handleRemoveAssignment(assignment.id)
                              }
                              color='error'
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}

        {/* Auditor Workload Tab */}
        {selectedTab === 2 && (
          <Box sx={{ p: 3 }}>
            <Typography variant='h6' sx={{ fontWeight: "bold", mb: 2 }}>
              Auditor Workload Distribution
            </Typography>

            <Grid container spacing={2}>
              {workload.map((auditor) => (
                <Grid item xs={12} sm={6} md={4} key={auditor.auditor_id}>
                  <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
                    <CardContent>
                      <Box
                        sx={{ display: "flex", alignItems: "center", mb: 2 }}
                      >
                        <Avatar
                          sx={{
                            width: 32,
                            height: 32,
                            mr: 2,
                            bgcolor: "#ff9800",
                          }}
                        >
                          <PersonIcon />
                        </Avatar>
                        <Box>
                          <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                            {getAuditorName(auditor.auditor_id)}
                          </Typography>
                          <Chip
                            label={
                              auditor.availability_status?.toUpperCase() ||
                              "UNKNOWN"
                            }
                            size='small'
                            color={
                              auditor.availability_status === "available"
                                ? "success"
                                : "warning"
                            }
                          />
                        </Box>
                      </Box>
                      <Divider sx={{ my: 1 }} />
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant='body2' color='text.secondary'>
                          Active Cases:
                        </Typography>
                        <Typography variant='body2' sx={{ fontWeight: "bold" }}>
                          {auditor.active_assignments}
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant='body2' color='text.secondary'>
                          Completed Today:
                        </Typography>
                        <Typography variant='body2' sx={{ fontWeight: "bold" }}>
                          {auditor.completed_today}
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant='body2' color='text.secondary'>
                          This Week:
                        </Typography>
                        <Typography variant='body2' sx={{ fontWeight: "bold" }}>
                          {auditor.completed_this_week}
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 1,
                        }}
                      >
                        <Typography variant='body2' color='text.secondary'>
                          Avg. Time:
                        </Typography>
                        <Typography variant='body2' sx={{ fontWeight: "bold" }}>
                          {auditor.average_review_time || "N/A"}
                        </Typography>
                      </Box>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                        }}
                      >
                        <Typography variant='body2' color='text.secondary'>
                          Efficiency:
                        </Typography>
                        <Typography variant='body2' sx={{ fontWeight: "bold" }}>
                          {auditor.efficiency_score?.toFixed(1) || "N/A"}%
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Paper>

      {/* Assignment Dialog */}
      <Dialog
        open={assignmentDialog}
        onClose={() => setAssignmentDialog(false)}
        maxWidth='sm'
        fullWidth
      >
        <DialogTitle>
          {editingAssignment ? "Edit Assignment" : "Assign Cases"}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Auditor</InputLabel>
              <Select
                value={assignmentForm.auditor_id}
                onChange={(e) =>
                  setAssignmentForm({
                    ...assignmentForm,
                    auditor_id: e.target.value,
                  })
                }
                label='Auditor'
              >
                {auditors.map((auditor) => (
                  <MenuItem key={auditor.id} value={auditor.id}>
                    {auditor.first_name} {auditor.last_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={assignmentForm.priority}
                onChange={(e) =>
                  setAssignmentForm({
                    ...assignmentForm,
                    priority: e.target.value,
                  })
                }
                label='Priority'
              >
                <MenuItem value='low'>Low</MenuItem>
                <MenuItem value='medium'>Medium</MenuItem>
                <MenuItem value='high'>High</MenuItem>
                <MenuItem value='urgent'>Urgent</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label='Due Date'
              type='date'
              value={assignmentForm.due_date}
              onChange={(e) =>
                setAssignmentForm({
                  ...assignmentForm,
                  due_date: e.target.value,
                })
              }
              InputLabelProps={{ shrink: true }}
            />

            <TextField
              fullWidth
              label='Notes'
              multiline
              rows={3}
              value={assignmentForm.notes}
              onChange={(e) =>
                setAssignmentForm({ ...assignmentForm, notes: e.target.value })
              }
              placeholder='Optional notes for the auditor...'
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignmentDialog(false)}>Cancel</Button>
          <Button
            onClick={handleAssignmentSubmit}
            variant='contained'
            disabled={!assignmentForm.auditor_id || loading}
            sx={{ bgcolor: "#ff9800", "&:hover": { bgcolor: "#f57c00" } }}
          >
            {loading ? (
              <CircularProgress size={20} />
            ) : editingAssignment ? (
              "Update"
            ) : (
              "Assign"
            )}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CaseManagementPage;
