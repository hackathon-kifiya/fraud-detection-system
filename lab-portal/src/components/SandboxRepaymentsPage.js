import React from 'react';
import SandboxPage from './SandboxPage';

const SandboxRepaymentsPage = ({ onShowSnackbar }) => {
  return (
    <SandboxPage 
      onShowSnackbar={onShowSnackbar}
      dataType="repayments"
      title="Repayment"
    />
  );
};

export default SandboxRepaymentsPage;

