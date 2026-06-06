"""
Validator module for AkademiQ
Handles input validation for schedules and tasks
"""

from datetime import datetime
import re


class Validator:
    """Input validation class"""
    
    DAYS_OF_WEEK = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    PRIORITIES = ['Low', 'Medium', 'High']
    TASK_STATUS = ['Pending', 'Not Started', 'Doing', 'Done']
    
    @staticmethod
    def validate_time(time_str):
        """Validate time format HH:MM"""
        pattern = r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(pattern, time_str):
            return False, "Time must be in HH:MM format (24-hour)"
        return True, ""
    
    @staticmethod
    def validate_date(date_str):
        """Validate date format YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True, ""
        except ValueError:
            return False, "Date must be in YYYY-MM-DD format"
    
    @staticmethod
    def validate_schedule(day, course, lecturer, start_time, end_time, room):
        """Validate schedule input"""
        errors = []
        
        if day not in Validator.DAYS_OF_WEEK:
            errors.append("Invalid day of week")
        
        if not course or len(course.strip()) < 2:
            errors.append("Course name must be at least 2 characters")
        
        if lecturer and len(lecturer.strip()) < 2:
            errors.append("Lecturer name must be at least 2 characters")
        
        valid, msg = Validator.validate_time(start_time)
        if not valid:
            errors.append(f"Start time: {msg}")
        
        valid, msg = Validator.validate_time(end_time)
        if not valid:
            errors.append(f"End time: {msg}")
        
        if valid and start_time >= end_time:
            errors.append("Start time must be before end time")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_task(task_name, course_name, deadline_date, deadline_time, priority, status):
        """Validate task input"""
        errors = []
        
        if not task_name or len(task_name.strip()) < 2:
            errors.append("Task name must be at least 2 characters")
        
        if not course_name or len(course_name.strip()) < 2:
            errors.append("Course name must be at least 2 characters")
        
        valid, msg = Validator.validate_date(deadline_date)
        if not valid:
            errors.append(f"Deadline date: {msg}")
        
        valid, msg = Validator.validate_time(deadline_time)
        if not valid:
            errors.append(f"Deadline time: {msg}")
        
        if priority not in Validator.PRIORITIES:
            errors.append(f"Priority must be one of: {', '.join(Validator.PRIORITIES)}")
        
        if status not in Validator.TASK_STATUS:
            errors.append(f"Status must be one of: {', '.join(Validator.TASK_STATUS)}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_status_color(status):
        """Get color for task status"""
        colors = {
            'Pending': '#f39c12',
            'Not Started': '#e74c3c',
            'Doing': '#3498db',
            'Done': '#2ecc71'
        }
        return colors.get(status, '#7f8c8d')
    
    @staticmethod
    def get_priority_color(priority):
        """Get color for task priority"""
        colors = {
            'Low': '#2ecc71',
            'Medium': '#f39c12',
            'High': '#e74c3c'
        }
        return colors.get(priority, '#7f8c8d')
    
    @staticmethod
    def is_overdue(deadline_date, status):
        """Check if task is overdue"""
        if status == 'Done':
            return False
        
        try:
            deadline = datetime.strptime(deadline_date, '%Y-%m-%d')
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return deadline < today
        except:
            return False