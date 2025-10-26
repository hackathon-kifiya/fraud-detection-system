import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Chip,
  Alert,
  CircularProgress,
  Divider,
  IconButton,
  Tooltip,
  Grid,
} from "@mui/material";
import {
  Close as CloseIcon,
  Save as SaveIcon,
  PlayArrow as ActivateIcon,
  Code as CodeIcon,
  CheckCircle as ValidIcon,
  Error as ErrorIcon,
  BugReport as TestIcon,
} from "@mui/icons-material";
import { Editor } from "@monaco-editor/react";
import { ruleEngineAPI } from "../services/api";

const DRL_TEMPLATES = {
  TRANSACTION: `package rules;

import com.frauddetection.domain.DynamicFact;

rule "High Amount Transaction"
when
    $f: DynamicFact(
        dataType == "transaction",
        getDoubleProperty("amount") > 10000
    )
then
    $f.addViolation("TXN_HIGH_AMOUNT", 20, "Transaction amount exceeds threshold");
end`,

  KYC: `package rules;

import com.frauddetection.domain.DynamicFact;

rule "Unverified KYC"
when
    $f: DynamicFact(
        dataType == "kyc",
        getBooleanProperty("verifiedStatus") == false
    )
then
    $f.addViolation("KYC_UNVERIFIED", 15, "User is not KYC verified");
end`,

  LOAN: `package rules;

import com.frauddetection.domain.DynamicFact;

rule "High Risk Loan"
when
    $f: DynamicFact(
        dataType == "loan",
        getDoubleProperty("amount") > 50000
    )
then
    $f.addViolation("LOAN_HIGH_AMOUNT", 25, "Loan amount exceeds high risk threshold");
end`,

  CREDIT: `package rules;

import com.frauddetection.domain.DynamicFact;

rule "Low Credit Score"
when
    $f: DynamicFact(
        dataType == "credit",
        getIntProperty("score") < 600
    )
then
    $f.addViolation("CREDIT_LOW_SCORE", 30, "Credit score below acceptable threshold");
end`,

  REPAYMENT: `package rules;

import com.frauddetection.domain.DynamicFact;

rule "Late Repayment"
when
    $f: DynamicFact(
        dataType == "repayment",
        getBooleanProperty("isLate") == true
    )
then
    $f.addViolation("REPAYMENT_LATE", 25, "Repayment is late");
end`,
};

