import React, { useCallback, useState } from 'react';
import {
  Button,
  Box,
  Typography,
  Paper,
  LinearProgress,
} from '@mui/material';
import { CloudUpload } from '@mui/icons-material';

const FileUpload = ({ onUpload, disabled, accept = "*" }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (disabled || uploading) return;

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  }, [disabled, uploading]);

  const handleFile = (file) => {
    if (accept && !file.name.toLowerCase().endsWith(accept.replace('.', ''))) {
      return;
    }
    
    setUploading(true);
    onUpload(file);
    // Reset uploading state after a delay to show progress
    setTimeout(() => setUploading(false), 1000);
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (disabled || uploading) return;
    
    const files = e.target.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  return (
    <Paper
      variant="outlined"
      sx={{
        p: 3,
        textAlign: 'center',
        border: dragActive ? '2px dashed' : '1px dashed',
        borderColor: dragActive ? 'primary.main' : 'grey.300',
        backgroundColor: dragActive ? 'action.hover' : 'background.paper',
        cursor: disabled || uploading ? 'not-allowed' : 'pointer',
        opacity: disabled || uploading ? 0.6 : 1,
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          borderColor: 'primary.main',
          backgroundColor: 'action.hover',
        },
      }}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept={accept}
        onChange={handleChange}
        disabled={disabled || uploading}
        style={{ display: 'none' }}
        id="file-upload"
      />
      
      <label htmlFor="file-upload">
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
          <CloudUpload 
            sx={{ 
              fontSize: 48, 
              color: dragActive ? 'primary.main' : 'grey.400',
              transition: 'color 0.2s ease-in-out',
            }} 
          />
          
          <Typography variant="h6" color={dragActive ? 'primary.main' : 'text.primary'}>
            {uploading ? 'Uploading...' : 'Click to upload or drag and drop'}
          </Typography>
          
          <Typography variant="body2" color="text.secondary">
            {accept === "*" ? 'Any file type' : `Only ${accept} files`}
          </Typography>
          
          {uploading && (
            <Box sx={{ width: '100%', mt: 2 }}>
              <LinearProgress />
            </Box>
          )}
          
          <Button
            variant="outlined"
            component="span"
            disabled={disabled || uploading}
            sx={{ mt: 1 }}
          >
            Choose File
          </Button>
        </Box>
      </label>
    </Paper>
  );
};

export default FileUpload;

