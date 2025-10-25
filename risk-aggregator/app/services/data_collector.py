"""
Data collector service for gathering risk signals from multiple sources.
"""

import httpx
from datetime import datetime, timedelta
from typing import List, Optional

from app.core.config import settings
from app.core.logging import setup_logging
from app.models.schemas import RiskSignal, RiskCategory

logger = setup_logging()


class DataCollector:
    """Service for collecting data from various sources."""

    def __init__(self):
        """Initialize data collector."""
        self.anomaly_detection_url = settings.ANOMALY_DETECTION_URL
        self.java_engine_url = settings.JAVA_ENGINE_URL
        self.backend_url = settings.BACKEND_URL
        self.timeout = 30.0

    async def collect_customer_signals(
        self,
        customer_id: str,
        include_kyc: bool = True,
        include_transactions: bool = True,
        include_credit: bool = True,
        include_loans: bool = True,
        include_repayments: bool = True,
        time_window_days: int = 90,
    ) -> List[RiskSignal]:
        """
        Collect risk signals from all available sources for a customer.

        Args:
            customer_id: Customer identifier
            include_kyc: Include KYC signals
            include_transactions: Include transaction signals
            include_credit: Include credit signals
            include_loans: Include loan signals
            include_repayments: Include repayment signals
            time_window_days: Time window for data collection

        Returns:
            List[RiskSignal]: Collected risk signals
        """
        signals: List[RiskSignal] = []

        # Collect KYC signals
        if include_kyc:
            kyc_signals = await self._collect_kyc_signals(customer_id)
            signals.extend(kyc_signals)

        # Collect transaction signals
        if include_transactions:
            transaction_signals = await self._collect_transaction_signals(
                customer_id, time_window_days
            )
            signals.extend(transaction_signals)

        # Collect credit signals
        if include_credit:
            credit_signals = await self._collect_credit_signals(customer_id)
            signals.extend(credit_signals)

        # Collect loan signals
        if include_loans:
            loan_signals = await self._collect_loan_signals(customer_id)
            signals.extend(loan_signals)

        # Collect repayment signals
        if include_repayments:
            repayment_signals = await self._collect_repayment_signals(customer_id)
            signals.extend(repayment_signals)

        logger.info(f"Collected {len(signals)} signals for customer {customer_id}")

        return signals

    async def _collect_kyc_signals(self, customer_id: str) -> List[RiskSignal]:
        """
        Collect KYC risk signals.

        Args:
            customer_id: Customer identifier

        Returns:
            List[RiskSignal]: KYC risk signals
        """
        signals = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Call anomaly detection service for KYC
                url = f"{self.anomaly_detection_url}/api/v1/kyc/detect"
                response = await client.post(
                    url,
                    json={"customer_id": customer_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    signals.append(
                        RiskSignal(
                            category=RiskCategory.KYC,
                            score=data.get("anomaly_score", 0.0),
                            confidence=data.get("confidence", 0.8),
                            source="anomaly-detection",
                            details=data,
                            timestamp=datetime.utcnow(),
                        )
                    )
                    logger.info(f"Collected KYC signal for {customer_id}")

        except Exception as e:
            logger.warning(f"Failed to collect KYC signals for {customer_id}: {str(e)}")

        return signals

    async def _collect_transaction_signals(
        self, customer_id: str, time_window_days: int
    ) -> List[RiskSignal]:
        """
        Collect transaction risk signals.

        Args:
            customer_id: Customer identifier
            time_window_days: Time window for analysis

        Returns:
            List[RiskSignal]: Transaction risk signals
        """
        signals = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Call anomaly detection service for transactions
                url = f"{self.anomaly_detection_url}/api/v1/transaction/detect"
                response = await client.post(
                    url,
                    json={
                        "customer_id": customer_id,
                        "time_window_days": time_window_days,
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    signals.append(
                        RiskSignal(
                            category=RiskCategory.TRANSACTION,
                            score=data.get("anomaly_score", 0.0),
                            confidence=data.get("confidence", 0.8),
                            source="anomaly-detection",
                            details=data,
                            timestamp=datetime.utcnow(),
                        )
                    )
                    logger.info(f"Collected transaction signal for {customer_id}")

        except Exception as e:
            logger.warning(
                f"Failed to collect transaction signals for {customer_id}: {str(e)}"
            )

        return signals

    async def _collect_credit_signals(self, customer_id: str) -> List[RiskSignal]:
        """
        Collect credit risk signals.

        Args:
            customer_id: Customer identifier

        Returns:
            List[RiskSignal]: Credit risk signals
        """
        signals = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Call Java engine for credit rules
                url = f"{self.java_engine_url}/api/credit/assess"
                response = await client.post(
                    url,
                    json={"customer_id": customer_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    signals.append(
                        RiskSignal(
                            category=RiskCategory.CREDIT,
                            score=data.get("risk_score", 0.0),
                            confidence=data.get("confidence", 0.9),
                            source="java-engine",
                            details=data,
                            timestamp=datetime.utcnow(),
                        )
                    )
                    logger.info(f"Collected credit signal for {customer_id}")

        except Exception as e:
            logger.warning(f"Failed to collect credit signals for {customer_id}: {str(e)}")

        return signals

    async def _collect_loan_signals(self, customer_id: str) -> List[RiskSignal]:
        """
        Collect loan risk signals.

        Args:
            customer_id: Customer identifier

        Returns:
            List[RiskSignal]: Loan risk signals
        """
        signals = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Call Java engine for loan rules
                url = f"{self.java_engine_url}/api/loan/assess"
                response = await client.post(
                    url,
                    json={"customer_id": customer_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    signals.append(
                        RiskSignal(
                            category=RiskCategory.LOAN,
                            score=data.get("risk_score", 0.0),
                            confidence=data.get("confidence", 0.9),
                            source="java-engine",
                            details=data,
                            timestamp=datetime.utcnow(),
                        )
                    )
                    logger.info(f"Collected loan signal for {customer_id}")

        except Exception as e:
            logger.warning(f"Failed to collect loan signals for {customer_id}: {str(e)}")

        return signals

    async def _collect_repayment_signals(self, customer_id: str) -> List[RiskSignal]:
        """
        Collect repayment risk signals.

        Args:
            customer_id: Customer identifier

        Returns:
            List[RiskSignal]: Repayment risk signals
        """
        signals = []

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Call Java engine for repayment rules
                url = f"{self.java_engine_url}/api/repayment/assess"
                response = await client.post(
                    url,
                    json={"customer_id": customer_id},
                )

                if response.status_code == 200:
                    data = response.json()
                    signals.append(
                        RiskSignal(
                            category=RiskCategory.REPAYMENT,
                            score=data.get("risk_score", 0.0),
                            confidence=data.get("confidence", 0.9),
                            source="java-engine",
                            details=data,
                            timestamp=datetime.utcnow(),
                        )
                    )
                    logger.info(f"Collected repayment signal for {customer_id}")

        except Exception as e:
            logger.warning(
                f"Failed to collect repayment signals for {customer_id}: {str(e)}"
            )

        return signals

