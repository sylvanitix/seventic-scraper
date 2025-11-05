"""
Web Scraper Pro V2 - Fluid Pipeline
Universal scraping → Domain finding → Data enrichment (seamless flow)
"""

from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
import os
import json
import threading
import time
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# Configuration
OUTPUT_FOLDER = 'output'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Global state - Pipeline data in memory
pipeline_data = {
    'companies': [],  # From scraping
    'domains': [],    # From domain finder
    'enriched': []    # From enrichment
}

# Job tracking
jobs = {}
job_lock = threading.Lock()


class JobTracker:
    """Track job progress with in-memory data"""
    def __init__(self, job_id, job_type):
        self.job_id = job_id
        self.job_type = job_type
        self.status = 'running'
        self.progress = 0
        self.total = 0
        self.current_item = ''
        self.results = {}
        self.data = []  # Store results in memory
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

    def complete(self, results, data=None):
        self.status = 'completed'
        self.progress = self.total
        self.results = results
        if data:
            self.data = data
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
            'data': self.data,  # IMPORTANT: Include data in response
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'logs': self.logs[-50:]
        }


@app.route('/')
def index():
    return render_template('index_modern.html')


@app.route('/api/pipeline-status')
def get_pipeline_status():
    """Get current pipeline data status"""
    return jsonify({
        'companies_count': len(pipeline_data['companies']),
        'domains_count': len(pipeline_data['domains']),
        'enriched_count': len(pipeline_data['enriched']),
        'has_companies': len(pipeline_data['companies']) > 0,
        'has_domains': len(pipeline_data['domains']) > 0,
        'has_enriched': len(pipeline_data['enriched']) > 0
    })


