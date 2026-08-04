"""
SentinelAI - Synthetic Enterprise Dataset Generator
Generates realistic employee activity data for Insider Threat Detection
Metadata-only (NEVER inspects file contents)

Produces these files:
  employees.csv
  login_events.csv
  usb_events.csv
  cloud_events.csv
  network_events.csv
  browser_events.csv
  email_events.csv
  application_events.csv
  activities.csv (combined master index)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import json
import os
from faker import Faker

fake = Faker()

# Deterministic seed for reproducibility
random.seed(42)
np.random.seed(42)


class SentinelDatasetGenerator:
    """Generates synthetic dataset for insider threat detection."""

    def __init__(self, num_employees: int = 1000, num_events: int = 200000):
        self.num_employees = num_employees
        self.num_events = num_events
        self.num_days = 60
        self.base_date = datetime.now() - timedelta(days=self.num_days)

        # Departments and roles
        self.departments = ['Engineering', 'Sales', 'Marketing', 'HR', 'Finance', 'Legal', 'Operations', 'IT']
        self.department_weights = [0.25, 0.15, 0.12, 0.08, 0.10, 0.07, 0.13, 0.10]

        # Roles by department
        self.roles = {
            'Engineering': ['Software Engineer', 'Data Scientist', 'DevOps Engineer', 'QA Engineer', 'Tech Lead'],
            'Sales': ['Account Executive', 'Sales Manager', 'SDR', 'Account Manager'],
            'Marketing': ['Marketing Lead', 'Content Strategist', 'SEO Specialist', 'Brand Manager'],
            'HR': ['HR Coordinator', 'Recruiter', 'HR Business Partner'],
            'Finance': ['Financial Analyst', 'Accountant', 'CFO', 'Payroll Specialist'],
            'Legal': ['Legal Counsel', 'Compliance Officer', 'Paralegal'],
            'Operations': ['Operations Manager', 'Logistics Coordinator', 'Facilities Manager'],
            'IT': ['IT Administrator', 'Network Engineer', 'Security Analyst', 'Helpdesk Tech']
        }

        # Risk profiles (5% are malicious insiders)
        num_malicious = max(1, int(num_employees * 0.05))
        num_normal = num_employees - num_malicious
        self.risk_profiles = ['normal'] * num_normal + ['malicious'] * num_malicious
        random.shuffle(self.risk_profiles)

        # Sensitive directories
        self.sensitive_dirs = [
            'C:/Projects/CustomerData', 'C:/Projects/FinancialReports', 'C:/Projects/SourceCode',
            'C:/Projects/EmployeeRecords', 'C:/Projects/StrategicPlans', 'C:/Projects/IP_Patents',
            'C:/Projects/Mergers_Acquisitions'
        ]

        # Applications
        self.applications = [
            'VS Code', 'IntelliJ', 'Notepad++', 'Chrome', 'Edge', 'File Explorer', 'Outlook',
            'PowerShell', 'Command Prompt', 'Slack', 'Zoom', 'Teams', 'Excel', 'Word', 'GitHub Desktop'
        ]

        # Browsers
        self.browsers = ['Chrome', 'Edge', 'Firefox', 'Safari', 'Opera']

        # Cloud services
        self.cloud_services = ['Google Drive', 'Dropbox', 'OneDrive', 'Mega', 'WeTransfer']

        # Suspicious domains
        self.suspicious_domains = ['pastebin.com', 'mega.nz', 'transfer.sh', 'anonfiles.com', 'file.io']
        self.normal_domains = ['github.com', 'stackoverflow.com', 'company.internal', 'jira.company.com']

        # Locations
        self.locations = ['New York', 'San Francisco', 'London', 'Tokyo', 'Berlin', 'Singapore',
                          'Austin', 'Toronto', 'Sydney', 'Amsterdam']

    def generate_employees(self) -> pd.DataFrame:
        """Generate employee records."""
        employees = []
        for i in range(1, self.num_employees + 1):
            dept = np.random.choice(self.departments, p=self.department_weights)
            is_malicious = self.risk_profiles[i - 1] == 'malicious'
            is_remote = random.random() < 0.3
            home_location = random.choice(self.locations)

            employee = {
                'employee_id': f'EMP{str(i).zfill(5)}',
                'name': fake.name(),
                'email': fake.email(),
                'department': dept,
                'position': random.choice(self.roles[dept]),
                'location': home_location,
                'is_remote': is_remote,
                'risk_profile': 'malicious' if is_malicious else 'normal',
                'tenure_days': random.randint(30, 365 * 5),
                'working_hours_start': random.randint(6, 10),
                'working_hours_end': random.randint(16, 20),
                'manager': fake.name(),
                'clearance_level': random.choice(['low', 'medium', 'high', 'critical']),
                'has_vpn': random.random() < 0.6,
                'device_id': fake.uuid4()[:8],
                'os': random.choice(['Windows 11', 'macOS Sonoma', 'Ubuntu 22.04']),
                'department_risk_factor': self._get_dept_risk(dept)
            }
            employees.append(employee)
        return pd.DataFrame(employees)

    def _get_dept_risk(self, dept: str) -> float:
        """Base risk factor by department."""
        risk_map = {
            'Engineering': 1.5, 'Finance': 1.3, 'Legal': 1.2, 'IT': 1.4,
            'HR': 1.0, 'Sales': 0.8, 'Marketing': 0.7, 'Operations': 0.9
        }
        return risk_map.get(dept, 1.0)

    def _get_activity_hour(self, emp: pd.Series, is_malicious: bool) -> int:
        """Get activity hour - malicious users work odd hours."""
        if is_malicious and random.random() < 0.4:
            return random.choice([1, 2, 3, 22, 23])
        work_start = emp['working_hours_start']
        work_end = emp['working_hours_end']
        if random.random() < 0.85:
            return random.randint(work_start, work_end)
        return random.randint(0, 23)

    def _weighted_employee_ids(self, employees: pd.DataFrame) -> np.ndarray:
        """Weighted employee selection so all employees get events."""
        malicious = employees[employees['risk_profile'] == 'malicious']
        # Malicious employees get more events for better signal
        weights = np.ones(len(employees))
        # Mark malicious employees index
        malicious_idx = employees.index[employees['risk_profile'] == 'malicious']
        for idx in malicious_idx:
            weights[idx] = 3.0
        weights = weights / weights.sum()
        return np.random.choice(employees['employee_id'].values, size=self.num_events, p=weights)

    def generate_events(self, employees: pd.DataFrame) -> pd.DataFrame:
        """Generate all activity events across vectors."""
        emp_map = employees.set_index('employee_id')
        emp_ids = self._weighted_employee_ids(employees)

        # Pre-generate timestamps
        seconds_in_range = self.num_days * 24 * 3600
        random_offsets = np.random.randint(0, seconds_in_range, size=self.num_events)
        base_ts = self.base_date.timestamp()

        rows = []
        for k in range(self.num_events):
            emp_id = emp_ids[k]
            emp = emp_map.loc[emp_id]
            is_malicious = emp['risk_profile'] == 'malicious'

            ts = datetime.fromtimestamp(base_ts + random_offsets[k])
            hour = self._get_activity_hour(emp, is_malicious)
            ts = ts.replace(hour=hour, minute=random.randint(0, 59), second=random.randint(0, 59))

            vector = random.choice(['login', 'usb', 'cloud', 'network', 'browser', 'email', 'application'])
            event = self._generate_vector_event(vector, emp, ts, is_malicious)
            event['log_id'] = fake.uuid4()[:12]
            event['employee_id'] = emp_id
            event['timestamp'] = ts.isoformat()
            event['hour'] = hour
            event['day_of_week'] = ts.weekday()
            event['is_weekend'] = ts.weekday() >= 5
            event['department'] = emp['department']
            event['risk_profile'] = emp['risk_profile']
            event['vector'] = vector
            rows.append(event)

        return pd.DataFrame(rows)

    def _generate_vector_event(self, vector: str, emp: pd.Series, ts: datetime, is_malicious: bool) -> dict:
        """Generate a single event for a specific vector."""
        if vector == 'login':
            return self._login_event(emp, is_malicious)
        if vector == 'usb':
            return self._usb_event(is_malicious)
        if vector == 'cloud':
            return self._cloud_event(emp, is_malicious)
        if vector == 'network':
            return self._network_event(is_malicious)
        if vector == 'browser':
            return self._browser_event(is_malicious)
        if vector == 'email':
            return self._email_event(emp, is_malicious)
        if vector == 'application':
            return self._application_event()
        return {}

    def _login_event(self, emp: pd.Series, is_malicious: bool) -> dict:
        """Login event with metadata."""
        home_country = random.choice(['United States', 'United Kingdom', 'Japan', 'Germany', 'Singapore', 'Australia'])
        if is_malicious and random.random() < 0.3:
            ip = f'{random.randint(10, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}'
            is_known_device = False
            country = random.choice(['China', 'Russia', 'Ukraine', 'Iran', 'North Korea'])
        else:
            ip = f'192.168.1.{random.randint(1, 50)}'
            is_known_device = True
            country = home_country

        return {
            'event_type': 'login',
            'ip_address': ip,
            'is_known_ip': ip.startswith('192.168.'),
            'device_id': emp['device_id'] if is_known_device else fake.uuid4()[:8],
            'is_new_device': not is_known_device,
            'browser': random.choice(self.browsers),
            'os': emp['os'],
            'login_success': random.random() < 0.9,
            'failed_attempts': random.randint(0, 3) if is_malicious else random.randint(0, 1),
            'country': country,
            'is_vpn_used': emp['has_vpn'] and random.random() < 0.3,
            'session_duration_minutes': random.randint(5, 480),
            'location': random.choice(self.locations)
        }

    def _usb_event(self, is_malicious: bool) -> dict:
        """USB activity event."""
        if is_malicious and random.random() < 0.5:
            files_copied = random.randint(50, 500)
            transfer_size = round(files_copied * random.uniform(0.5, 5), 2)
        else:
            files_copied = random.randint(1, 20)
            transfer_size = round(files_copied * random.uniform(0.1, 1), 2)

        return {
            'event_type': 'usb',
            'usb_action': random.choice(['insert', 'remove']),
            'device_id': fake.uuid4()[:8],
            'device_name': random.choice(['USB Drive', 'External HDD', 'SD Card', 'Phone Storage']),
            'vendor': random.choice(['SanDisk', 'Samsung', 'Kingston', 'Seagate', 'WD']),
            'files_copied': files_copied,
            'transfer_size_mb': transfer_size,
            'transfer_speed_mbps': round(random.uniform(10, 500), 1),
            'is_high_volume': files_copied > 100
        }

    def _cloud_event(self, emp: pd.Series, is_malicious: bool) -> dict:
        """Cloud upload event."""
        if is_malicious and random.random() < 0.4:
            upload_size = round(random.uniform(50, 1000), 2)
            file_count = random.randint(10, 100)
        else:
            upload_size = round(random.uniform(1, 50), 2)
            file_count = random.randint(1, 10)

        return {
            'event_type': 'cloud_upload',
            'cloud_service': random.choice(self.cloud_services),
            'upload_size_mb': upload_size,
            'file_count': file_count,
            'destination': random.choice(['Personal Account', 'Shared Drive', 'External Share']),
            'is_large_upload': upload_size > 100,
            'is_off_hours': emp['risk_profile'] == 'malicious' and random.random() < 0.5
        }

    def _network_event(self, is_malicious: bool) -> dict:
        """Network activity event."""
        if is_malicious and random.random() < 0.4:
            domain = random.choice(self.suspicious_domains)
            upload_volume = round(random.uniform(100, 1000), 2)
        else:
            domain = random.choice(self.normal_domains)
            upload_volume = round(random.uniform(1, 50), 2)

        return {
            'event_type': 'network',
            'destination_domain': domain,
            'destination_ip': fake.ipv4(),
            'protocol': random.choice(['HTTPS', 'SFTP', 'FTP', 'SSH', 'SMTP']),
            'upload_volume_mb': upload_volume,
            'download_volume_mb': round(random.uniform(10, 500), 2),
            'bandwidth_usage_mbps': round(random.uniform(1, 100), 1),
            'is_suspicious_domain': domain in self.suspicious_domains,
            'port': random.choice([443, 22, 21, 25, 8080, 8443]),
            'connection_duration_sec': random.randint(30, 3600)
        }

    def _browser_event(self, is_malicious: bool) -> dict:
        """Browser download/browsing event - metadata only."""
        if is_malicious and random.random() < 0.3:
            downloads = random.randint(5, 50)
            download_size = round(random.uniform(100, 2000), 2)
        else:
            downloads = random.randint(0, 10)
            download_size = round(random.uniform(1, 100), 2)

        return {
            'event_type': 'browser',
            'browser': random.choice(self.browsers),
            'downloads': downloads,
            'download_size_mb': download_size,
            'url_category': random.choice(['social', 'news', 'cloud_storage', 'file_share', 'webmail', 'internal']),
            'is_file_download': random.random() < 0.3,
            'is_suspicious_site': random.random() < 0.1 if is_malicious else random.random() < 0.02
        }

    def _email_event(self, emp: pd.Series, is_malicious: bool) -> dict:
        """Email metadata event - NO CONTENT INSPECTION."""
        if is_malicious and random.random() < 0.3:
            external_recipients = random.randint(5, 20)
            attachments = random.randint(3, 10)
        else:
            external_recipients = random.randint(0, 5)
            attachments = random.randint(0, 3)

        return {
            'event_type': 'email',
            'email_count': random.randint(1, 30),
            'sent_count': random.randint(1, 15),
            'received_count': random.randint(1, 20),
            'external_recipients': external_recipients,
            'attachment_count': attachments,
            'total_attachment_size_mb': round(attachments * random.uniform(0.1, 5), 2),
            'has_large_attachments': attachments > 5,
            'is_high_frequency': random.randint(1, 30) > 20,
            'is_to_external': external_recipients > 3
        }

    def _application_event(self) -> dict:
        """Application usage event."""
        return {
            'event_type': 'app_usage',
            'application': random.choice(self.applications),
            'duration_minutes': random.randint(5, 240),
            'category': random.choice(['development', 'communication', 'browsing', 'file_management', 'terminal']),
            'is_productivity_app': random.random() < 0.7
        }

    def generate_all(self) -> tuple:
        """Generate complete dataset with separate vector CSVs."""
        print("🚀 Generating SentinelAI synthetic dataset...")
        print(f"   Employees: {self.num_employees}, Events: {self.num_events}")

        print("📋 Generating employees...")
        employees = self.generate_employees()

        print("📊 Generating events...")
        events = self.generate_events(employees)

        # Split into per-vector CSV files
        os.makedirs('dataset', exist_ok=True)

        employees.to_csv('dataset/employees.csv', index=False)

        vector_files = {
            'login': 'login_events.csv',
            'usb': 'usb_events.csv',
            'cloud': 'cloud_events.csv',
            'network': 'network_events.csv',
            'browser': 'browser_events.csv',
            'email': 'email_events.csv',
            'application': 'application_events.csv'
        }

        breakdown = {}
        for vector, filename in vector_files.items():
            subset = events[events['vector'] == vector].copy()
            subset = subset.drop(columns=['vector'], errors='ignore')
            subset.to_csv(f'dataset/{filename}', index=False)
            breakdown[vector] = len(subset)

        # Save combined master activities file
        combined = events.copy()
        combined.drop(columns=['vector'], errors='ignore').to_csv('dataset/activities.csv', index=False)

        # Save metadata
        metadata = {
            'total_employees': len(employees),
            'total_events': len(events),
            'malicious_employees': int(len(employees[employees['risk_profile'] == 'malicious'])),
            'normal_employees': int(len(employees[employees['risk_profile'] == 'normal'])),
            'date_range': {
                'start': self.base_date.isoformat(),
                'end': datetime.now().isoformat()
            },
            'event_breakdown': breakdown
        }
        with open('dataset/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2, default=str)

        print(f"\n✅ Dataset generation complete!")
        print(f"   Employees: {len(employees)}")
        print(f"   Events: {len(events)}")
        print(f"   Malicious: {int(len(employees[employees['risk_profile'] == 'malicious']))}")
        print(f"   Normal: {int(len(employees[employees['risk_profile'] == 'normal']))}")
        print(f"   Event breakdown: {breakdown}")

        return employees, events


if __name__ == '__main__':
    generator = SentinelDatasetGenerator(num_employees=1000, num_events=200000)
    employees, events = generator.generate_all()
