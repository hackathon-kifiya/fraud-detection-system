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
  CircularProgress,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Snackbar,
} from "@mui/material";
import {
  Add as AddIcon,
  Edit as EditIcon,
  PlayArrow as ActivateIcon,
  Pause as DeactivateIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  CheckCircle as ActiveIcon,
  Cancel as InactiveIcon,
  Code as CodeIcon,
} from "@mui/icons-material";
import { dataTypeAPI } from "../services/api";

const DataTypeManagementPage = ({ onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [dataTypes, setDataTypes] = useState([]);
  const [filteredDataTypes, setFilteredDataTypes] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedDataType, setSelectedDataType] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    displayName: "",
    description: "",
    schemaDefinition: "",
    sampleData: "",
  });

  useEffect(() => {
    loadDataTypes();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = dataTypes.filter(
        (dt) =>
          dt.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          dt.displayName?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredDataTypes(filtered);
    } else {
      setFilteredDataTypes(dataTypes);
    }
  }, [searchTerm, dataTypes]);

  const loadDataTypes = async () => {
    setLoading(true);
    try {
      const response = await dataTypeAPI.getAll({ limit: 100, offset: 0 });
      // Map API response (snake_case) to frontend format (camelCase)
      const mappedData = (response.data || []).map(dt => ({
        id: dt.data_type,
        name: dt.data_type,
        displayName: dt.name,
        description: dt.description,
        status: dt.status,
        schemaDefinition: dt.schema_definition,
        sampleData: dt.sample_data,
        updatedAt: dt.updated_at,
        createdAt: dt.created_at,
      }));
      setDataTypes(mappedData);
      setFilteredDataTypes(mappedData);
    } catch (error) {
      onShowSnackbar("Failed to load data types: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (dataType = null) => {
    setSelectedDataType(dataType);
    if (dataType) {
      setFormData({
        name: dataType.name || "",
        displayName: dataType.displayName || "",
        description: dataType.description || "",
        schemaDefinition: JSON.stringify(dataType.schemaDefinition || {}, null, 2),
        sampleData: JSON.stringify(dataType.sampleData || {}, null, 2),
      });
    } else {
      setFormData({
        name: "",
        displayName: "",
        description: "",
        schemaDefinition: "",
        sampleData: "",
      });
    }
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedDataType(null);
    setFormData({
      name: "",
      displayName: "",
      description: "",
      schemaDefinition: "",
      sampleData: "",
    });
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      
      // Validate sample data is provided for new data types
      if (!selectedDataType && !formData.sampleData.trim()) {
        onShowSnackbar("Sample data is required when creating a new data type", "error");
        setLoading(false);
        return;
      }
      
      if (selectedDataType) {
        // Update payload - only send fields that can be updated
        const payload = {
          name: formData.displayName || formData.name,
          description: formData.description,
          schema_definition: JSON.parse(formData.schemaDefinition || "{}"),
          sample_data: formData.sampleData ? JSON.parse(formData.sampleData) : undefined,
          status: "ACTIVE",
          updated_by: "admin",
        };
        await dataTypeAPI.update(selectedDataType.id, payload);
        onShowSnackbar("Data type updated successfully", "success");
      } else {
        // Create payload - include all required fields including sample_data
        const payload = {
          data_type: formData.name,
          name: formData.displayName || formData.name,
          description: formData.description,
          schema_definition: JSON.parse(formData.schemaDefinition || "{}"),
          sample_data: JSON.parse(formData.sampleData),
          status: "ACTIVE",
          created_by: "admin",
        };
        await dataTypeAPI.create(payload);
        onShowSnackbar("Data type created successfully", "success");
      }
      handleCloseDialog();
      loadDataTypes();
    } catch (error) {
      onShowSnackbar("Failed to save data type: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };


  const handleActivate = async (dataType) => {
    try {
      setLoading(true);
      await dataTypeAPI.update(dataType.id, { status: "ACTIVE", updated_by: "admin" });
      onShowSnackbar("Data type activated successfully", "success");
      loadDataTypes();
    } catch (error) {
      onShowSnackbar("Failed to activate data type: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivate = async (dataType) => {
    try {
      setLoading(true);
      await dataTypeAPI.update(dataType.id, { status: "INACTIVE", updated_by: "admin" });
      onShowSnackbar("Data type deactivated successfully", "success");
      loadDataTypes();
    } catch (error) {
      onShowSnackbar("Failed to deactivate data type: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    return status === "ACTIVE" ? "success" : "error";
  };

  const getStatusIcon = (status) => {
    return status === "ACTIVE" ? <ActiveIcon /> : <InactiveIcon />;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: "bold" }}>
        Data Type Management
      </Typography>
      <Typography variant="body1" sx={{ mb: 3, color: "text.secondary" }}>
        Define and manage data type schemas for rule-based fraud detection.
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <CodeIcon sx={{ fontSize: 40, mr: 2, color: "primary.main" }} />
                <Box>
                  <Typography variant="h4">{dataTypes.length}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Data Types
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <ActiveIcon sx={{ fontSize: 40, mr: 2, color: "success.main" }} />
                <Box>
                  <Typography variant="h4">
                    {dataTypes.filter((dt) => dt.status === "ACTIVE").length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Data Types
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <InactiveIcon sx={{ fontSize: 40, mr: 2, color: "error.main" }} />
                <Box>
                  <Typography variant="h4">
                    {dataTypes.filter((dt) => dt.status === "INACTIVE").length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Inactive Data Types
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center" }}>
                <CodeIcon sx={{ fontSize: 40, mr: 2, color: "info.main" }} />
                <Box>
                  <Typography variant="h4">{filteredDataTypes.length}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Filtered Results
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Bar */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <TextField
            placeholder="Search data types..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1 }} />,
            }}
            sx={{ width: 300 }}
          />
          <Box>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadDataTypes}
              disabled={loading}
              sx={{ mr: 1 }}
            >
              Refresh
            </Button>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => handleOpenDialog()}>
              New Data Type
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Data Types Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Display Name</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Updated</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : filteredDataTypes.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No data types found
                  </TableCell>
                </TableRow>
              ) : (
                filteredDataTypes.map((dataType) => (
                  <TableRow key={dataType.id}>
                    <TableCell>
                      <Box sx={{ display: "flex", alignItems: "center" }}>
                        <CodeIcon sx={{ mr: 1 }} />
                        {dataType.name}
                      </Box>
                    </TableCell>
                    <TableCell>{dataType.displayName}</TableCell>
                    <TableCell>{dataType.description}</TableCell>
                    <TableCell>
                      <Chip
                        label={dataType.status}
                        color={getStatusColor(dataType.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {dataType.updatedAt
                        ? new Date(dataType.updatedAt).toLocaleDateString()
                        : "-"}
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: "flex", justifyContent: "flex-end", gap: 1 }}>
                        <Tooltip title="Edit">
                          <IconButton size="small" onClick={() => handleOpenDialog(dataType)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        {dataType.status === "ACTIVE" ? (
                          <Tooltip title="Deactivate">
                            <IconButton size="small" onClick={() => handleDeactivate(dataType)}>
                              <DeactivateIcon />
                            </IconButton>
                          </Tooltip>
                        ) : (
                          <Tooltip title="Activate">
                            <IconButton size="small" onClick={() => handleActivate(dataType)}>
                              <ActivateIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Create/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedDataType ? "Edit Data Type" : "Create New Data Type"}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                disabled={!!selectedDataType}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Display Name"
                value={formData.displayName}
                onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                multiline
                rows={3}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Schema Definition (JSON)"
                value={formData.schemaDefinition}
                onChange={(e) => setFormData({ ...formData, schemaDefinition: e.target.value })}
                multiline
                rows={6}
                placeholder='{"fields": [{"name": "field1", "type": "string"}]}'
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={`Sample Data (JSON) ${!selectedDataType ? "*" : ""}`}
                value={formData.sampleData}
                onChange={(e) => setFormData({ ...formData, sampleData: e.target.value })}
                multiline
                rows={8}
                placeholder='{"field1": "example value", "field2": 123}'
                required={!selectedDataType}
                helperText={!selectedDataType ? "Sample data is required when creating a new data type" : "Optional: Update the example data"}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSave} variant="contained" disabled={loading}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataTypeManagementPage;

