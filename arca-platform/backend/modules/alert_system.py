"""
Alert System Module
Manages real-time alerts and notifications
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class Alert:
    """Represents an alert"""
    alert_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None


class AlertSystem:
    """
    AlertSystem Class
    Real-time critical issue notification system
    """
    
    def __init__(self):
        """Initialize AlertSystem"""
        self.alerts: List[Alert] = []
        self.alert_queue: List[Alert] = []
        self._alert_counter = 0
    
    def send_alert(self, alert_data: Dict):
        """
        Send an alert
        
        Args:
            alert_data: Dictionary containing alert information
        """
        # Create alert
        self._alert_counter += 1
        alert_id = f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self._alert_counter}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_type=alert_data.get('type', 'UNKNOWN'),
            severity=alert_data.get('severity', 'MEDIUM'),
            message=self._format_alert_message(alert_data),
            timestamp=datetime.now(),
            acknowledged=False
        )
        
        # Add to alerts list and queue
        self.alerts.append(alert)
        self.alert_queue.append(alert)
        
        # Send notification (placeholder for actual notification logic)
        self._send_notification(alert)
        
        print(f"🚨 Alert sent: {alert.alert_type} - {alert.severity}")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: ID of alert to acknowledge
        
        Returns:
            True if successful, False otherwise
        """
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.now()
                
                # Remove from queue
                self.alert_queue = [a for a in self.alert_queue if a.alert_id != alert_id]
                
                print(f"✅ Alert acknowledged: {alert_id}")
                return True
        
        return False
    
    def get_unacknowledged_alerts(self) -> List[Alert]:
        """
        Get all unacknowledged alerts
        
        Returns:
            List of unacknowledged Alert objects
        """
        return [alert for alert in self.alerts if not alert.acknowledged]
    
    def get_alerts_by_severity(self, severity: str) -> List[Alert]:
        """
        Get alerts filtered by severity
        
        Args:
            severity: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
        
        Returns:
            List of Alert objects
        """
        return [alert for alert in self.alerts if alert.severity == severity.upper()]
    
    def get_alert_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get alert history
        
        Args:
            limit: Optional limit on number of alerts
        
        Returns:
            List of alert dictionaries
        """
        history = [self._alert_to_dict(alert) for alert in self.alerts]
        
        # Sort by timestamp (most recent first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if limit:
            return history[:limit]
        
        return history
    
    def clear_old_alerts(self, days: int = 30):
        """
        Clear alerts older than specified days
        
        Args:
            days: Number of days after which to clear alerts
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        self.alerts = [
            alert for alert in self.alerts
            if alert.timestamp > cutoff_date
        ]
        
        print(f"🧹 Cleared alerts older than {days} days")
    
    def _format_alert_message(self, alert_data: Dict) -> str:
        """
        Format alert message from alert data
        
        Args:
            alert_data: Alert data dictionary
        
        Returns:
            Formatted message string
        """
        alert_type = alert_data.get('type', 'UNKNOWN')
        
        if alert_type == 'CRITICAL_ANOMALY':
            return (
                f"Critical anomaly detected: {alert_data.get('root_cause', 'Unknown cause')}. "
                f"Confidence: {alert_data.get('confidence', 0):.2f}. "
                f"Anomalies: {alert_data.get('anomaly_count', 0)}"
            )
        elif alert_type == 'RESOURCE_THRESHOLD':
            return (
                f"Resource threshold exceeded: {alert_data.get('resource', 'Unknown')} "
                f"at {alert_data.get('value', 0):.2f}%"
            )
        elif alert_type == 'DEPLOYMENT_FAILURE':
            return (
                f"Deployment failure: {alert_data.get('message', 'Unknown error')}"
            )
        else:
            return alert_data.get('message', 'Alert triggered')
    
    def _send_notification(self, alert: Alert):
        """
        Send notification through various channels
        
        Args:
            alert: Alert object to send
        """
        # This is a placeholder for actual notification logic
        # In production, this would send notifications via:
        # - Email
        # - Slack
        # - SMS
        # - PagerDuty
        # - etc.
        
        # For now, just log it
        print(f"📧 Notification sent for alert: {alert.alert_id}")
        
        # Example notification formats:
        
        # Email notification
        if alert.severity in ['CRITICAL', 'HIGH']:
            self._send_email_notification(alert)
        
        # Slack notification
        if alert.severity == 'CRITICAL':
            self._send_slack_notification(alert)
    
    def _send_email_notification(self, alert: Alert):
        """Send email notification (placeholder)"""
        # In production, integrate with email service (SendGrid, SES, etc.)
        print(f"📧 Email notification: {alert.message}")
    
    def _send_slack_notification(self, alert: Alert):
        """Send Slack notification (placeholder)"""
        # In production, integrate with Slack API
        print(f"💬 Slack notification: {alert.message}")
    
    def _send_sms_notification(self, alert: Alert):
        """Send SMS notification (placeholder)"""
        # In production, integrate with SMS service (Twilio, SNS, etc.)
        print(f"📱 SMS notification: {alert.message}")
    
    def _alert_to_dict(self, alert: Alert) -> Dict:
        """
        Convert Alert object to dictionary
        
        Args:
            alert: Alert object
        
        Returns:
            Dictionary representation
        """
        return {
            'id': alert.alert_id,
            'type': alert.alert_type,
            'severity': alert.severity,
            'message': alert.message,
            'timestamp': alert.timestamp.isoformat(),
            'acknowledged': alert.acknowledged,
            'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
        }


# Test code
if __name__ == "__main__":
    print("Testing AlertSystem...")
    
    from datetime import timedelta
    
    # Create alert system
    alert_system = AlertSystem()
    
    # Send test alerts
    alert_system.send_alert({
        'type': 'CRITICAL_ANOMALY',
        'severity': 'CRITICAL',
        'root_cause': 'DEPLOYMENT_CONFIGURATION_ERROR',
        'confidence': 0.85,
        'anomaly_count': 3
    })
    
    alert_system.send_alert({
        'type': 'RESOURCE_THRESHOLD',
        'severity': 'HIGH',
        'resource': 'CPU',
        'value': 95.5
    })
    
    # Get unacknowledged alerts
    unacked = alert_system.get_unacknowledged_alerts()
    print(f"✅ Unacknowledged alerts: {len(unacked)}")
    
    # Acknowledge first alert
    if unacked:
        alert_system.acknowledge_alert(unacked[0].alert_id)
    
    # Get alert history
    history = alert_system.get_alert_history(limit=10)
    print(f"✅ Alert history: {len(history)} alerts")
    
    print("✅ AlertSystem tests passed!")
