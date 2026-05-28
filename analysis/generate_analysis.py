#!/usr/bin/env python3
"""
VulnSniffer Analysis Generator
Generates CSVs and visualizations for vulnerability analysis from mining, AST scanning, and audit data.
"""

import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Configure matplotlib for better quality
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

class VulnerabilityAnalyzer:
    def __init__(self, base_path="/Users/leandro/git/VulnSniffer"):
        self.base_path = Path(base_path)
        self.csv_dir = self.base_path / "csv"
        self.output_dir = self.base_path / "analysis_output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Load data
        self.mining_df = self._load_csv("results_mining.csv")
        self.ast_df = self._load_csv("results_ast_analysis.csv")
        self.audit_df = self._load_csv("results_audit.csv")
        
    def _load_csv(self, filename):
        """Load CSV file with error handling"""
        try:
            filepath = self.csv_dir / filename
            return pd.read_csv(filepath)
        except Exception as e:
            print(f"Warning: Could not load {filename}: {e}")
            return pd.DataFrame()
    
    def generate_vulnerability_distribution(self):
        """Generate vulnerability distribution CSV"""
        if self.ast_df.empty:
            return
        
        vuln_counts = self.ast_df['Type'].value_counts().reset_index()
        vuln_counts.columns = ['Vulnerability Type', 'Count']
        vuln_counts['Percentage'] = (vuln_counts['Count'] / vuln_counts['Count'].sum() * 100).round(2)
        
        output_file = self.output_dir / "vulnerability_distribution.csv"
        vuln_counts.to_csv(output_file, index=False)
        print(f"✓ Generated: {output_file.name}")
        return vuln_counts
    
    def generate_repository_status(self):
        """Generate repository vulnerability status CSV (vulnerable vs secure)"""
        if self.mining_df.empty:
            return
        
        total_repos = len(self.mining_df)
        
        # Get repositories with vulnerabilities
        vulnerable_repos = set(self.ast_df['Repo'].unique()) if not self.ast_df.empty else set()
        num_vulnerable = len(vulnerable_repos)
        num_secure = total_repos - num_vulnerable
        
        status_data = {
            'Status': ['Vulnerable', 'Secure'],
            'Count': [num_vulnerable, num_secure],
            'Percentage': [
                round(num_vulnerable / total_repos * 100, 2),
                round(num_secure / total_repos * 100, 2)
            ]
        }
        
        status_df = pd.DataFrame(status_data)
        output_file = self.output_dir / "repository_status.csv"
        status_df.to_csv(output_file, index=False)
        print(f"✓ Generated: {output_file.name}")
        return status_df
    
    def generate_audit_status(self):
        """Generate audit status summary CSV"""
        if self.audit_df.empty:
            return
        
        audit_counts = self.audit_df['Status'].value_counts().reset_index()
        audit_counts.columns = ['Audit Status', 'Count']
        audit_counts['Percentage'] = (audit_counts['Count'] / audit_counts['Count'].sum() * 100).round(2)
        
        output_file = self.output_dir / "audit_status.csv"
        audit_counts.to_csv(output_file, index=False)
        print(f"✓ Generated: {output_file.name}")
        return audit_counts
    
    def generate_confirmed_cases_by_type(self):
        """Generate confirmed vulnerability cases by type"""
        if self.audit_df.empty:
            return
        
        confirmed_df = self.audit_df[self.audit_df['Status'] != 'NAO_SE_APLICA']
        confirmed_counts = confirmed_df['Type'].value_counts().reset_index()
        confirmed_counts.columns = ['Vulnerability Type', 'Confirmed Cases']
        
        output_file = self.output_dir / "confirmed_cases_by_type.csv"
        confirmed_counts.to_csv(output_file, index=False)
        print(f"✓ Generated: {output_file.name}")
        return confirmed_counts
    
    def generate_detailed_audit_report(self):
        """Generate detailed audit report with summary statistics"""
        if self.audit_df.empty:
            return
        
        summary_data = []
        for vuln_type in self.audit_df['Type'].unique():
            type_data = self.audit_df[self.audit_df['Type'] == vuln_type]
            summary_data.append({
                'Vulnerability Type': vuln_type,
                'Total Found': len(type_data),
                'Status NAO_SE_APLICA': len(type_data[type_data['Status'] == 'NAO_SE_APLICA']),
                'With Review Notes': len(type_data[type_data['ReviewerNote'].notna() & (type_data['ReviewerNote'] != '')]),
                'Percentage with Notes': round(len(type_data[type_data['ReviewerNote'].notna() & (type_data['ReviewerNote'] != '')]) / len(type_data) * 100, 2)
            })
        
        report_df = pd.DataFrame(summary_data)
        output_file = self.output_dir / "detailed_audit_report.csv"
        report_df.to_csv(output_file, index=False)
        print(f"✓ Generated: {output_file.name}")
        return report_df
    
    def plot_repository_status_pie(self):
        """Generate pie chart: Vulnerable vs Secure repositories"""
        status_df = self.generate_repository_status()
        if status_df is None:
            return
        
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = ['#ff6b6b', '#51cf66']
        wedges, texts, autotexts = ax.pie(
            status_df['Count'],
            labels=status_df['Status'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
        
        ax.set_title('Repository Status Distribution\n(Vulnerable vs Secure)', 
                    fontsize=14, weight='bold', pad=20)
        
        plt.tight_layout()
        output_file = self.output_dir / "01_repository_status_pie.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generated: {output_file.name}")
    
    def plot_vulnerability_distribution_bar(self):
        """Generate bar chart: Vulnerability types distribution"""
        vuln_df = self.generate_vulnerability_distribution()
        if vuln_df is None:
            return
        
        fig, ax = plt.subplots(figsize=(12, 7))
        colors = sns.color_palette("husl", len(vuln_df))
        
        bars = ax.barh(vuln_df['Vulnerability Type'], vuln_df['Count'], color=colors)
        ax.set_xlabel('Count', fontsize=12, weight='bold')
        ax.set_ylabel('Vulnerability Type', fontsize=12, weight='bold')
        ax.set_title('Vulnerability Distribution by Type', fontsize=14, weight='bold', pad=20)
        
        # Add value labels
        for i, (count, pct) in enumerate(zip(vuln_df['Count'], vuln_df['Percentage'])):
            ax.text(count + 0.5, i, f'{count} ({pct}%)', va='center', fontsize=10, weight='bold')
        
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        output_file = self.output_dir / "02_vulnerability_distribution_bar.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generated: {output_file.name}")
    
    def plot_confirmed_cases_bar(self):
        """Generate bar chart: Confirmed vulnerability cases by type"""
        confirmed_df = self.generate_confirmed_cases_by_type()
        if confirmed_df is None or confirmed_df.empty:
            confirmed_df = self.generate_audit_status()
            if confirmed_df is None or confirmed_df.empty:
                return
        
        fig, ax = plt.subplots(figsize=(12, 7))
        colors = sns.color_palette("Set2", len(confirmed_df))
        
        bars = ax.bar(range(len(confirmed_df)), 
                      confirmed_df.iloc[:, 1], 
                      color=colors)
        ax.set_xlabel('Vulnerability Type', fontsize=12, weight='bold')
        ax.set_ylabel('Count', fontsize=12, weight='bold')
        ax.set_title('Confirmed Vulnerability Cases by Type', fontsize=14, weight='bold', pad=20)
        ax.set_xticks(range(len(confirmed_df)))
        ax.set_xticklabels(confirmed_df.iloc[:, 0], rotation=45, ha='right')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, confirmed_df.iloc[:, 1])):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                   str(value), ha='center', va='bottom', fontsize=10, weight='bold')
        
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        output_file = self.output_dir / "03_confirmed_cases_bar.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generated: {output_file.name}")
    
    def plot_audit_status_pie(self):
        """Generate pie chart: Audit status distribution"""
        audit_df = self.generate_audit_status()
        if audit_df is None:
            return
        
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = sns.color_palette("pastel", len(audit_df))
        
        wedges, texts, autotexts = ax.pie(
            audit_df['Count'],
            labels=audit_df['Audit Status'],
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 11, 'weight': 'bold'}
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
        
        ax.set_title('Audit Status Distribution', fontsize=14, weight='bold', pad=20)
        
        plt.tight_layout()
        output_file = self.output_dir / "04_audit_status_pie.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generated: {output_file.name}")
    
    def plot_vulnerability_accuracy(self):
        """Generate accuracy visualization: detected vs confirmed vulnerabilities"""
        if self.ast_df.empty or self.audit_df.empty:
            return
        
        # Count detected vs confirmed for each type
        detected_types = self.ast_df['Type'].value_counts().reset_index()
        detected_types.columns = ['Type', 'Detected']
        
        audit_types = self.audit_df[self.audit_df['Status'] != 'NAO_SE_APLICA']['Type'].value_counts().reset_index()
        audit_types.columns = ['Type', 'Confirmed']
        
        merged = pd.merge(detected_types, audit_types, on='Type', how='left')
        merged['Confirmed'] = merged['Confirmed'].fillna(0).astype(int)
        merged['Accuracy %'] = (merged['Confirmed'] / merged['Detected'] * 100).round(2)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        x = range(len(merged))
        width = 0.35
        
        bars1 = ax.bar([i - width/2 for i in x], merged['Detected'], width, label='Detected', color='#3498db')
        bars2 = ax.bar([i + width/2 for i in x], merged['Confirmed'], width, label='Confirmed', color='#e74c3c')
        
        ax.set_xlabel('Vulnerability Type', fontsize=12, weight='bold')
        ax.set_ylabel('Count', fontsize=12, weight='bold')
        ax.set_title('Vulnerability Detection vs Confirmation Accuracy', fontsize=14, weight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(merged['Type'], rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "05_accuracy_comparison.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generated: {output_file.name}")
    
    def plot_pipeline_funnel(self):
        """Generate funnel chart: Mining -> AST -> Audit pipeline"""
        if self.mining_df.empty:
            return
        
        total_repos = len(self.mining_df)
        scanned_repos = len(self.ast_df['Repo'].unique()) if not self.ast_df.empty else 0
        audited_repos = len(self.audit_df['Repo'].unique()) if not self.audit_df.empty else 0
        
        stages = ['Total Repositories', 'With Vulnerabilities Found', 'Audited Repositories']
        counts = [total_repos, scanned_repos, audited_repos]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create funnel
        colors = ['#3498db', '#e74c3c', '#f39c12']
        for i, (stage, count, color) in enumerate(zip(stages, counts, colors)):
            width = 0.8 - (i * 0.15)
            ax.barh(i, count, height=0.6, left=(1-width)/2, color=color, alpha=0.8, edgecolor='black', linewidth=2)
            ax.text(count/2, i, f'{stage}\n{count}', ha='center', va='center', fontsize=11, weight='bold', color='white')
        
        ax.set_yticks(range(len(stages)))
        ax.set_yticklabels(stages)
        ax.set_xlabel('Count', fontsize=12, weight='bold')
        ax.set_title('VulnSniffer Analysis Pipeline Funnel', fontsize=14, weight='bold', pad=20)
        ax.set_xlim(0, total_repos * 1.1)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        output_file = self.output_dir / "06_pipeline_funnel.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generated: {output_file.name}")
    
    def plot_framework_distribution(self):
        """Generate bar chart: Framework distribution in repositories"""
        if self.mining_df.empty:
            return
        
        # Extract framework info
        frameworks = self.mining_df['Framework'].str.extract(r'\(([^)]+)\)', expand=False)
        framework_counts = frameworks.value_counts().head(10)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        colors = sns.color_palette("coolwarm", len(framework_counts))
        
        bars = ax.barh(framework_counts.index, framework_counts.values, color=colors)
        ax.set_xlabel('Count', fontsize=12, weight='bold')
        ax.set_ylabel('Framework', fontsize=12, weight='bold')
        ax.set_title('Top 10 Frameworks in Analyzed Repositories', fontsize=14, weight='bold', pad=20)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, framework_counts.values)):
            ax.text(value + 0.2, i, str(value), va='center', fontsize=10, weight='bold')
        
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        output_file = self.output_dir / "07_framework_distribution.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Generated: {output_file.name}")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        report_lines = [
            "# VulnSniffer Analysis Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary Statistics",
            ""
        ]
        
        if not self.mining_df.empty:
            total_repos = len(self.mining_df)
            report_lines.append(f"- **Total Repositories Analyzed**: {total_repos}")
        
        if not self.ast_df.empty:
            total_vulns = len(self.ast_df)
            unique_repos_with_vulns = len(self.ast_df['Repo'].unique())
            report_lines.extend([
                f"- **Total Vulnerabilities Detected**: {total_vulns}",
                f"- **Repositories with Vulnerabilities**: {unique_repos_with_vulns}",
            ])
        
        if not self.audit_df.empty:
            total_audited = len(self.audit_df)
            report_lines.append(f"- **Total Items Audited**: {total_audited}")
        
        report_lines.extend([
            "",
            "## Vulnerability Types",
            ""
        ])
        
        if not self.ast_df.empty:
            vuln_types = self.ast_df['Type'].value_counts()
            for vuln_type, count in vuln_types.items():
                percentage = count / len(self.ast_df) * 100
                report_lines.append(f"- **{vuln_type}**: {count} ({percentage:.1f}%)")
        
        report_lines.extend([
            "",
            "## Generated Files",
            "",
            "### CSV Files:",
            "- `vulnerability_distribution.csv` - Distribution of vulnerability types",
            "- `repository_status.csv` - Repository status (vulnerable/secure)",
            "- `audit_status.csv` - Audit status summary",
            "- `confirmed_cases_by_type.csv` - Confirmed cases by vulnerability type",
            "- `detailed_audit_report.csv` - Detailed audit report with statistics",
            "",
            "### Visualization Files:",
            "- `01_repository_status_pie.png` - Pie chart of repository status",
            "- `02_vulnerability_distribution_bar.png` - Bar chart of vulnerability distribution",
            "- `03_confirmed_cases_bar.png` - Bar chart of confirmed cases",
            "- `04_audit_status_pie.png` - Pie chart of audit status",
            "- `05_accuracy_comparison.png` - Detected vs confirmed comparison",
            "- `06_pipeline_funnel.png` - Pipeline funnel visualization",
            "- `07_framework_distribution.png` - Framework distribution chart",
        ])
        
        report_file = self.output_dir / "ANALYSIS_REPORT.md"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))
        
        print(f"✓ Generated: {report_file.name}")
    
    def run_all(self):
        """Execute all analysis and visualization tasks"""
        print("\n" + "="*70)
        print("VulnSniffer Analysis Generator")
        print("="*70 + "\n")
        
        print("📊 Generating CSV Reports...")
        print("-" * 70)
        self.generate_vulnerability_distribution()
        self.generate_repository_status()
        self.generate_audit_status()
        self.generate_confirmed_cases_by_type()
        self.generate_detailed_audit_report()
        
        print("\n📈 Generating Visualizations...")
        print("-" * 70)
        self.plot_repository_status_pie()
        self.plot_vulnerability_distribution_bar()
        self.plot_confirmed_cases_bar()
        self.plot_audit_status_pie()
        self.plot_vulnerability_accuracy()
        self.plot_pipeline_funnel()
        self.plot_framework_distribution()
        
        print("\n📄 Generating Summary Report...")
        print("-" * 70)
        self.generate_summary_report()
        
        print("\n" + "="*70)
        print(f"✅ Analysis Complete!")
        print(f"📁 All files saved to: {self.output_dir}")
        print("="*70 + "\n")


def main():
    """Main entry point"""
    analyzer = VulnerabilityAnalyzer()
    analyzer.run_all()


if __name__ == "__main__":
    main()
