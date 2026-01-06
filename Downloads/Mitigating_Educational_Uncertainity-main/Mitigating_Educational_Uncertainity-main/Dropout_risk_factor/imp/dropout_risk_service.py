import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import numpy as np

class DropoutRiskService:
    """
    Service class for handling dropout risk assessment and related operations.
    """
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize the DropoutRiskService.
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        self.assessments: Dict[str, Dict] = {}
        self.logger = self._setup_logging()
        self._ensure_directories()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger('dropout_risk_service')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # Console handler
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            
            # File handler
            fh = logging.FileHandler('dropout_risk_service.log')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            
        return logger
        
    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        os.makedirs(os.path.join(self.data_dir, 'raw'), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, 'processed'), exist_ok=True)
        os.makedirs('models', exist_ok=True)
    
    def assess_risk(self, data: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate dropout risk based on multiple factors.
        
        Args:
            data: Dictionary containing assessment metrics
            
        Returns:
            Dictionary containing risk score, level, and factor details
        """
        try:
            # Calculate weighted scores for each category
            academic_score = self._calculate_academic_score(data)
            behavioral_score = self._calculate_behavioral_score(data)
            personal_score = self._calculate_personal_score(data)
            institutional_score = self._calculate_institutional_score(data)
            social_score = self._calculate_social_score(data)
            external_score = self._calculate_external_score(data)
            psychological_score = self._calculate_psychological_score(data)
            historical_score = self._calculate_historical_score(data)
            digital_score = self._calculate_digital_score(data)
            warning_score = self._calculate_warning_score(data)
            
            # Calculate total risk score (0-100)
            total_score = (
                (academic_score * 0.25) +
                (behavioral_score * 0.15) +
                (personal_score * 0.1) +
                (institutional_score * 0.1) +
                (social_score * 0.08) +
                (external_score * 0.07) +
                (psychological_score * 0.1) +
                (historical_score * 0.08) +
                (digital_score * 0.05) +
                (warning_score * 0.12)
            )
            
            risk_score = min(100, max(0, total_score))  # Ensure score is between 0-100
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = 'High Risk'
            elif risk_score >= 30:
                risk_level = 'Moderate Risk'
            else:
                risk_level = 'Low Risk'
            
            return {
                'risk_score': round(risk_score, 1),
                'risk_level': risk_level,
                'factors': {
                    'academic': academic_score,
                    'behavioral': behavioral_score,
                    'personal': personal_score,
                    'institutional': institutional_score,
                    'social': social_score,
                    'external': external_score,
                    'psychological': psychological_score,
                    'historical': historical_score,
                    'digital': digital_score,
                    'warning': warning_score,
                    'details': self._get_detailed_factors(data)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in assess_risk: {str(e)}", exc_info=True)
            raise
    
    def _calculate_academic_score(self, data: Dict[str, float]) -> float:
        """Calculate academic performance score."""
        return (
            ((10 - data.get('grades', 5)) * 4) +  # Convert GPA to risk (higher GPA = lower risk)
            ((100 - data.get('attendance', 75)) * 0.2) + 
            ((100 - data.get('assignments', 75)) * 0.2) +
            ((100 - data.get('exams', 70)) * 0.2)
        )
    
    def _calculate_behavioral_score(self, data: Dict[str, float]) -> float:
        """Calculate behavioral indicators score."""
        return (
            ((100 - data.get('participation', 65)) * 0.3) +  # Lower participation = higher risk
            (data.get('absences', 3) * 5 * 0.3) +           # Scale 0-10 to 0-50
            (data.get('tardiness', 2) * 5 * 0.2) +          # Scale 0-10 to 0-50
            (data.get('behavioralIssues', 1) * 4 * 0.2)     # Scale 0-10 to 0-40
        )
    
    def _calculate_personal_score(self, data: Dict[str, float]) -> float:
        """Calculate personal factors score."""
        return (
            (data.get('financialStress', 50) * 0.4) +
            ((data.get('workHours', 20) / 40 * 100) * 0.2) +  # Scale 0-40 to 0-100
            ((100 - data.get('familySupport', 70)) * 0.2) +   # Lower support = higher risk
            ((100 - data.get('healthStatus', 80)) * 0.2)      # Worse health = higher risk
        )
    
    def _calculate_institutional_score(self, data: Dict[str, float]) -> float:
        """Calculate institutional factors score."""
        return (
            ((data.get('courseLoad', 15) / 24 * 100) * 0.3) +  # Higher course load = higher risk
            ((100 - data.get('majorFit', 70)) * 0.4) +        # Lower fit = higher risk
            ((100 - min(data.get('facultyInteraction', 7) * 10, 100)) * 0.2) +  # Less interaction = higher risk
            ((100 - min(data.get('campusInvolvement', 6) * 5, 100)) * 0.1)      # Less involvement = higher risk
        )
    
    def _calculate_social_score(self, data: Dict[str, float]) -> float:
        """Calculate social factors score."""
        return (
            ((100 - data.get('peerNetwork', 70)) * 0.4) +  # Weaker network = higher risk
            ((100 - data.get('mentorship', 60)) * 0.4) +   # Less mentorship = higher risk
            (data.get('bullying', 2) * 0.2)               # More bullying = higher risk
        )
    
    def _calculate_external_score(self, data: Dict[str, float]) -> float:
        """Calculate external factors score."""
        return (
            (min(data.get('commuteTime', 0.5) / 1.8, 100) * 0.4) +  # Longer commute = higher risk (max 3 hours = 100%)
            (min(data.get('familyResponsibilities', 3) * 2, 100) * 0.3) +  # More responsibilities = higher risk
            ((100 - data.get('workLifeBalance', 70)) * 0.3)        # Worse balance = higher risk
        )
    
    def _calculate_psychological_score(self, data: Dict[str, float]) -> float:
        """Calculate psychological factors score."""
        return (
            (100 - data.get('motivation', 70)) * 0.4 +  # Lower motivation = higher risk
            (100 - data.get('selfEfficacy', 70)) * 0.4 +  # Lower self-efficacy = higher risk
            data.get('stressLevel', 50) * 0.2  # Higher stress = higher risk
        )
    
    def _calculate_historical_score(self, data: Dict[str, float]) -> float:
        """Calculate historical data score."""
        return (
            data.get('previousDropout', 0) * 0.4 +  # Previous dropout = higher risk
            data.get('gradeRetention', 0) * 0.4 +   # Grade retention = higher risk
            min(data.get('schoolChanges', 0) * 10, 100) * 0.2  # More school changes = higher risk (max 10 changes = 100%)
        )
    
    def _calculate_digital_score(self, data: Dict[str, float]) -> float:
        """Calculate digital footprint score."""
        return (
            (100 - min(data.get('lmsActivity', 15) * 5, 100)) * 0.6 +  # Less LMS activity = higher risk
            (100 - data.get('onlineEngagement', 70)) * 0.4  # Less online engagement = higher risk
        )
    
    def _calculate_warning_score(self, data: Dict[str, float]) -> float:
        """Calculate early warning indicators score."""
        return (
            data.get('warningSigns', 1) * 0.7 +  # More warning signs = higher risk
            data.get('earlyAlerts', 0) * 0.3     # More faculty concerns = higher risk
        )
    
    def _get_detailed_factors(self, data: Dict[str, float]) -> Dict[str, float]:
        """Get detailed factor values from input data."""
        return {
            # Academic
            'grades': data.get('grades', 5.0),
            'attendance': data.get('attendance', 75.0),
            'assignments': data.get('assignments', 75.0),
            'exams': data.get('exams', 70.0),
            # Behavioral
            'participation': data.get('participation', 65.0),
            'absences': data.get('absences', 3.0),
            'tardiness': data.get('tardiness', 2.0),
            'behavioral_issues': data.get('behavioralIssues', 1.0),
            # Personal
            'financial_stress': data.get('financialStress', 50.0),
            'work_hours': data.get('workHours', 20.0),
            'family_support': data.get('familySupport', 70.0),
            'health_status': data.get('healthStatus', 80.0),
            # Institutional
            'course_load': data.get('courseLoad', 15.0),
            'major_fit': data.get('majorFit', 70.0),
            'faculty_interaction': data.get('facultyInteraction', 7.0),
            'campus_involvement': data.get('campusInvolvement', 6.0),
            # Social
            'peer_network': data.get('peerNetwork', 70.0),
            'mentorship': data.get('mentorship', 60.0),
            'bullying': data.get('bullying', 2.0),
            # External
            'commute_time': data.get('commuteTime', 0.5),
            'family_responsibilities': data.get('familyResponsibilities', 3.0),
            'work_life_balance': data.get('workLifeBalance', 70.0),
            # Psychological
            'motivation': data.get('motivation', 70.0),
            'self_efficacy': data.get('selfEfficacy', 70.0),
            'stress_level': data.get('stressLevel', 50.0),
            # Historical
            'previous_dropout': data.get('previousDropout', 0.0),
            'grade_retention': data.get('gradeRetention', 0.0),
            'school_changes': data.get('schoolChanges', 0.0),
            # Digital
            'lms_activity': data.get('lmsActivity', 15.0),
            'online_engagement': data.get('onlineEngagement', 70.0),
            # Early Warning
            'warning_signs': data.get('warningSigns', 1.0),
            'early_alerts': data.get('earlyAlerts', 0.0)
        }
    
    def get_category_progress(self, student_data: Dict[str, float]) -> Dict[str, Dict[str, float]]:
        """
        Calculate progress for each category.
        
        Args:
            student_data: Dictionary containing student assessment data
            
        Returns:
            Dictionary with progress data for each category
        """
        if not student_data:
            return {}
            
        return {
            'academic': {
                'score': (
                    student_data.get('grades', 5.0) * 10 * 0.4 +  # Convert 0-10 to 0-100
                    student_data.get('assignments', 75.0) * 0.3 +
                    student_data.get('exams', 70.0) * 0.3
                ),
                'target': 85
            },
            'behavioral': {
                'score': 100 - (
                    (100 - student_data.get('participation', 65.0)) * 0.4 +
                    student_data.get('absences', 3.0) * 10 * 0.3 +
                    student_data.get('tardiness', 2.0) * 10 * 0.2 +
                    student_data.get('behavioralIssues', 1.0) * 10 * 0.1
                ),
                'target': 80
            },
            'personal': {
                'score': (
                    (100 - student_data.get('financialStress', 50.0)) * 0.4 +
                    (100 - min(student_data.get('workHours', 20.0) * 2.5, 100)) * 0.2 +
                    student_data.get('familySupport', 70.0) * 0.2 +
                    student_data.get('healthStatus', 80.0) * 0.2
                ),
                'target': 75
            },
            'institutional': {
                'score': (
                    (100 - min(student_data.get('courseLoad', 15.0) * 4.17, 100)) * 0.3 +
                    student_data.get('majorFit', 70.0) * 0.4 +
                    student_data.get('facultyInteraction', 7.0) * 10 * 0.2 +
                    student_data.get('campusInvolvement', 6.0) * 20 * 0.1
                ),
                'target': 70
            },
            'social': {
                'score': (
                    student_data.get('peerNetwork', 70.0) * 0.4 +
                    student_data.get('mentorship', 60.0) * 0.4 +
                    (100 - student_data.get('bullying', 2.0) * 10) * 0.2
                ),
                'target': 80
            },
            'external': {
                'score': (
                    (100 - min(student_data.get('commuteTime', 0.5) / 1.8 * 100, 100)) * 0.4 +
                    (100 - min(student_data.get('familyResponsibilities', 3.0) * 2, 100)) * 0.3 +
                    student_data.get('workLifeBalance', 70.0) * 0.3
                ),
                'target': 75
            },
            'psychological': {
                'score': (
                    student_data.get('motivation', 70.0) * 0.4 +
                    student_data.get('selfEfficacy', 70.0) * 0.4 +
                    (100 - student_data.get('stressLevel', 50.0)) * 0.2
                ),
                'target': 80
            },
            'historical': {
                'score': 100 - (
                    student_data.get('previousDropout', 0.0) * 100 * 0.4 +
                    student_data.get('gradeRetention', 0.0) * 100 * 0.4 +
                    min(student_data.get('schoolChanges', 0.0) * 10, 100) * 0.2
                ),
                'target': 90
            },
            'digital': {
                'score': (
                    min(student_data.get('lmsActivity', 15.0) * 5, 100) * 0.6 +
                    student_data.get('onlineEngagement', 70.0) * 0.4
                ),
                'target': 70
            },
            'warning': {
                'score': 100 - (
                    student_data.get('warningSigns', 1.0) * 20 * 0.7 +
                    student_data.get('earlyAlerts', 0.0) * 20 * 0.3
                ),
                'target': 90
            }
        }
    
    def generate_trends(self, student_id: str, assessment_data: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Generate trend data for a student.
        
        Args:
            student_id: Unique identifier for the student
            assessment_data: Optional current assessment data
            
        Returns:
            Dictionary containing trend data
        """
        try:
            if not assessment_data:
                assessment_data = {}
            
            # Normalize and prepare current values with defaults
            current_values = {
                'grades': min(100, (assessment_data.get('grades', 5.0) / 10) * 100),
                'attendance': min(100, assessment_data.get('attendance', 75.0)),
                'assignments': min(100, assessment_data.get('assignments', 75.0)),
                'participation': min(100, assessment_data.get('participation', 65.0)),
                'exams': min(100, assessment_data.get('exams', 70.0)),
                'behavioral_issues': min(100, assessment_data.get('behavioralIssues', 1.0) * 10),
                'motivation': min(100, assessment_data.get('motivation', 70.0)),
                'self_efficacy': min(100, assessment_data.get('selfEfficacy', 70.0))
            }
            
            # Generate dates for the last 6 months
            end_date = datetime.now()
            dates = [(end_date - timedelta(days=30*(5-i))).strftime('%b %Y') for i in range(6)]
            
            # Generate trends for each metric
            trends = {
                'dates': dates,
                'grades': self._generate_trend(current_values['grades'], 'grades', is_positive=True, volatility=5),
                'attendance': self._generate_trend(current_values['attendance'], 'attendance', is_positive=True, volatility=3),
                'assignments': self._generate_trend(current_values['assignments'], 'assignments', is_positive=True, volatility=7),
                'participation': self._generate_trend(current_values['participation'], 'participation', is_positive=True, volatility=8),
                'exams': self._generate_trend(current_values['exams'], 'exams', is_positive=True, volatility=6),
                'behavioral_issues': self._generate_trend(current_values['behavioral_issues'], 'behavioral_issues', is_positive=False, volatility=10),
                'motivation': self._generate_trend(current_values['motivation'], 'motivation', is_positive=True, volatility=9),
                'self_efficacy': self._generate_trend(current_values['self_efficacy'], 'self_efficacy', is_positive=True, volatility=7),
                'current_values': current_values
            }
            
            # Add risk score if assessment data is available
            if assessment_data:
                risk_assessment = self.assess_risk(assessment_data)
                trends.update({
                    'risk_score': risk_assessment['risk_score'],
                    'risk_level': risk_assessment['risk_level']
                })
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error in generate_trends for student {student_id}: {str(e)}", exc_info=True)
            # Return fallback data in case of error
            return {
                'dates': ['2023-06', '2023-07', '2023-08', '2023-09', '2023-10', '2023-11'],
                'grades': [75, 78, 82, 80, 85, 88],
                'attendance': [85, 82, 88, 90, 92, 95],
                'assignments': [80, 82, 78, 85, 88, 90],
                'participation': [70, 72, 75, 78, 82, 85],
                'error': str(e)
            }
    
    def _generate_trend(
        self, 
        current: float, 
        metric_name: str,
        is_positive: bool = True, 
        volatility: float = 8.0
    ) -> List[float]:
        """
        Generate a realistic trend for a metric.
        
        Args:
            current: Current value of the metric (0-100)
            metric_name: Name of the metric (for logging)
            is_positive: Whether higher values are better
            volatility: Amount of random variation to add
            
        Returns:
            List of 6 values representing the trend
        """
        try:
            # Set baseline and target based on metric type
            if is_positive:
                # For positive metrics, start lower and trend up
                base = max(20, current * np.random.uniform(0.6, 0.9))  # Start between 60-90% of current
            else:
                # For negative metrics, start higher and trend down
                base = min(100, current * np.random.uniform(1.1, 1.5))
            
            # Generate smooth trend using cubic interpolation
            x = np.linspace(0, 1, 6)
            if is_positive:
                # S-curve for positive trends (start slow, accelerate, then slow down)
                y = [base + (current - base) * (xi**0.7) for xi in x]
            else:
                # Inverted S-curve for negative trends
                y = [base - (base - current) * (xi**0.7) for xi in x]
            
            # Add some random noise (less noise for more stable metrics like attendance)
            if metric_name in ['attendance', 'grades']:
                noise = np.random.normal(0, volatility/3, 6)
            else:
                noise = np.random.normal(0, volatility, 6)
            
            # Apply noise and ensure values are within bounds
            y = [max(0, min(100, y[i] + noise[i])) for i in range(6)]
            
            # Ensure the last value matches the current assessment
            y[-1] = current
            
            return [round(val, 1) for val in y]
            
        except Exception as e:
            self.logger.error(f"Error in _generate_trend for {metric_name}: {str(e)}")
            # Return a simple linear trend if there's an error
            if is_positive:
                return [max(0, current - 20 + i * 4) for i in range(6)]
            else:
                return [min(100, current + 20 - i * 4) for i in range(6)]


# Example usage
if __name__ == "__main__":
    # Initialize the service
    service = DropoutRiskService()
    
    # Sample assessment data
    sample_assessment = {
        'grades': 7.5,  # 0-10 scale
        'attendance': 85.0,  # 0-100%
        'assignments': 80.0,  # 0-100%
        'exams': 75.0,  # 0-100%
        'participation': 70.0,  # 0-100%
        'absences': 3.0,  # Number of absences
        'tardiness': 2.0,  # 0-10 scale
        'behavioralIssues': 1.0,  # 0-10 scale
        'financialStress': 40.0,  # 0-100%
        'workHours': 15.0,  # Hours per week
        'familySupport': 80.0,  # 0-100%
        'healthStatus': 85.0,  # 0-100%
        'courseLoad': 15.0,  # Credit hours
        'majorFit': 80.0,  # 0-100%
        'facultyInteraction': 7.0,  # 0-10 scale
        'campusInvolvement': 6.0,  # 0-10 scale
        'peerNetwork': 75.0,  # 0-100%
        'mentorship': 70.0,  # 0-100%
        'bullying': 1.0,  # 0-10 scale
        'commuteTime': 0.5,  # Hours one-way
        'familyResponsibilities': 3.0,  # 0-10 scale
        'workLifeBalance': 75.0,  # 0-100%
        'motivation': 80.0,  # 0-100%
        'selfEfficacy': 75.0,  # 0-100%
        'stressLevel': 40.0,  # 0-100%
        'previousDropout': 0.0,  # 0 or 1
        'gradeRetention': 0.0,  # 0 or 1
        'schoolChanges': 0.0,  # Number of school changes
        'lmsActivity': 15.0,  # 0-20 scale
        'onlineEngagement': 75.0,  # 0-100%
        'warningSigns': 1.0,  # 0-5 scale
        'earlyAlerts': 0.0  # 0-5 scale
    }
    
    # Perform risk assessment
    result = service.assess_risk(sample_assessment)
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    
    # Get category progress
    progress = service.get_category_progress(sample_assessment)
    print("\nCategory Progress:")
    for category, data in progress.items():
        print(f"{category.capitalize()}: {data['score']:.1f}% (Target: {data['target']}%)")
    
    # Generate trends
    trends = service.generate_trends("sample_student", sample_assessment)
    print("\nTrend data generated for:", ", ".join([k for k in trends.keys() if k not in ['dates', 'current_values']]))