const RuleEditorDialog = ({ open, rule, onClose, onSave, onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [loadingTemplate, setLoadingTemplate] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [dataTypes, setDataTypes] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    dataType: "TRANSACTION",
    status: "DRAFT",
    drlContent: "",
    changeDescription: "",
  });

  useEffect(() => {
    const loadDataTypes = async () => {
      try {
        const response = await ruleEngineAPI.getAllDataTypes();
        const types = response.data || [];
        setDataTypes(types);
        if (types.length > 0 && !rule) {
          const firstType = types[0].name || "TRANSACTION";
          setFormData(prev => ({
            ...prev,
            dataType: firstType,
            drlContent: DRL_TEMPLATES[firstType] || "",
          }));
        }
      } catch (error) {
        console.error("Failed to load data types:", error);
      }
    };
    loadDataTypes();
  }, []);

  useEffect(() => {
    if (rule) {
      setFormData({
        name: rule.name || "",
        description: rule.description || "",
        dataType: rule.dataType || "TRANSACTION",
        status: rule.status || "DRAFT",
        drlContent: rule.drlContent || "",
        changeDescription: "",
      });
    } else {
      const defaultType = dataTypes.length > 0 ? dataTypes[0].name : "TRANSACTION";
      setFormData({
        name: "",
        description: "",
        dataType: defaultType,
        status: "DRAFT",
        drlContent: DRL_TEMPLATES[defaultType] || "",
        changeDescription: "",
      });
    }
    setValidationResult(null);
  }, [rule, open, dataTypes]);

  const handleInputChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
    if (field === "dataType" && !rule) {
      setFormData({
        ...formData,
        [field]: value,
        drlContent: DRL_TEMPLATES[value] || "",
      });
    }
  };

  const handleLoadTemplate = async () => {
    console.log("Load template clicked, dataType:", formData.dataType);
    try {
      setLoadingTemplate(true);
      // Fetch template from API for all data types
      console.log("Fetching template from API for:", formData.dataType);
      const response = await ruleEngineAPI.getTemplate(formData.dataType);
      console.log("API response:", response);
      
      // Update the drlContent from API response
      const templateContent = response.data?.drlContent || "";
      setFormData(prev => ({
        ...prev,
        drlContent: templateContent,
      }));
      onShowSnackbar("Template loaded successfully", "success");
      setLoadingTemplate(false);
    } catch (error) {
      console.error("Error loading template:", error);
      onShowSnackbar("Failed to load template: " + error.message, "error");
      setLoadingTemplate(false);
    }
  };

  const handleValidate = async () => {
    if (!formData.drlContent.trim()) {
      setValidationResult({
        valid: false,
        errors: ["DRL content cannot be empty"],
      });
      return;
    }

    setValidating(true);
    try {
      const response = await ruleEngineAPI.validateDrl({
        drlContent: formData.drlContent,
        dataType: formData.dataType,
      });
      setValidationResult({
        valid: response.data.valid,
        errors: response.data.errors || [],
        warnings: response.data.warnings || [],
      });
    } catch (error) {
      setValidationResult({
        valid: false,
        errors: ["Validation failed: " + error.message],
      });
    } finally {
      setValidating(false);
    }
  };

  const handleSave = async (activate = false) => {
    if (!formData.name.trim()) {
      onShowSnackbar("Rule name is required", "error");
      return;
    }

    if (!formData.drlContent.trim()) {
      onShowSnackbar("DRL content is required", "error");
      return;
    }

    setLoading(true);
    try {
      const ruleData = {
        name: formData.name,
        description: formData.description,
        dataType: formData.dataType,
        drlContent: formData.drlContent,
        status: activate ? "ACTIVE" : formData.status,
        changeDescription: formData.changeDescription,
      };

      if (rule) {
        await ruleEngineAPI.updateRule(rule.id, ruleData);
        onShowSnackbar("Rule updated successfully", "success");
      } else {
        await ruleEngineAPI.createRule(ruleData);
        onShowSnackbar("Rule created successfully", "success");
      }

      onSave();
    } catch (error) {
      onShowSnackbar("Failed to save rule: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      name: "",
      description: "",
      dataType: "TRANSACTION",
      status: "DRAFT",
      drlContent: "",
      changeDescription: "",
    });
    setValidationResult(null);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth='lg'
      fullWidth
      fullScreen
      PaperProps={{
        sx: {
          height: "100vh",
          maxHeight: "100vh",
        },
      }}
    >
      <DialogTitle>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <Typography variant='h6' sx={{ fontWeight: "bold" }}>
            {rule ? "Edit Rule" : "Create New Rule"}
          </Typography>
          <IconButton onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ p: 3 }}>
          {/* Basic Information */}
          <Box sx={{ mb: 3 }}>
            <Typography variant='h6' sx={{ mb: 2, fontWeight: "bold" }}>
              Basic Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label='Rule Name'
                  value={formData.name}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Data Type</InputLabel>
                  <Select
                    value={formData.dataType}
                    onChange={(e) =>
                      handleInputChange("dataType", e.target.value)
                    }
                    label='Data Type'
                  >
                    {dataTypes.filter(dt => dt.status === 'ACTIVE').map((dt) => (
                      <MenuItem key={dt.id} value={dt.name}>
                        {dt.displayName || dt.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label='Description'
                  value={formData.description}
                  onChange={(e) =>
                    handleInputChange("description", e.target.value)
                  }
                  multiline
                  rows={2}
                />
              </Grid>
              {rule && (
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label='Change Description'
                    value={formData.changeDescription}
                    onChange={(e) =>
                      handleInputChange("changeDescription", e.target.value)
                    }
                    placeholder='Describe what changed in this version...'
                    multiline
                    rows={2}
                  />
                </Grid>
              )}
            </Grid>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* DRL Editor */}
          <Box sx={{ mb: 3 }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                mb: 2,
              }}
            >
              <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                DRL Content
              </Typography>
              <Box sx={{ display: "flex", gap: 1 }}>
                <Tooltip title="Load template from API">
                  <Button
                    variant='outlined'
                    startIcon={loadingTemplate ? <CircularProgress size={16} /> : <CodeIcon />}
                    onClick={handleLoadTemplate}
                    disabled={loadingTemplate}
                    size='small'
                  >
                    Load Template
                  </Button>
                </Tooltip>
                <Button
                  variant='outlined'
                  startIcon={
                    validating ? <CircularProgress size={16} /> : <ValidIcon />
                  }
                  onClick={handleValidate}
                  disabled={validating}
                  size='small'
                >
                  Validate
                </Button>
              </Box>
            </Box>

            <Box
              sx={{
                border: 1,
                borderColor: "divider",
                borderRadius: 1,
                overflow: "hidden",
              }}
            >
              <Editor
                height='400px'
                language='java'
                value={formData.drlContent}
                onChange={(value) =>
                  handleInputChange("drlContent", value || "")
                }
                theme='vs-dark'
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: "on",
                  wordWrap: "on",
                  automaticLayout: true,
                }}
              />
            </Box>

            {/* Validation Results */}
            {validationResult && (
              <Box sx={{ mt: 2 }}>
                {validationResult.valid ? (
                  <Alert severity='success' icon={<ValidIcon />}>
                    Validation passed! DRL syntax is correct.
                  </Alert>
                ) : (
                  <Alert severity='error' icon={<ErrorIcon />}>
                    <Typography
                      variant='body2'
                      sx={{ fontWeight: "bold", mb: 1 }}
                    >
                      Validation failed:
                    </Typography>
                    {validationResult.errors.map((error, index) => (
                      <Typography key={index} variant='body2'>
                        • {error}
                      </Typography>
                    ))}
                  </Alert>
                )}
              </Box>
            )}
          </Box>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, borderTop: 1, borderColor: "divider" }}>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={() => handleSave(false)}
          variant='outlined'
          startIcon={<SaveIcon />}
          disabled={loading}
        >
          {loading ? <CircularProgress size={20} /> : "Save Draft"}
        </Button>
        <Button
          onClick={() => handleSave(true)}
          variant='contained'
          startIcon={<ActivateIcon />}
          disabled={loading || !validationResult?.valid}
          sx={{ bgcolor: "#ff9800", "&:hover": { bgcolor: "#f57c00" } }}
        >
          {loading ? <CircularProgress size={20} /> : "Save & Activate"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default RuleEditorDialog;
