import React from 'react';
import SandboxPage from './SandboxPage';

const SandboxTransactionsPage = ({ onShowSnackbar }) => {
  return (
    <SandboxPage 
      onShowSnackbar={onShowSnackbar}
      dataType="transactions"
      title="Transaction"
    />
  );
};

export default SandboxTransactionsPage;

