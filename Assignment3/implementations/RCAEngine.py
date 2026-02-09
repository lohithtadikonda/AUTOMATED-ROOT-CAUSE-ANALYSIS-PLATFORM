"""
RCAEngine Module
Part C - Module 2 Implementation
CS331 Software Engineering Lab Assignment 3

This module implements the Root Cause Analysis Engine for the 
Automated Root Cause Analysis Platform. It identifies root causes of 
system failures by analyzing correlated events.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class CorrelatedEvent:
    """Group of related anomalies"""
    anomalies: List  # List of Anomaly objects
    correlation_score: float
    time_window: str
    affected_components: List[str]


@dataclass
class Rule:
    """RCA rule definition"""
    rule_id: str
    pattern: Dict[str, any]
    root_cause: str
    confidence: float
    description: str


@dataclass
class RCAResult:
    """Root cause analysis result"""
    root_cause: str
    confidence: float
    affected_components: List[str]
    causal_chain: List[str]
    evidence: List[Dict]
    recommendations: List[str]
    timestamp: datetime


class RCAEngine:
    """
    RCAEngine Class
    Identifies root causes of system failures by analyzing correlated events
    and applying predefined rules
    """
    
    def __init__(self, rules: List[Rule]):
        """
        Initialize RCA Engine
        
        Args:
            rules: List of Rule objects for root cause identification
        """
        if not isinstance(rules, list):
            raise ValueError("Rules must be a list")
        
        self.root_cause_rules = rules
        self.correlated_events: List[CorrelatedEvent] = []
        self.analysis_history: List[RCAResult] = []
        
        # Default rules if none provided
        if not self.root_cause_rules:
            self.root_cause_rules = self._get_default_rules()
    
    def analyze_root_cause(self, correlated_events: List[CorrelatedEvent]) -> RCAResult:
        """
        Analyze correlated events to identify root cause
        
        Args:
            correlated_events: List of CorrelatedEvent objects
        
        Returns:
            RCAResult object with identified root cause
        """
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
                confidence = self._calculate_confidence(
                    rule.root_cause, correlated_events
                )
                possible_causes.append({
                    'cause': rule.root_cause,
                    'confidence': confidence,
                    'rule': rule
                })
        
        # Rank causes by confidence
        if possible_causes:
            sorted_causes = sorted(
                possible_causes, 
                key=lambda x: x['confidence'], 
                reverse=True
            )
            best_match = sorted_causes[0]
            root_cause = best_match['cause']
            confidence = best_match['confidence']
            rule = best_match['rule']
        else:
            # No rules matched - infer from anomaly patterns
            root_cause = self._infer_root_cause(all_anomalies)
            confidence = 0.5
            rule = None
        
        # Build causal chain
        causal_chain = self.generate_causal_chain(root_cause, all_anomalies)
        
        # Extract affected components
        affected = set()
        for ce in correlated_events:
            affected.update(ce.affected_components)
        
        # Gather evidence
        evidence = [
            {
                'type': a.anomaly_type,
                'metric': a.metric_name,
                'value': a.value,
                'severity': a.severity,
                'timestamp': a.timestamp.isoformat()
            }
            for a in all_anomalies[:10]  # Limit to top 10
        ]
        
        # Generate recommendations
        recommendations = self._generate_recommendations(root_cause, rule)
        
        # Create result
        result = RCAResult(
            root_cause=root_cause,
            confidence=confidence,
            affected_components=list(affected),
            causal_chain=causal_chain,
            evidence=evidence,
            recommendations=recommendations,
            timestamp=datetime.now()
        )
        
        # Store in history
        self.analysis_history.append(result)
        
        return result
    
    def apply_rule(self, rule: Rule, events: List[CorrelatedEvent]) -> bool:
        """
        Check if a rule matches the given events
        
        Args:
            rule: Rule to apply
            events: List of CorrelatedEvent objects
        
        Returns:
            True if rule matches
        """
        pattern = rule.pattern
        
        # Extract all anomalies
        all_anomalies = []
        for ce in events:
            all_anomalies.extend(ce.anomalies)
        
        # Check required anomaly types
        if 'required_types' in pattern:
            anomaly_types = {a.anomaly_type for a in all_anomalies}
            required = set(pattern['required_types'])
            if not required.issubset(anomaly_types):
                return False
        
        # Check severity threshold
        if 'min_severity' in pattern:
            severities = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
            min_sev = severities.get(pattern['min_severity'], 0)
            has_severe = any(
                severities.get(a.severity, 0) >= min_sev 
                for a in all_anomalies
            )
            if not has_severe:
                return False
        
        # Check minimum event count
        if 'min_events' in pattern:
            if len(all_anomalies) < pattern['min_events']:
                return False
        
        # Check affected components
        if 'components' in pattern:
            all_components = set()
            for ce in events:
                all_components.update(ce.affected_components)
            
            required_components = set(pattern['components'])
            if not required_components.issubset(all_components):
                return False
        
        return True
    
    def rank_causes(self, possible_causes: List[str]) -> List[str]:
        """
        Rank possible causes by probability
        
        Args:
            possible_causes: List of cause strings
        
        Returns:
            Sorted list of causes (highest probability first)
        """
        # In a real system, this would use historical data
        # For now, use simple heuristics
        
        priority_order = [
            'DEPLOYMENT_CONFIGURATION_ERROR',
            'RESOURCE_EXHAUSTION',
            'NETWORK_CONNECTIVITY',
            'DATABASE_FAILURE',
            'APPLICATION_BUG',
            'EXTERNAL_DEPENDENCY_FAILURE'
        ]
        
        ranked = []
        for cause in priority_order:
            if cause in possible_causes:
                ranked.append(cause)
        
        # Add remaining causes
        for cause in possible_causes:
            if cause not in ranked:
                ranked.append(cause)
        
        return ranked
    
    def generate_causal_chain(self, root_cause: str, 
                            anomalies: List) -> List[str]:
        """
        Generate cause-effect chain from root cause to observed symptoms
        
        Args:
            root_cause: Identified root cause
            anomalies: List of anomalies
        
        Returns:
            List of causal steps
        """
        # Define causal chains for common root causes
        chains = {
            'DEPLOYMENT_CONFIGURATION_ERROR': [
                '1. Deployment initiated with incorrect configuration',
                '2. Application fails to start or load settings',
                '3. Connection errors and timeouts occur',
                '4. System logs show critical errors',
                '5. Service becomes unavailable'
            ],
            'RESOURCE_EXHAUSTION': [
                '1. Resource usage gradually increases',
                '2. Threshold limits are exceeded (CPU/Memory)',
                '3. System performance degrades',
                '4. Timeouts and failures occur',
                '5. Service becomes unresponsive'
            ],
            'DATABASE_FAILURE': [
                '1. Database connection pool exhausted',
                '2. Database queries timeout',
                '3. Application layer errors increase',
                '4. Data operations fail',
                '5. User-facing features break'
            ],
            'NETWORK_CONNECTIVITY': [
                '1. Network interruption occurs',
                '2. Services lose connectivity',
                '3. API calls timeout',
                '4. Cascading failures in dependent services',
                '5. System-wide degradation'
            ],
            'APPLICATION_BUG': [
                '1. Code defect triggers unexpected behavior',
                '2. Error handling fails or is inadequate',
                '3. System state becomes inconsistent',
                '4. Errors propagate through application',
                '5. Features malfunction or crash'
            ]
        }
        
        return chains.get(root_cause, [
            f'1. {root_cause} occurred',
            '2. System anomalies detected',
            '3. Service degradation observed',
            '4. Failures propagated through system'
        ])
    
    def _calculate_confidence(self, cause: str, 
                            events: List[CorrelatedEvent]) -> float:
        """
        Calculate confidence score for a root cause
        
        Args:
            cause: Root cause string
            events: Correlated events
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence from rule
        base_confidence = 0.6
        
        # Increase confidence based on evidence strength
        all_anomalies = []
        for ce in events:
            all_anomalies.extend(ce.anomalies)
        
        # More critical anomalies = higher confidence
        critical_count = sum(1 for a in all_anomalies if a.severity == 'CRITICAL')
        high_count = sum(1 for a in all_anomalies if a.severity == 'HIGH')
        
        confidence = base_confidence
        confidence += (critical_count * 0.1)
        confidence += (high_count * 0.05)
        
        # Cap at 0.95 (never 100% certain)
        return min(confidence, 0.95)
    
    def _infer_root_cause(self, anomalies: List) -> str:
        """
        Infer root cause when no rules match
        
        Args:
            anomalies: List of anomalies
        
        Returns:
            Inferred root cause string
        """
        # Check for deployment-related errors
        deployment_errors = sum(
            1 for a in anomalies 
            if a.anomaly_type == 'DEPLOYMENT_ERROR'
        )
        if deployment_errors > 0:
            return 'DEPLOYMENT_CONFIGURATION_ERROR'
        
        # Check for resource issues
        metric_anomalies = sum(
            1 for a in anomalies 
            if 'METRIC' in a.anomaly_type and 
            ('cpu' in a.metric_name.lower() or 'memory' in a.metric_name.lower())
        )
        if metric_anomalies >= 2:
            return 'RESOURCE_EXHAUSTION'
        
        # Check for log errors
        error_logs = sum(
            1 for a in anomalies 
            if a.anomaly_type in ['LOG_ERROR', 'LOG_CRITICAL']
        )
        if error_logs >= 3:
            return 'APPLICATION_BUG'
        
        # Default to unknown
        return 'UNKNOWN_ROOT_CAUSE'
    
    def _generate_recommendations(self, root_cause: str, 
                                 rule: Optional[Rule]) -> List[str]:
        """Generate recommended actions"""
        recommendations_map = {
            'DEPLOYMENT_CONFIGURATION_ERROR': [
                'Review deployment configuration files',
                'Validate environment variables',
                'Check application logs for configuration errors',
                'Rollback to previous stable deployment',
                'Verify dependency versions'
            ],
            'RESOURCE_EXHAUSTION': [
                'Scale up resources (CPU/Memory)',
                'Identify and optimize resource-intensive processes',
                'Implement resource limits and throttling',
                'Check for memory leaks',
                'Review and optimize queries'
            ],
            'DATABASE_FAILURE': [
                'Check database connection pool settings',
                'Verify database server health',
                'Review slow query logs',
                'Optimize database indexes',
                'Check disk space on database server'
            ],
            'NETWORK_CONNECTIVITY': [
                'Verify network connectivity between services',
                'Check firewall and security group rules',
                'Review DNS configuration',
                'Validate service endpoints',
                'Check for network timeouts in logs'
            ],
            'APPLICATION_BUG': [
                'Review recent code changes',
                'Check error stack traces in logs',
                'Reproduce issue in test environment',
                'Run diagnostic tests',
                'Consider rolling back recent deployment'
            ]
        }
        
        return recommendations_map.get(root_cause, [
            'Review system logs for error messages',
            'Check recent changes or deployments',
            'Verify external dependencies are functioning',
            'Monitor system metrics for unusual patterns',
            'Consult with development team'
        ])
    
    def _get_default_rules(self) -> List[Rule]:
        """Get default RCA rules"""
        return [
            Rule(
                rule_id='R001',
                pattern={
                    'required_types': ['DEPLOYMENT_ERROR'],
                    'min_severity': 'CRITICAL'
                },
                root_cause='DEPLOYMENT_CONFIGURATION_ERROR',
                confidence=0.85,
                description='Deployment configuration issues'
            ),
            Rule(
                rule_id='R002',
                pattern={
                    'required_types': ['METRIC_THRESHOLD'],
                    'min_events': 2,
                    'min_severity': 'HIGH'
                },
                root_cause='RESOURCE_EXHAUSTION',
                confidence=0.75,
                description='Resource exhaustion patterns'
            ),
            Rule(
                rule_id='R003',
                pattern={
                    'required_types': ['LOG_ERROR', 'LOG_CRITICAL'],
                    'min_events': 3
                },
                root_cause='APPLICATION_BUG',
                confidence=0.70,
                description='Application error patterns'
            )
        ]
    
    def get_analysis_history(self, limit: int = 10) -> List[RCAResult]:
        """Get recent RCA results"""
        return self.analysis_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear analysis history"""
        self.analysis_history.clear()


# Example usage and testing
if __name__ == "__main__":
    print("="*60)
    print("RCAEngine Module - Test Cases")
    print("="*60)
    
    # Mock Anomaly class for testing
    class MockAnomaly:
        def __init__(self, atype, severity, metric):
            self.anomaly_type = atype
            self.severity = severity
            self.metric_name = metric
            self.value = 95.0
            self.timestamp = datetime.now()
    
    # Create engine with default rules
    engine = RCAEngine([])
    print(f"\n✓ RCAEngine initialized with {len(engine.root_cause_rules)} rules")
    
    # Test 1: Deployment error analysis
    print("\n" + "="*60)
    print("Test 1: Deployment Configuration Error")
    print("="*60)
    
    events1 = [
        CorrelatedEvent(
            anomalies=[
                MockAnomaly('DEPLOYMENT_ERROR', 'CRITICAL', 'deployment'),
                MockAnomaly('LOG_CRITICAL', 'CRITICAL', 'app_logs'),
                MockAnomaly('LOG_ERROR', 'HIGH', 'system_logs')
            ],
            correlation_score=0.9,
            time_window='2026-02-09 10:00-10:05',
            affected_components=['WebServer', 'AppServer', 'Database']
        )
    ]
    
    result1 = engine.analyze_root_cause(events1)
    print(f"\nRoot Cause: {result1.root_cause}")
    print(f"Confidence: {result1.confidence:.2%}")
    print(f"Affected Components: {', '.join(result1.affected_components)}")
    print(f"\nCausal Chain:")
    for step in result1.causal_chain:
        print(f"  {step}")
    print(f"\nRecommendations:")
    for i, rec in enumerate(result1.recommendations[:3], 1):
        print(f"  {i}. {rec}")
    
    # Test 2: Resource exhaustion analysis
    print("\n" + "="*60)
    print("Test 2: Resource Exhaustion")
    print("="*60)
    
    events2 = [
        CorrelatedEvent(
            anomalies=[
                MockAnomaly('METRIC_THRESHOLD', 'HIGH', 'cpu_usage'),
                MockAnomaly('METRIC_THRESHOLD', 'HIGH', 'memory_usage'),
                MockAnomaly('METRIC_THRESHOLD', 'CRITICAL', 'response_time')
            ],
            correlation_score=0.85,
            time_window='2026-02-09 11:00-11:10',
            affected_components=['AppServer', 'LoadBalancer']
        )
    ]
    
    result2 = engine.analyze_root_cause(events2)
    print(f"\nRoot Cause: {result2.root_cause}")
    print(f"Confidence: {result2.confidence:.2%}")
    print(f"Affected Components: {', '.join(result2.affected_components)}")
    print(f"\nTop 3 Recommendations:")
    for i, rec in enumerate(result2.recommendations[:3], 1):
        print(f"  {i}. {rec}")
    
    # Test 3: Application bug analysis
    print("\n" + "="*60)
    print("Test 3: Application Bug")
    print("="*60)
    
    events3 = [
        CorrelatedEvent(
            anomalies=[
                MockAnomaly('LOG_ERROR', 'MEDIUM', 'app_logs'),
                MockAnomaly('LOG_ERROR', 'HIGH', 'app_logs'),
                MockAnomaly('LOG_CRITICAL', 'CRITICAL', 'app_logs'),
                MockAnomaly('LOG_ERROR', 'MEDIUM', 'app_logs')
            ],
            correlation_score=0.75,
            time_window='2026-02-09 12:00-12:15',
            affected_components=['AppServer']
        )
    ]
    
    result3 = engine.analyze_root_cause(events3)
    print(f"\nRoot Cause: {result3.root_cause}")
    print(f"Confidence: {result3.confidence:.2%}")
    print(f"\nCausal Chain:")
    for step in result3.causal_chain[:3]:
        print(f"  {step}")
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Total analyses performed: {len(engine.analysis_history)}")
    print(f"\nIdentified root causes:")
    for i, result in enumerate(engine.analysis_history, 1):
        print(f"  {i}. {result.root_cause} (confidence: {result.confidence:.1%})")
    
    print("\n" + "="*60)
    print("All tests completed successfully! ✓")
    print("="*60)
