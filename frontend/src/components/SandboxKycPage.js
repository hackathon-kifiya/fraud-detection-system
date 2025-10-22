import React from 'react';
import SandboxPage from './SandboxPage';

const SandboxKycPage = ({ onShowSnackbar }) => {
  return (
    <SandboxPage 
      onShowSnackbar={onShowSnackbar}
      dataType="kyc"
      title="KYC"
    />
  );
};

export default SandboxKycPage;

