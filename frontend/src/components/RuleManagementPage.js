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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Tooltip,
  Avatar,
  Divider,
  Menu,
  ListItemIcon,
  ListItemText,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as ActivateIcon,
  Pause as DeactivateIcon,
  History as HistoryIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  MoreVert as MoreVertIcon,
  Code as CodeIcon,
  CheckCircle as ActiveIcon,
  Cancel as InactiveIcon,
  BugReport as TestIcon,
} from "@mui/icons-material";
import { ruleEngineAPI } from "../services/api";
import RuleEditorDialog from "./RuleEditorDialog";
import RuleTestPanel from "./RuleTestPanel";
import RuleVersionHistoryDialog from "./RuleVersionHistoryDialog";

const RuleManagementPage = ({ onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [rules, setRules] = useState([]);
  const [dataTypes, setDataTypes] = useState([]);
  const [filters, setFilters] = useState({
    dataType: "",
    status: "",
    search: "",
  });
  const [selectedRule, setSelectedRule] = useState(null);
  const [editorDialogOpen, setEditorDialogOpen] = useState(false);
  const [testPanelOpen, setTestPanelOpen] = useState(false);
  const [versionDialogOpen, setVersionDialogOpen] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState(null);

  // Load data types on component mount
  useEffect(() => {
    const loadDataTypes = async () => {
      try {
        const response = await ruleEngineAPI.getAllDataTypes();
        setDataTypes(response.data || []);
      } catch (error) {
        console.error("Failed to load data types:", error);
      }
    };
    loadDataTypes();
  }, []);

  // Load rules on component mount
  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    setLoading(true);
    try {
      const response = await ruleEngineAPI.getAllRules({
        limit: 100,
        offset: 0,
        dataType: filters.dataType || undefined,
        status: filters.status || undefined,
        search: filters.search || undefined,
      });
      // The API returns {content: [...], totalElements: n}
      setRules(response.data.content || []);
    } catch (error) {
      onShowSnackbar("Failed to load rules: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
  };

  const handleSearch = () => {
    loadRules();
  };

  const handleCreateRule = () => {
    setSelectedRule(null);
    setEditorDialogOpen(true);
  };

  const handleEditRule = (rule) => {
    setSelectedRule(rule);
    setEditorDialogOpen(true);
  };

  const handleTestRule = (rule) => {
    setSelectedRule(rule);
    setTestPanelOpen(true);
  };

  const handleViewVersions = (rule) => {
    setSelectedRule(rule);
    setVersionDialogOpen(true);
  };

  const handleActivateRule = async (rule) => {
    try {
      setLoading(true);
      await ruleEngineAPI.activateRule(rule.id);
      onShowSnackbar("Rule activated successfully", "success");
      loadRules();
    } catch (error) {
      onShowSnackbar("Failed to activate rule: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivateRule = async (rule) => {
    try {
      setLoading(true);
      await ruleEngineAPI.deactivateRule(rule.id);
      onShowSnackbar("Rule deactivated successfully", "success");
      loadRules();
    } catch (error) {
      onShowSnackbar("Failed to deactivate rule: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRule = async (rule) => {
    if (window.confirm(`Are you sure you want to delete "${rule.name}"?`)) {
      try {
        setLoading(true);
        await ruleEngineAPI.deleteRule(rule.id);
        onShowSnackbar("Rule deleted successfully", "success");
        loadRules();
      } catch (error) {
        onShowSnackbar("Failed to delete rule: " + error.message, "error");
      } finally {
        setLoading(false);
      }
    }
  };

  const handleMenuClick = (event, rule) => {
    setMenuAnchor(event.currentTarget);
    setSelectedRule(rule);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedRule(null);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "ACTIVE":
        return "success";
      case "DRAFT":
        return "warning";
      case "INACTIVE":
        return "error";
      default:
        return "default";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "ACTIVE":
        return <ActiveIcon />;
      case "DRAFT":
        return <EditIcon />;
      case "INACTIVE":
        return <InactiveIcon />;
      default:
        return <CodeIcon />;
    }
  };

  const getDataTypeColor = (dataType) => {
    switch (dataType) {
      case "TRANSACTION":
        return "primary";
      case "KYC":
        return "secondary";
      case "LOAN":
        return "success";
      case "CREDIT":
        return "warning";
      case "REPAYMENT":
        return "info";
      default:
        return "default";
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Unknown";
    return new Date(dateString).toLocaleDateString();
  };

  if (loading && rules.length === 0) {
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
          Rule Management
        </Typography>
        <Typography variant='body1' color='text.secondary'>
          Create and manage fraud detection rules dynamically.
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <CodeIcon sx={{ fontSize: 24, color: "#1976d2", mr: 1 }} />
                <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                  Total Rules
                </Typography>
              </Box>
              <Typography
                variant='h4'
                sx={{ fontWeight: "bold", color: "#1976d2" }}
              >
                {rules.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <ActiveIcon sx={{ fontSize: 24, color: "#4caf50", mr: 1 }} />
                <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                  Active Rules
                </Typography>
              </Box>
              <Typography
                variant='h4'
                sx={{ fontWeight: "bold", color: "#4caf50" }}
              >
                {rules.filter((r) => r.status === "ACTIVE").length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <EditIcon sx={{ fontSize: 24, color: "#ff9800", mr: 1 }} />
                <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                  Draft Rules
                </Typography>
              </Box>
              <Typography
                variant='h4'
                sx={{ fontWeight: "bold", color: "#ff9800" }}
              >
                {rules.filter((r) => r.status === "DRAFT").length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ borderRadius: 2, boxShadow: 1 }}>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <TestIcon sx={{ fontSize: 24, color: "#9c27b0", mr: 1 }} />
                <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                  Data Types
                </Typography>
              </Box>
              <Typography
                variant='h4'
                sx={{ fontWeight: "bold", color: "#9c27b0" }}
              >
                {new Set(rules.map((r) => r.dataType)).size}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters and Actions */}
      <Paper sx={{ borderRadius: 2, boxShadow: 1, mb: 3, p: 3 }}>
        <Box
          sx={{
            display: "flex",
            gap: 2,
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Data Type</InputLabel>
            <Select
              value={filters.dataType}
              onChange={(e) => handleFilterChange("dataType", e.target.value)}
              label='Data Type'
            >
              <MenuItem value=''>All Types</MenuItem>
              {dataTypes.filter(dt => dt.status === 'ACTIVE').map((dt) => (
                <MenuItem key={dt.id} value={dt.dataType}>
                  {dt.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filters.status}
              onChange={(e) => handleFilterChange("status", e.target.value)}
              label='Status'
            >
              <MenuItem value=''>All Status</MenuItem>
              <MenuItem value='ACTIVE'>Active</MenuItem>
              <MenuItem value='DRAFT'>Draft</MenuItem>
              <MenuItem value='INACTIVE'>Inactive</MenuItem>
            </Select>
          </FormControl>

          <TextField
            placeholder='Search rules...'
            value={filters.search}
            onChange={(e) => handleFilterChange("search", e.target.value)}
            sx={{ flexGrow: 1, maxWidth: 300 }}
            InputProps={{
              startAdornment: (
                <SearchIcon sx={{ mr: 1, color: "text.secondary" }} />
              ),
            }}
          />

          <Button
            variant='outlined'
            startIcon={<RefreshIcon />}
            onClick={loadRules}
            disabled={loading}
          >
            Refresh
          </Button>

          <Button
            variant='contained'
            startIcon={<AddIcon />}
            onClick={handleCreateRule}
            sx={{ bgcolor: "#ff9800", "&:hover": { bgcolor: "#f57c00" } }}
          >
            New Rule
          </Button>
        </Box>
      </Paper>

      {/* Rules List */}
      <Paper sx={{ borderRadius: 2, boxShadow: 1 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Rule Name</TableCell>
                <TableCell>Data Type</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rules.map((rule) => (
                <TableRow key={rule.id} hover>
                  <TableCell>
                    <Box sx={{ display: "flex", alignItems: "center" }}>
                      <Avatar
                        sx={{
                          width: 32,
                          height: 32,
                          mr: 2,
                          bgcolor: "#ff9800",
                        }}
                      >
                        <CodeIcon sx={{ fontSize: 16 }} />
                      </Avatar>
                      <Box>
                        <Typography variant='body1' sx={{ fontWeight: "bold" }}>
                          {rule.name}
                        </Typography>
                        <Typography variant='caption' color='text.secondary'>
                          {rule.description || "No description"}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={rule.dataType}
                      size='small'
                      color={getDataTypeColor(rule.dataType)}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      icon={getStatusIcon(rule.status)}
                      label={rule.status}
                      size='small'
                      color={getStatusColor(rule.status)}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2' fontFamily='monospace'>
                      v{rule.version}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant='body2' color='text.secondary'>
                      {formatDate(rule.updatedAt)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: "flex", gap: 0.5 }}>
                      <Tooltip title='Edit Rule'>
                        <IconButton
                          size='small'
                          onClick={() => handleEditRule(rule)}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title='Test Rule'>
                        <IconButton
                          size='small'
                          onClick={() => handleTestRule(rule)}
                        >
                          <TestIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title='View Versions'>
                        <IconButton
                          size='small'
                          onClick={() => handleViewVersions(rule)}
                        >
                          <HistoryIcon />
                        </IconButton>
                      </Tooltip>
                      {rule.status === "ACTIVE" ? (
                        <Tooltip title='Deactivate'>
                          <IconButton
                            size='small'
                            onClick={() => handleDeactivateRule(rule)}
                            color='warning'
                          >
                            <DeactivateIcon />
                          </IconButton>
                        </Tooltip>
                      ) : (
                        <Tooltip title='Activate'>
                          <IconButton
                            size='small'
                            onClick={() => handleActivateRule(rule)}
                            color='success'
                          >
                            <ActivateIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title='More Actions'>
                        <IconButton
                          size='small'
                          onClick={(e) => handleMenuClick(e, rule)}
                        >
                          <MoreVertIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Action Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        transformOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
      >
        <MenuItem onClick={() => handleDeleteRule(selectedRule)}>
          <ListItemIcon>
            <DeleteIcon color='error' />
          </ListItemIcon>
          <ListItemText>Delete Rule</ListItemText>
        </MenuItem>
      </Menu>

      {/* Dialogs */}
      <RuleEditorDialog
        open={editorDialogOpen}
        rule={selectedRule}
        onClose={() => setEditorDialogOpen(false)}
        onSave={() => {
          setEditorDialogOpen(false);
          loadRules();
        }}
        onShowSnackbar={onShowSnackbar}
      />

      <RuleTestPanel
        open={testPanelOpen}
        rule={selectedRule}
        onClose={() => setTestPanelOpen(false)}
        onShowSnackbar={onShowSnackbar}
      />

      <RuleVersionHistoryDialog
        open={versionDialogOpen}
        rule={selectedRule}
        onClose={() => setVersionDialogOpen(false)}
        onShowSnackbar={onShowSnackbar}
      />
    </Box>
  );
};

export default RuleManagementPage;
