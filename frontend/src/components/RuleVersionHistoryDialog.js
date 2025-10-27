import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Divider,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Tooltip,
  Grid,
} from "@mui/material";
import {
  Close as CloseIcon,
  Undo as RollbackIcon,
  Visibility as ViewIcon,
  Code as CodeIcon,
  History as HistoryIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
} from "@mui/icons-material";
import { Editor } from "@monaco-editor/react";
import { ruleEngineAPI } from "../services/api";

const RuleVersionHistoryDialog = ({ open, rule, onClose, onShowSnackbar }) => {
  const [loading, setLoading] = useState(false);
  const [versions, setVersions] = useState([]);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [showCode, setShowCode] = useState(false);

  useEffect(() => {
    if (open && rule) {
      loadVersions();
    }
  }, [open, rule]);

  const loadVersions = async () => {
    if (!rule) return;

    setLoading(true);
    try {
      const response = await ruleEngineAPI.getRuleVersions(rule.id);
      setVersions(response.data.versions || []);
    } catch (error) {
      onShowSnackbar("Failed to load rule versions: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleViewVersion = (version) => {
    setSelectedVersion(version);
    setShowCode(true);
  };

  const handleRollback = async (version) => {
    if (
      !window.confirm(
        `Are you sure you want to rollback to version ${version.version}?`
      )
    ) {
      return;
    }

    try {
      setLoading(true);
      await ruleEngineAPI.rollbackRule(rule.id, version.version, {
        changeDescription: `Rollback to version ${version.version}`,
      });
      onShowSnackbar("Rule rolled back successfully", "success");
      loadVersions();
    } catch (error) {
      onShowSnackbar("Failed to rollback rule: " + error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return "Unknown";
    return new Date(dateString).toLocaleString();
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

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth='lg'
      fullWidth
      PaperProps={{
        sx: {
          height: "90vh",
          maxHeight: "90vh",
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
            Version History: {rule?.name || "Unknown Rule"}
          </Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ p: 3 }}>
          {loading && versions.length === 0 ? (
            <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
              <CircularProgress />
            </Box>
          ) : versions.length === 0 ? (
            <Alert severity='info'>
              No version history found for this rule.
            </Alert>
          ) : (
            <Grid container spacing={3}>
              {/* Version List */}
              <Grid item xs={12} md={6}>
                <Typography variant='h6' sx={{ mb: 2, fontWeight: "bold" }}>
                  Versions ({versions.length})
                </Typography>

                <List sx={{ maxHeight: 400, overflow: "auto" }}>
                  {versions.map((version, index) => (
                    <React.Fragment key={version.version}>
                      <ListItem
                        sx={{
                          border: 1,
                          borderColor: "divider",
                          borderRadius: 1,
                          mb: 1,
                          bgcolor:
                            selectedVersion?.version === version.version
                              ? "action.selected"
                              : "background.paper",
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box
                              sx={{
                                display: "flex",
                                alignItems: "center",
                                gap: 1,
                              }}
                            >
                              <Typography
                                variant='subtitle1'
                                sx={{ fontWeight: "bold" }}
                              >
                                Version {version.version}
                              </Typography>
                              <Chip
                                label={version.status}
                                size='small'
                                color={getStatusColor(version.status)}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography
                                variant='body2'
                                color='text.secondary'
                              >
                                {version.changeDescription || "No description"}
                              </Typography>
                              <Box
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  gap: 2,
                                  mt: 1,
                                }}
                              >
                                <Box
                                  sx={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 0.5,
                                  }}
                                >
                                  <PersonIcon sx={{ fontSize: 16 }} />
                                  <Typography variant='caption'>
                                    {version.createdBy || "Unknown"}
                                  </Typography>
                                </Box>
                                <Box
                                  sx={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 0.5,
                                  }}
                                >
                                  <ScheduleIcon sx={{ fontSize: 16 }} />
                                  <Typography variant='caption'>
                                    {formatDate(version.createdAt)}
                                  </Typography>
                                </Box>
                              </Box>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <Box sx={{ display: "flex", gap: 0.5 }}>
                            <Tooltip title='View Code'>
                              <IconButton
                                size='small'
                                onClick={() => handleViewVersion(version)}
                              >
                                <ViewIcon />
                              </IconButton>
                            </Tooltip>
                            {index > 0 && (
                              <Tooltip title='Rollback to this version'>
                                <IconButton
                                  size='small'
                                  onClick={() => handleRollback(version)}
                                  color='warning'
                                >
                                  <RollbackIcon />
                                </IconButton>
                              </Tooltip>
                            )}
                          </Box>
                        </ListItemSecondaryAction>
                      </ListItem>
                    </React.Fragment>
                  ))}
                </List>
              </Grid>

              {/* Code Viewer */}
              <Grid item xs={12} md={6}>
                <Typography variant='h6' sx={{ mb: 2, fontWeight: "bold" }}>
                  {selectedVersion
                    ? `Version ${selectedVersion.version} Code`
                    : "Select a version to view code"}
                </Typography>

                {selectedVersion ? (
                  <Card>
                    <CardContent sx={{ p: 0 }}>
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
                          value={selectedVersion.drlContent || ""}
                          theme='vs-dark'
                          options={{
                            minimap: { enabled: false },
                            fontSize: 12,
                            lineNumbers: "on",
                            wordWrap: "on",
                            readOnly: true,
                            automaticLayout: true,
                          }}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent>
                      <Box
                        sx={{
                          display: "flex",
                          flexDirection: "column",
                          alignItems: "center",
                          justifyContent: "center",
                          py: 4,
                          color: "text.secondary",
                        }}
                      >
                        <CodeIcon sx={{ fontSize: 48, mb: 2 }} />
                        <Typography variant='body1'>
                          Click on a version to view its code
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                )}
              </Grid>
            </Grid>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3, borderTop: 1, borderColor: "divider" }}>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default RuleVersionHistoryDialog;
