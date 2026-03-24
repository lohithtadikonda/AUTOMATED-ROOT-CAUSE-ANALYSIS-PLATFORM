from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class CorrelatedEvent:
    anomalies: List
    correlation_score: float
    time_window: str
    affected_components: List[str]


@dataclass
class Rule:
    rule_id: str
    pattern: Dict[str, any]
    root_cause: str
    confidence: float
    description: str


@dataclass
class RCAResult:
    root_cause: str
    confidence: float
    affected_components: List[str]
    causal_chain: List[str]
    evidence: List[Dict]
    recommendations: List[str]
    timestamp: datetime


class RCAEngine:
    
    def __init__(self, rules: List[Rule]):
        if not isinstance(rules, list):
            raise ValueError("Rules must be a list")
        
        self.root_cause_rules = rules if rules else self._get_default_rules()
        self.correlated_events: List[CorrelatedEvent] = []
        self.analysis_history: List[RCAResult] = []
    
    def analyze_root_cause(self, correlated_events: List[CorrelatedEvent]) -> RCAResult:
        if not correlated_events:
            return RCAResult(
                root_cause="UNKNOWN",
                confidence=0.0,
                affected_components=[],
                causal_chain=[],
                evidence=[],
                recommendations=["No events to analyze"],
                timestamp=datetime.now()
            )
        
        self.correlated_events = correlated_events
        
        # Extract all anomalies from correlated events
        all_anomalies = []
        for ce in correlated_events:
            all_anomalies.extend(ce.anomalies)
        
        # Find matching rules
        possible_causes = []
        
        for rule in self.root_cause_rules:
            if self.apply_rule(rule, correlated_events):
                confidence = self._calculate_confidence(rule, correlated_events)
                possible_causes.append({
                    'cause': rule.root_cause,
                    'confidence': confidence,
                    'rule_id': rule.rule_id,
                    'description': rule.description
                })
        
        # Rank causes by confidence
        if possible_causes:
            ranked_causes = sorted(possible_causes, key=lambda x: x['confidence'], reverse=True)
            best_cause = ranked_causes[0]
            
            # Generate causal chain
            causal_chain = self.generate_causal_chain(best_cause['cause'], all_anomalies)
            
            # Collect evidence
            evidence = self._collect_evidence(all_anomalies)
            
            # Get affected components
            affected_components = list(set([
                ce.affected_components for ce in correlated_events
            ]))
            affected_components = [item for sublist in affected_components for item in sublist]
            
            # Generate recommendations
            recommendations = self._generate_recommendations(best_cause['cause'])
            
            result = RCAResult(
                root_cause=best_cause['cause'],
                confidence=best_cause['confidence'],
                affected_components=affected_components,
                causal_chain=causal_chain,
                evidence=evidence,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
        else:
            # No matching rule found
            result = RCAResult(
                root_cause="UNKNOWN",
                confidence=0.5,
                affected_components=[],
                causal_chain=["Multiple anomalies detected", "No specific pattern matched"],
                evidence=self._collect_evidence(all_anomalies),
                recommendations=["Review system logs", "Check system metrics", "Investigate recent changes"],
                timestamp=datetime.now()
            )
        
        # Store in history
        self.analysis_history.append(result)
        
        return result
    
    def apply_rule(self, rule: Rule, correlated_events: List[CorrelatedEvent]) -> bool:
        """
        Check if a rule applies to the correlated events
        
        Args:
            rule: Rule to apply
            correlated_events: List of CorrelatedEvent objects
        
        Returns:
            True if rule matches, False otherwise
        """
        pattern = rule.pattern
        
        # Extract all anomalies
        all_anomalies = []
        for ce in correlated_events:
            all_anomalies.extend(ce.anomalies)
        
        # Check pattern requirements
        required_types = pattern.get('anomaly_types', [])
        required_metrics = pattern.get('metrics', [])
        required_keywords = pattern.get('keywords', [])
        
        # Check if required anomaly types are present
        if required_types:
            present_types = set()
            for anomaly in all_anomalies:
                if isinstance(anomaly, dict):
                    present_types.add(anomaly.get('type', ''))
                else:
                    present_types.add(getattr(anomaly, 'anomaly_type', ''))
            
            if not all(rt in present_types for rt in required_types):
                return False
        
        # Check if required metrics are present
        if required_metrics:
            present_metrics = set()
            for anomaly in all_anomalies:
                if isinstance(anomaly, dict):
                    present_metrics.add(anomaly.get('metric', ''))
                else:
                    present_metrics.add(getattr(anomaly, 'metric_name', ''))
            
            if not all(rm in present_metrics for rm in required_metrics):
                return False
        
        # Check for required keywords in descriptions
        if required_keywords:
            all_descriptions = []
            for anomaly in all_anomalies:
                if isinstance(anomaly, dict):
                    all_descriptions.append(anomaly.get('description', '').lower())
                else:
                    all_descriptions.append(getattr(anomaly, 'description', '').lower())
            
            combined_text = ' '.join(all_descriptions)
            
            if not any(keyword.lower() in combined_text for keyword in required_keywords):
                return False
        
        return True
    
    def generate_causal_chain(self, root_cause: str, anomalies: List) -> List[str]:
        chains = {
            'DEPLOYMENT_CONFIGURATION_ERROR': [
                "Incorrect deployment configuration",
                "Application failed to start properly",
                "Error logs generated",
                "System health deteriorated"
            ],
            'RESOURCE_EXHAUSTION': [
                "Resource usage increased gradually",
                "Threshold limits exceeded",
                "System performance degraded",
                "Critical resource exhaustion"
            ],
            'NETWORK_CONNECTIVITY_ISSUE': [
                "Network connectivity problem occurred",
                "Connection timeouts increased",
                "Service dependencies failed",
                "Cascading failures across components"
            ],
            'DATABASE_CONNECTION_FAILURE': [
                "Database connection lost",
                "Query timeouts occurred",
                "Application errors increased",
                "Data inconsistencies appeared"
            ],
            'MEMORY_LEAK': [
                "Memory usage gradually increased",
                "Garbage collection overhead increased",
                "Application slowdown",
                "Out of memory errors"
            ]
        }
        
        return chains.get(root_cause, [
            f"Root cause: {root_cause}",
            "Multiple anomalies detected",
            "System instability"
        ])
    
    def _calculate_confidence(self, rule: Rule, correlated_events: List[CorrelatedEvent]) -> float:
        base_confidence = rule.confidence
        
        # Adjust confidence based on correlation scores
        avg_correlation = sum(ce.correlation_score for ce in correlated_events) / len(correlated_events)
        
        # Higher correlation increases confidence
        adjusted_confidence = (base_confidence + avg_correlation) / 2
        
        return min(adjusted_confidence, 1.0)
    
    def _collect_evidence(self, anomalies: List) -> List[Dict]:
        evidence = []
        
        for anomaly in anomalies:
            if isinstance(anomaly, dict):
                evidence.append({
                    'type': anomaly.get('type', 'UNKNOWN'),
                    'severity': anomaly.get('severity', 'UNKNOWN'),
                    'description': anomaly.get('description', ''),
                    'timestamp': anomaly.get('timestamp', '')
                })
            else:
                evidence.append({
                    'type': getattr(anomaly, 'anomaly_type', 'UNKNOWN'),
                    'severity': getattr(anomaly, 'severity', 'UNKNOWN'),
                    'description': getattr(anomaly, 'description', ''),
                    'timestamp': getattr(anomaly, 'timestamp', datetime.now()).isoformat()
                })
        
        return evidence
    
    def _generate_recommendations(self, root_cause: str) -> List[str]:
        recommendations = {
            'DEPLOYMENT_CONFIGURATION_ERROR': [
                "Review and validate deployment configuration files",
                "Check environment variables and secrets",
                "Verify application dependencies and versions",
                "Rollback to previous stable configuration"
            ],
            'RESOURCE_EXHAUSTION': [
                "Scale up resources (CPU/Memory)",
                "Implement resource limits and quotas",
                "Optimize resource-intensive operations",
                "Enable auto-scaling policies"
            ],
            'NETWORK_CONNECTIVITY_ISSUE': [
                "Check network configuration and firewall rules",
                "Verify DNS resolution",
                "Test connectivity to dependent services",
                "Review load balancer settings"
            ],
            'DATABASE_CONNECTION_FAILURE': [
                "Verify database credentials and connection string",
                "Check database server status",
                "Review connection pool settings",
                "Increase connection timeout values"
            ],
            'MEMORY_LEAK': [
                "Profile application memory usage",
                "Review recent code changes",
                "Implement memory limits",
                "Restart affected services"
            ]
        }
        
        return recommendations.get(root_cause, [
            "Review system logs for more details",
            "Check recent configuration changes",
            "Monitor system metrics closely",
            "Contact system administrator if issue persists"
        ])
    
    def _get_default_rules(self) -> List[Rule]:
        """
        Get default RCA rules
        
        Returns:
            List of default Rule objects
        """
        return [
            Rule(
                rule_id="R001",
                pattern={
                    'anomaly_types': ['LOG_ERROR', 'DEPLOYMENT_ERROR'],
                    'keywords': ['deployment', 'configuration', 'failed']
                },
                root_cause="DEPLOYMENT_CONFIGURATION_ERROR",
                confidence=0.85,
                description="Deployment configuration error detected"
            ),
            Rule(
                rule_id="R002",
                pattern={
                    'metrics': ['cpu_usage', 'memory_usage'],
                    'anomaly_types': ['METRIC_ANOMALY']
                },
                root_cause="RESOURCE_EXHAUSTION",
                confidence=0.80,
                description="Resource exhaustion detected"
            ),
            Rule(
                rule_id="R003",
                pattern={
                    'keywords': ['connection', 'timeout', 'refused', 'network']
                },
                root_cause="NETWORK_CONNECTIVITY_ISSUE",
                confidence=0.75,
                description="Network connectivity issue detected"
            ),
            Rule(
                rule_id="R004",
                pattern={
                    'keywords': ['database', 'connection', 'pool', 'query']
                },
                root_cause="DATABASE_CONNECTION_FAILURE",
                confidence=0.80,
                description="Database connection failure detected"
            ),
            Rule(
                rule_id="R005",
                pattern={
                    'metrics': ['memory_usage'],
                    'keywords': ['out of memory', 'heap', 'gc']
                },
                root_cause="MEMORY_LEAK",
                confidence=0.70,
                description="Memory leak detected"
            )
        ]
    
    def get_analysis_history(self, limit: Optional[int] = None) -> List[RCAResult]:
        """
        Get analysis history
        
        Args:
            limit: Optional limit on results
        
        Returns:
            List of RCAResult objects
        """
        if limit:
            return self.analysis_history[-limit:]
        return self.analysis_history


# Test code
if __name__ == "__main__":
    print("Testing RCAEngine...")
    
    # Create test correlated event
    test_anomalies = [
        {'type': 'LOG_ERROR', 'severity': 'HIGH', 'description': 'Deployment failed - configuration error', 
         'metric': 'error_logs', 'timestamp': datetime.now().isoformat()},
        {'type': 'DEPLOYMENT_ERROR', 'severity': 'CRITICAL', 'description': 'Configuration validation failed',
         'metric': 'deployment_logs', 'timestamp': datetime.now().isoformat()}
    ]
    
    correlated_event = CorrelatedEvent(
        anomalies=test_anomalies,
        correlation_score=0.9,
        time_window="5_minutes",
        affected_components=["app-server", "config-service"]
    )
    
    # Initialize engine
    engine = RCAEngine([])
    
    # Analyze
    result = engine.analyze_root_cause([correlated_event])
    
    print(f"Root Cause: {result.root_cause}")
    print(f"Confidence: {result.confidence}")
    print(f"Recommendations: {len(result.recommendations)}")
    print("RCAEngine tests passed!")
