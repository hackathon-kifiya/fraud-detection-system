import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Avatar,
  TextField,
  Button,
  Grid,
  Divider,
  Alert,
  Snackbar,
  Paper,
  IconButton,
  Tooltip,
} from "@mui/material";
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Security as SecurityIcon,
  AdminPanelSettings as AdminIcon,
} from "@mui/icons-material";
import { useAuth } from "../contexts/AuthContext";

const ProfilePage = ({ onShowSnackbar }) => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    role: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || "",
        last_name: user.last_name || "",
        email: user.email || "",
        role: user.role || "",
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      first_name: user.first_name || "",
      last_name: user.last_name || "",
      email: user.email || "",
      role: user.role || "",
    });
    setError("");
  };

  const handleSave = async () => {
    setLoading(true);
    setError("");

    try {
      // Here you would typically make an API call to update the user profile
      // For now, we'll just simulate a successful update
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setIsEditing(false);
      onShowSnackbar("Profile updated successfully", "success");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  const getRoleIcon = (role) => {
    switch (role?.toLowerCase()) {
      case "admin":
        return <AdminIcon sx={{ fontSize: "1.2rem" }} />;
      case "analyst":
        return <SecurityIcon sx={{ fontSize: "1.2rem" }} />;
      default:
        return <PersonIcon sx={{ fontSize: "1.2rem" }} />;
    }
  };

  const getRoleColor = (role) => {
    switch (role?.toLowerCase()) {
      case "admin":
        return "#f44336";
      case "analyst":
        return "#ff9800";
      default:
        return "#2196f3";
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: "auto", p: 3 }}>
      <Typography
        variant='h4'
        component='h1'
        sx={{ mb: 3, fontWeight: "bold" }}
      >
        Profile Settings
      </Typography>

      <Grid container spacing={3}>
        {/* Profile Card */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: "fit-content" }}>
            <CardContent sx={{ textAlign: "center", p: 3 }}>
              <Avatar
                sx={{
                  width: 120,
                  height: 120,
                  bgcolor: "#ff9800",
                  mx: "auto",
                  mb: 2,
                  fontSize: "3rem",
                }}
              >
                {user?.first_name?.charAt(0)?.toUpperCase()}
                {user?.last_name?.charAt(0)?.toUpperCase()}
              </Avatar>

              <Typography variant='h5' sx={{ fontWeight: "bold", mb: 1 }}>
                {user?.first_name} {user?.last_name}
              </Typography>

              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 1,
                  mb: 2,
                }}
              >
                {getRoleIcon(user?.role)}
                <Typography
                  variant='body1'
                  sx={{
                    color: getRoleColor(user?.role),
                    fontWeight: "600",
                    textTransform: "uppercase",
                    fontSize: "0.9rem",
                  }}
                >
                  {user?.role}
                </Typography>
              </Box>

              <Typography variant='body2' color='text.secondary' sx={{ mb: 2 }}>
                {user?.email}
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Typography variant='body2' color='text.secondary'>
                Member since {new Date().getFullYear()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Profile Form */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Box
                sx={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  mb: 3,
                }}
              >
                <Typography variant='h6' sx={{ fontWeight: "bold" }}>
                  Personal Information
                </Typography>
                {!isEditing ? (
                  <Tooltip title='Edit Profile'>
                    <IconButton onClick={handleEdit} color='primary'>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                ) : (
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Tooltip title='Save Changes'>
                      <IconButton
                        onClick={handleSave}
                        color='primary'
                        disabled={loading}
                      >
                        <SaveIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title='Cancel'>
                      <IconButton onClick={handleCancel} color='error'>
                        <CancelIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                )}
              </Box>

              {error && (
                <Alert severity='error' sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label='First Name'
                    name='first_name'
                    value={formData.first_name}
                    onChange={handleChange}
                    disabled={!isEditing}
                    InputProps={{
                      startAdornment: (
                        <PersonIcon sx={{ mr: 1, color: "text.secondary" }} />
                      ),
                    }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label='Last Name'
                    name='last_name'
                    value={formData.last_name}
                    onChange={handleChange}
                    disabled={!isEditing}
                    InputProps={{
                      startAdornment: (
                        <PersonIcon sx={{ mr: 1, color: "text.secondary" }} />
                      ),
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label='Email Address'
                    name='email'
                    type='email'
                    value={formData.email}
                    onChange={handleChange}
                    disabled={!isEditing}
                    InputProps={{
                      startAdornment: (
                        <EmailIcon sx={{ mr: 1, color: "text.secondary" }} />
                      ),
                    }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label='Role'
                    name='role'
                    value={formData.role}
                    disabled
                    InputProps={{
                      startAdornment: getRoleIcon(formData.role),
                    }}
                    sx={{
                      "& .MuiInputBase-input": {
                        color: getRoleColor(formData.role),
                        fontWeight: "600",
                        textTransform: "uppercase",
                      },
                    }}
                  />
                </Grid>
              </Grid>

              {isEditing && (
                <Box
                  sx={{
                    mt: 3,
                    display: "flex",
                    gap: 2,
                    justifyContent: "flex-end",
                  }}
                >
                  <Button
                    variant='outlined'
                    onClick={handleCancel}
                    disabled={loading}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant='contained'
                    onClick={handleSave}
                    disabled={loading}
                    sx={{
                      bgcolor: "#ff9800",
                      "&:hover": { bgcolor: "#f57c00" },
                    }}
                  >
                    {loading ? "Saving..." : "Save Changes"}
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProfilePage;
