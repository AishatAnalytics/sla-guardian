import boto3
import requests
import json
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ses = boto3.client('ses', region_name=os.getenv('AWS_REGION'))

# Endpoints to monitor
ENDPOINTS = [
    {
        'name': 'AWS Health API',
        'url': 'https://health.amazonaws.com',
        'method': 'GET',
        'timeout': 5
    },
    {
        'name': 'GitHub API',
        'url': 'https://api.github.com',
        'method': 'GET',
        'timeout': 5
    },
    {
        'name': 'OpenWeatherMap API',
        'url': 'https://api.openweathermap.org',
        'method': 'GET',
        'timeout': 5
    }
]

def check_endpoint(endpoint):
    print(f"Checking {endpoint['name']}...")
    result = {
        'name': endpoint['name'],
        'url': endpoint['url'],
        'timestamp': datetime.now().isoformat(),
        'status': 'unknown',
        'response_time_ms': None,
        'status_code': None,
        'error': None
    }

    try:
        start = time.time()
        response = requests.get(
            endpoint['url'],
            timeout=endpoint['timeout']
        )
        response_time = (time.time() - start) * 1000

        result['status_code'] = response.status_code
        result['response_time_ms'] = round(response_time, 2)

        if response.status_code < 400:
            result['status'] = 'healthy'
            print(f"✅ {endpoint['name']}: {response.status_code} in {response_time:.0f}ms")
        else:
            result['status'] = 'degraded'
            print(f"⚠️ {endpoint['name']}: {response.status_code} in {response_time:.0f}ms")

    except requests.exceptions.Timeout:
        result['status'] = 'down'
        result['error'] = 'Timeout'
        print(f"❌ {endpoint['name']}: Timeout after {endpoint['timeout']}s")

    except requests.exceptions.ConnectionError:
        result['status'] = 'down'
        result['error'] = 'Connection Error'
        print(f"❌ {endpoint['name']}: Connection Error")

    except Exception as e:
        result['status'] = 'down'
        result['error'] = str(e)
        print(f"❌ {endpoint['name']}: {e}")

    return result

def calculate_sla(checks):
    total = len(checks)
    healthy = len([c for c in checks if c['status'] == 'healthy'])
    degraded = len([c for c in checks if c['status'] == 'degraded'])
    down = len([c for c in checks if c['status'] == 'down'])

    uptime_percentage = (healthy / total * 100) if total > 0 else 0
    avg_response_time = sum(
        c['response_time_ms'] for c in checks if c['response_time_ms']
    ) / max(len([c for c in checks if c['response_time_ms']]), 1)

    sla_target = float(os.getenv('SLA_TARGET', 99.9))
    sla_breach = uptime_percentage < sla_target

    return {
        'total_checks': total,
        'healthy': healthy,
        'degraded': degraded,
        'down': down,
        'uptime_percentage': round(uptime_percentage, 2),
        'avg_response_time_ms': round(avg_response_time, 2),
        'sla_target': sla_target,
        'sla_breach': sla_breach,
        'sla_status': '🔴 BREACH' if sla_breach else '✅ COMPLIANT'
    }

def send_alert(checks, sla_metrics):
    status_emoji = '🔴' if sla_metrics['sla_breach'] else '✅'

    message = f"""
SLA GUARDIAN REPORT
===================
Date: {datetime.now().toDateString() if False else datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SLA STATUS: {sla_metrics['sla_status']}
Uptime: {sla_metrics['uptime_percentage']}%
SLA Target: {sla_metrics['sla_target']}%
Avg Response Time: {sla_metrics['avg_response_time_ms']}ms

ENDPOINT RESULTS:
{chr(10).join([f"{'✅' if c['status'] == 'healthy' else '❌'} {c['name']}: {c['status'].upper()} ({c['response_time_ms']}ms)" for c in checks])}

SUMMARY:
Healthy: {sla_metrics['healthy']}/{sla_metrics['total_checks']}
Degraded: {sla_metrics['degraded']}/{sla_metrics['total_checks']}
Down: {sla_metrics['down']}/{sla_metrics['total_checks']}

{'⚠️ ACTION REQUIRED: SLA breach detected! Investigate immediately.' if sla_metrics['sla_breach'] else '✅ All systems operating within SLA targets.'}

SLA Guardian 🛡️
    """

    subject = f"{status_emoji} SLA Report — {sla_metrics['uptime_percentage']}% uptime — {'BREACH DETECTED' if sla_metrics['sla_breach'] else 'All Clear'}"

    ses.send_email(
        Source=os.getenv('YOUR_EMAIL'),
        Destination={'ToAddresses': [os.getenv('YOUR_EMAIL')]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': message}}
        }
    )
    print(f"\n📧 SLA report sent to {os.getenv('YOUR_EMAIL')}")

def run():
    print("🛡️ SLA Guardian")
    print("===============\n")

    # Check all endpoints
    print("Step 1: Checking all endpoints...\n")
    checks = [check_endpoint(ep) for ep in ENDPOINTS]

    # Calculate SLA
    print("\nStep 2: Calculating SLA metrics...")
    sla_metrics = calculate_sla(checks)

    print(f"\n📊 SLA METRICS:")
    print(f"Uptime: {sla_metrics['uptime_percentage']}%")
    print(f"SLA Target: {sla_metrics['sla_target']}%")
    print(f"Status: {sla_metrics['sla_status']}")
    print(f"Avg Response Time: {sla_metrics['avg_response_time_ms']}ms")

    # Send report
    print("\nStep 3: Sending SLA report...")
    send_alert(checks, sla_metrics)

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'checks': checks,
        'sla_metrics': sla_metrics
    }

    with open('sla_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("📄 Report saved to sla_report.json")
    print("\n✅ SLA Guardian complete!")

if __name__ == "__main__":
    run()