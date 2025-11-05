"""
Web Scraper Pro - Flask Web Application
Professional web interface for scraping, domain finding, and data enrichment
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
import os
import json
import threading
import time
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename

# Import our existing tools
import sys
sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global state for job tracking
jobs = {}
job_lock = threading.Lock()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class JobTracker:
    """Track job progress"""
    def __init__(self, job_id, job_type):
        self.job_id = job_id
        self.job_type = job_type
        self.status = 'running'
        self.progress = 0
        self.total = 0
        self.current_item = ''
        self.results = {}
        self.error = None
        self.started_at = datetime.now()
        self.completed_at = None
        self.logs = []

    def update(self, progress, total, current_item=''):
        self.progress = progress
        self.total = total
        self.current_item = current_item

    def add_log(self, message, level='info'):
        self.logs.append({
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        })

    def complete(self, results):
        self.status = 'completed'
        self.progress = self.total
        self.results = results
        self.completed_at = datetime.now()

    def fail(self, error):
        self.status = 'failed'
        self.error = str(error)
        self.completed_at = datetime.now()

    def to_dict(self):
        return {
            'job_id': self.job_id,
            'job_type': self.job_type,
            'status': self.status,
            'progress': self.progress,
            'total': self.total,
            'current_item': self.current_item,
            'results': self.results,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'logs': self.logs[-50:]  # Last 50 logs
        }


@app.route('/')
def index():
    """Dashboard page"""
    return render_template('index.html')


@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    stats = {
        'total_companies': 0,
        'domains_found': 0,
        'emails_found': 0,
        'active_jobs': sum(1 for j in jobs.values() if j.status == 'running')
    }

    # Check if we have previous results
    if os.path.exists('output/equipauto_exhibitors_clean.json'):
        with open('output/equipauto_exhibitors_clean.json', 'r') as f:
            data = json.load(f)
            stats['total_companies'] = len(data)

    if os.path.exists('output/company_domains_premium.json'):
        with open('output/company_domains_premium.json', 'r') as f:
            data = json.load(f)
            stats['domains_found'] = sum(1 for d in data if d.get('domain'))

    if os.path.exists('output/company_enriched_data.json'):
        with open('output/company_enriched_data.json', 'r') as f:
            data = json.load(f)
            stats['emails_found'] = sum(1 for d in data if d.get('company_email'))

    return jsonify(stats)


@app.route('/api/scrape', methods=['POST'])
def run_scraper():
    """Run the Equipauto scraper"""
    job_id = f"scrape_{int(time.time())}"

    with job_lock:
        jobs[job_id] = JobTracker(job_id, 'scraping')

    def scrape_task():
        try:
            from equipauto_scraper_fast import EquipautoScraper

            tracker = jobs[job_id]
            tracker.add_log("Starting Equipauto scraper...")

            scraper = EquipautoScraper()
            scraper.setup_driver()

            tracker.add_log("Navigating to Equipauto website...")
            data = scraper.scrape_equipauto()

            tracker.update(len(data), len(data), f"Scraped {len(data)} exhibitors")
            tracker.add_log(f"Successfully scraped {len(data)} exhibitors")

            scraper.export_data(data, 'output/equipauto_exhibitors')
            scraper.close()

            # Run clean_data
            tracker.add_log("Cleaning and deduplicating data...")
            from clean_data import clean_and_deduplicate
            clean_count = clean_and_deduplicate()

            tracker.complete({
                'total_scraped': len(data),
                'unique_companies': clean_count,
                'files': ['equipauto_exhibitors.json', 'equipauto_exhibitors_clean.json']
            })

        except Exception as e:
            tracker = jobs[job_id]
            tracker.fail(e)
            tracker.add_log(f"Error: {str(e)}", 'error')

    thread = threading.Thread(target=scrape_task)
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/find-domains', methods=['POST'])
def run_domain_finder():
    """Run domain finder"""
    job_id = f"domains_{int(time.time())}"
    data = request.json
    max_results = data.get('max_results')  # None = all

    with job_lock:
        jobs[job_id] = JobTracker(job_id, 'domain_finding')

    def domain_task():
        try:
            from domain_finder import PremiumDomainFinder

            tracker = jobs[job_id]
            tracker.add_log("Loading companies...")

            # Load companies
            with open('output/equipauto_exhibitors_clean.json', 'r') as f:
                exhibitors = json.load(f)

            company_names = [ex['name'] for ex in exhibitors]

            if max_results:
                company_names = company_names[:max_results]
                tracker.add_log(f"Processing first {max_results} companies")
            else:
                tracker.add_log(f"Processing all {len(company_names)} companies")

            tracker.update(0, len(company_names))

            finder = PremiumDomainFinder()
            results = []

            for i, company_name in enumerate(company_names):
                tracker.update(i + 1, len(company_names), f"Finding domain for: {company_name}")
                result = finder.find_domain_single(company_name)
                results.append(result)
                time.sleep(1)

            finder.results = results
            finder.export_results('output/company_domains_premium')

            found = sum(1 for r in results if r['domain'])

            tracker.complete({
                'total_processed': len(results),
                'domains_found': found,
                'not_found': len(results) - found,
                'files': ['company_domains_premium.json', 'company_domains_premium.csv']
            })

        except Exception as e:
            tracker = jobs[job_id]
            tracker.fail(e)
            tracker.add_log(f"Error: {str(e)}", 'error')

    thread = threading.Thread(target=domain_task)
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/enrich', methods=['POST'])
def run_enricher():
    """Run data enrichment"""
    job_id = f"enrich_{int(time.time())}"
    data = request.json
    max_results = data.get('max_results')  # None = all

    with job_lock:
        jobs[job_id] = JobTracker(job_id, 'enrichment')

    def enrich_task():
        try:
            from company_enricher import CompanyEnricher

            tracker = jobs[job_id]
            tracker.add_log("Loading companies with domains...")

            # Load from CSV
            df = pd.read_csv('output/company_domains_premium.csv')
            companies_to_enrich = [
                {'company_name': row['company_name'], 'domain': row['domain']}
                for _, row in df.iterrows()
                if pd.notna(row.get('domain')) and row.get('domain')
            ]

            if max_results:
                companies_to_enrich = companies_to_enrich[:max_results]
                tracker.add_log(f"Processing first {max_results} companies")
            else:
                tracker.add_log(f"Processing all {len(companies_to_enrich)} companies")

            tracker.update(0, len(companies_to_enrich))

            enricher = CompanyEnricher()
            results = []

            for i, company_data in enumerate(companies_to_enrich):
                company_name = company_data['company_name']
                domain = company_data['domain']

                tracker.update(i + 1, len(companies_to_enrich), f"Enriching: {company_name}")
                result = enricher.enrich_single_company(company_name, domain)
                results.append(result)
                time.sleep(1.5)

            enricher.export_results(results, 'output/company_enriched_data')

            emails_found = sum(1 for r in results if r['company_email'])
            phones_found = sum(1 for r in results if r['company_phone'])
            linkedin_found = sum(1 for r in results if r['company_linkedin'])

            tracker.complete({
                'total_processed': len(results),
                'emails_found': emails_found,
                'phones_found': phones_found,
                'linkedin_found': linkedin_found,
                'files': ['company_enriched_data.json', 'company_enriched_data.csv']
            })

        except Exception as e:
            tracker = jobs[job_id]
            tracker.fail(e)
            tracker.add_log(f"Error: {str(e)}", 'error')

    thread = threading.Thread(target=enrich_task)
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/jobs/<job_id>')
def get_job_status(job_id):
    """Get job status and progress"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify(jobs[job_id].to_dict())


@app.route('/api/jobs')
def get_all_jobs():
    """Get all jobs"""
    return jsonify([job.to_dict() for job in jobs.values()])


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download result file"""
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404

    return send_file(filepath, as_attachment=True)


@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    """Get or update API keys configuration"""
    if request.method == 'GET':
        config = {
            'pappers_api_key': os.getenv('PAPPERS_API_KEY', ''),
            'hunter_api_key': os.getenv('HUNTER_API_KEY', ''),
            'pappers_configured': bool(os.getenv('PAPPERS_API_KEY')),
            'hunter_configured': bool(os.getenv('HUNTER_API_KEY'))
        }
        return jsonify(config)

    else:  # POST
        data = request.json

        # Update .env file
        env_path = '.env'
        env_vars = {}

        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_vars[key] = value

        if 'pappers_api_key' in data:
            env_vars['PAPPERS_API_KEY'] = data['pappers_api_key']
            os.environ['PAPPERS_API_KEY'] = data['pappers_api_key']

        if 'hunter_api_key' in data:
            env_vars['HUNTER_API_KEY'] = data['hunter_api_key']
            os.environ['HUNTER_API_KEY'] = data['hunter_api_key']

        # Write back to .env
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        return jsonify({'success': True})


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