@app.route('/api/scrape-universal', methods=['POST'])
def run_universal_scraper():
    """Universal scraper - any website"""
    job_id = f"scrape_{int(time.time())}"
    data = request.json
    url = data.get('url')
    max_pages = data.get('max_pages', 5)

    if not url:
        return jsonify({'error': 'URL required'}), 400

    with job_lock:
        jobs[job_id] = JobTracker(job_id, 'scraping')

    def scrape_task():
        try:
            from universal_scraper import scrape_companies_from_url

            tracker = jobs[job_id]
            tracker.add_log(f"Starting scrape of: {url}")

            def progress_callback(current, total, message):
                tracker.update(current, total, message)
                tracker.add_log(message)

            companies = scrape_companies_from_url(url, max_pages, progress_callback)

            tracker.add_log(f"Successfully scraped {len(companies)} companies")

            # Store in pipeline
            pipeline_data['companies'] = companies
            pipeline_data['domains'] = []  # Reset next stages
            pipeline_data['enriched'] = []

            tracker.complete({
                'total_companies': len(companies),
                'url': url,
                'pages_scraped': tracker.progress
            }, data=companies)

        except Exception as e:
            tracker = jobs[job_id]
            tracker.fail(e)
            tracker.add_log(f"Error: {str(e)}", 'error')

    thread = threading.Thread(target=scrape_task)
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/find-domains', methods=['POST'])
def run_domain_finder():
    """Find domains from scraped companies - CASCADE MODE"""
    job_id = f"domains_{int(time.time())}"

    if not pipeline_data['companies']:
        return jsonify({'error': 'No companies found. Run scraping first.'}), 400

    with job_lock:
        jobs[job_id] = JobTracker(job_id, 'domain_finding')

    def domain_task():
        try:
            from domain_finder import PremiumDomainFinder

            tracker = jobs[job_id]
            companies = pipeline_data['companies']

            tracker.add_log(f"🔍 CASCADE MODE: Processing {len(companies)} companies")
            tracker.update(0, len(companies))

            finder = PremiumDomainFinder()

            # CASCADE: Traite TOUTES les entreprises, même sans données précédentes
            cascade_results = []

            for i, company in enumerate(companies):
                company_name = company.get('name', '')
                tracker.update(i + 1, len(companies), f"Finding: {company_name}")

                # Recherche du domaine
                domain_result = finder.find_domain_single(company_name)

                # CASCADE: Combine données précédentes + nouvelles données
                cascade_item = {
                    **company,  # Données du scraping (name, url, etc.)
                    'domain': domain_result.get('domain', ''),
                    'domain_source': domain_result.get('source', ''),
                    'confidence_score': domain_result.get('confidence_score', 0),
                    'company_name': company_name  # Ensure company_name field
                }

                cascade_results.append(cascade_item)
                time.sleep(0.5)

            # Store in pipeline - CASCADE
            pipeline_data['domains'] = cascade_results
            pipeline_data['enriched'] = []  # Reset enrichment

            found = sum(1 for r in cascade_results if r.get('domain'))
            not_found = len(cascade_results) - found

            tracker.add_log(f"✅ {found} domains found, {not_found} not found (kept in cascade)")

            tracker.complete({
                'total_processed': len(cascade_results),
                'domains_found': found,
                'not_found': not_found
            }, data=cascade_results)

        except Exception as e:
            tracker = jobs[job_id]
            tracker.fail(e)
            tracker.add_log(f"Error: {str(e)}", 'error')

    thread = threading.Thread(target=domain_task)
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/enrich', methods=['POST'])
def run_enricher():
    """Enrich companies with domains - CASCADE MODE"""
    job_id = f"enrich_{int(time.time())}"

    if not pipeline_data['domains']:
        return jsonify({'error': 'No domains data. Run domain finder first.'}), 400

    with job_lock:
        jobs[job_id] = JobTracker(job_id, 'enrichment')

    def enrich_task():
        try:
            from company_enricher import CompanyEnricher

            tracker = jobs[job_id]
            all_companies = pipeline_data['domains']

            # CASCADE: Identifie ceux à traiter (avec domaines)
            companies_to_enrich = [c for c in all_companies if c.get('domain')]
            companies_without_domain = [c for c in all_companies if not c.get('domain')]

            tracker.add_log(f"🔍 CASCADE MODE: {len(companies_to_enrich)} to enrich, {len(companies_without_domain)} without domains (kept)")
            tracker.update(0, len(companies_to_enrich))

            enricher = CompanyEnricher()
            enriched_results = []
            no_domain_results = []

            # Enrichit seulement ceux avec domaines
            for i, company_data in enumerate(companies_to_enrich):
                company_name = company_data.get('company_name', company_data.get('name', ''))
                domain = company_data.get('domain', '')

                tracker.update(i + 1, len(companies_to_enrich), f"Enriching: {company_name}")

                # Enrichissement
                enrich_result = enricher.enrich_single_company(company_name, domain)

                # CASCADE: Combine TOUTES les données précédentes + nouvelles
                cascade_item = {
                    **company_data,  # Données du scraping + domain finder
                    'company_email': enrich_result.get('company_email', ''),
                    'company_phone': enrich_result.get('company_phone', ''),
                    'company_linkedin': enrich_result.get('company_linkedin', ''),
                    'company_address': enrich_result.get('company_address', ''),
                    'enrichment_status': 'enriched'
                }

                enriched_results.append(cascade_item)
                time.sleep(1)

            # CASCADE: Ajoute aussi ceux SANS domaines (avec champs vides)
            for company_data in companies_without_domain:
                cascade_item = {
                    **company_data,  # Données du scraping + domain finder
                    'company_email': '',
                    'company_phone': '',
                    'company_linkedin': '',
                    'company_address': '',
                    'enrichment_status': 'no_domain'
                }
                no_domain_results.append(cascade_item)

            # CASCADE: TRIER - Données enrichies en PREMIER, puis sans domaines
            cascade_results = enriched_results + no_domain_results

            # Store in pipeline - CASCADE COMPLET
            pipeline_data['enriched'] = cascade_results

            emails_found = sum(1 for r in cascade_results if r.get('company_email'))
            phones_found = sum(1 for r in cascade_results if r.get('company_phone'))
            linkedin_found = sum(1 for r in cascade_results if r.get('company_linkedin'))

            tracker.add_log(f"✅ CASCADE: {len(cascade_results)} total companies in final dataset")
            tracker.add_log(f"   - {len(enriched_results)} enriched (shown FIRST)")
            tracker.add_log(f"   - {len(no_domain_results)} without domains (shown LAST with empty fields)")

            tracker.complete({
                'total_companies': len(cascade_results),
                'enriched': len(companies_to_enrich),
                'without_domains': len(companies_without_domain),
                'emails_found': emails_found,
                'phones_found': phones_found,
                'linkedin_found': linkedin_found
            }, data=cascade_results)

        except Exception as e:
            tracker = jobs[job_id]
            tracker.fail(e)
            tracker.add_log(f"Error: {str(e)}", 'error')

    thread = threading.Thread(target=enrich_task)
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/full-pipeline', methods=['POST'])
def run_full_pipeline():
    """Run complete pipeline: Scrape → Find Domains → Enrich (all in one)"""
    job_id = f"pipeline_{int(time.time())}"
    data = request.json
    url = data.get('url')
    max_pages = data.get('max_pages', 10)

    if not url:
        return jsonify({'error': 'URL required'}), 400

    with job_lock:
        jobs[job_id] = JobTracker(job_id, 'full_pipeline')

    def pipeline_task():
        try:
            from lead_pipeline import LeadPipeline

            tracker = jobs[job_id]
            tracker.add_log(f"Starting full pipeline for: {url}")
            tracker.add_log(f"Max pages: {max_pages}")

            def progress_callback(current, total, message):
                tracker.update(current, total, message)
                tracker.add_log(message)

            # Run full pipeline
            pipeline = LeadPipeline()
            results = pipeline.run(
                url=url,
                max_pages=max_pages,
                export_csv=False,  # Don't auto-export, user will choose
                progress_callback=progress_callback
            )

            if results:
                # Store in pipeline data
                pipeline_data['companies'] = [{'name': name} for name in results['companies_scraped']]
                pipeline_data['domains'] = results['domains_found']
                pipeline_data['enriched'] = results['companies_enriched']

                tracker.add_log(f"Pipeline complete!")
                tracker.complete({
                    'total_companies': results['stats']['total_companies_scraped'],
                    'domains_found': results['stats']['domains_found'],
                    'companies_enriched': results['stats']['companies_enriched'],
                    'emails_found': results['stats']['emails_found'],
                    'phones_found': results['stats']['phones_found'],
                    'linkedin_found': results['stats']['linkedin_found'],
                    'total_time': results['stats']['total_time_seconds']
                }, data=results['companies_enriched'])
            else:
                tracker.fail("Pipeline returned no results")

        except Exception as e:
            tracker = jobs[job_id]
            tracker.fail(e)
            tracker.add_log(f"Error: {str(e)}", 'error')

    thread = threading.Thread(target=pipeline_task)
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/export/<stage>', methods=['POST'])
def export_data(stage):
    """Export data from any pipeline stage"""
    format = request.json.get('format', 'csv')

    # Map stage names
    stage_map = {
        'companies': 'companies',
        'domains': 'domains',
        'enriched': 'enriched'
    }

    if stage not in stage_map:
        return jsonify({'error': f'Invalid stage: {stage}'}), 400

    actual_stage = stage_map[stage]

    if actual_stage not in pipeline_data or not pipeline_data[actual_stage]:
        return jsonify({'error': f'No data in {stage} stage'}), 400

    data = pipeline_data[actual_stage]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{stage}_{timestamp}"

    try:
        if format == 'csv':
            filepath = os.path.join(OUTPUT_FOLDER, f'{filename}.csv')
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
        elif format == 'json':
            filepath = os.path.join(OUTPUT_FOLDER, f'{filename}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format == 'xlsx':
            filepath = os.path.join(OUTPUT_FOLDER, f'{filename}.xlsx')
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
        else:
            return jsonify({'error': f'Invalid format: {format}'}), 400

        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/<job_id>')
def get_job_status(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(jobs[job_id].to_dict())


@app.route('/api/jobs/<job_id>/logs')
def get_job_logs(job_id):
    """Get all logs for a job"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify({
        'job_id': job_id,
        'status': jobs[job_id].status,
        'logs': jobs[job_id].logs
    })


@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    """API configuration"""
    if request.method == 'GET':
        return jsonify({
            'pappers_configured': bool(os.getenv('PAPPERS_API_KEY')),
            'hunter_configured': bool(os.getenv('HUNTER_API_KEY'))
        })
    else:
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

        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        return jsonify({'success': True})


# ========================================
# SUPERVISED SCRAPING ROUTES
# ========================================

@app.route('/api/analyze-patterns', methods=['POST'])
def analyze_patterns():
    """Analyze URL and detect repeating patterns"""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'success': False, 'error': 'URL required'}), 400

    try:
        from smart_pattern_detector import SmartPatternDetector

        detector = SmartPatternDetector()
        result = detector.analyze_url(url)

        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scrape-supervised', methods=['POST'])
def scrape_supervised():
    """Scrape with user-defined mapping"""
    job_id = f"supervised_{int(time.time())}"
    data = request.json

    url = data.get('url')
    pattern_signature = data.get('pattern_signature')  # NOUVELLE: signature au lieu d'index
    pattern_index = data.get('pattern_index', 0)  # Fallback
    company_column = data.get('company_column', 'text')
    max_pages = data.get('max_pages', 5)

    if not url:
        return jsonify({'error': 'URL required'}), 400

    with job_lock:
        jobs[job_id] = JobTracker(job_id, 'supervised_scraping')

    def supervised_scrape_task():
        try:
            from smart_pattern_detector import SmartPatternDetector

            tracker = jobs[job_id]
            tracker.add_log(f"Starting supervised scraping: {url}")
            if pattern_signature:
                tracker.add_log(f"Pattern signature: {pattern_signature}, Column: {company_column}")
            else:
                tracker.add_log(f"Pattern index: {pattern_index}, Column: {company_column}")
            tracker.add_log(f"Max pages: {max_pages}")

            detector = SmartPatternDetector()

            # Logger function pour tracer tout
            def log_message(message):
                tracker.add_log(message)
                print(message)  # Also print to console

            tracker.update(0, max_pages, f"Initializing scraper...")

            companies = detector.scrape_with_mapping(
                url=url,
                pattern_signature=pattern_signature,  # Envoie la signature
                pattern_index=pattern_index,  # Fallback si pas de signature
                company_name_column=company_column,
                max_pages=max_pages,
                logger=log_message
            )

            tracker.add_log(f"✅ Successfully scraped {len(companies)} companies")

            # Store in pipeline
            pipeline_data['companies'] = companies
            pipeline_data['domains'] = []
            pipeline_data['enriched'] = []

            tracker.complete({
                'total_companies': len(companies),
                'url': url
            }, data=companies)

        except Exception as e:
            tracker = jobs[job_id]
            tracker.fail(e)
            tracker.add_log(f"❌ Error: {str(e)}", 'error')
            import traceback
            tracker.add_log(traceback.format_exc(), 'error')

    thread = threading.Thread(target=supervised_scrape_task)
    thread.start()

    return jsonify({'job_id': job_id})


@app.route('/api/export-direct', methods=['POST'])
def export_direct():
    """Export data directly from request"""
    data = request.json.get('data', [])
    format = request.json.get('format', 'csv')

    if not data:
        return jsonify({'error': 'No data to export'}), 400

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"companies_{timestamp}"

    try:
        if format == 'csv':
            filepath = os.path.join(OUTPUT_FOLDER, f'{filename}.csv')
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8')
        elif format == 'json':
            filepath = os.path.join(OUTPUT_FOLDER, f'{filename}.json')
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif format == 'xlsx':
            filepath = os.path.join(OUTPUT_FOLDER, f'{filename}.xlsx')
            df = pd.DataFrame(data)
            df.to_excel(filepath, index=False, engine='openpyxl')
        else:
            return jsonify({'error': f'Invalid format: {format}'}), 400

        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
