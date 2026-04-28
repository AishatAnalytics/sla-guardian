# SLA Guardian 🛡️

Monitors API endpoints, calculates real-time SLA compliance and alerts on breaches.

## The Problem
Companies promise customers 99.9% uptime SLAs but have no automated way to track whether they are actually meeting them. They find out about breaches when customers complain.

## What It Does
- Monitors multiple API endpoints in real time
- Measures response times and availability
- Calculates uptime percentage against SLA target
- Detects SLA breaches immediately
- Sends detailed email alerts with full report
- Saves JSON report for audit trail

## Sample Output
Uptime: 66.67%
SLA Target: 99.9%
Status: BREACH DETECTED
Avg Response Time: 843ms

Action Required: SLA breach detected! Investigate immediately.

## Tech Stack
- Python 3
- AWS SES
- boto3
- requests

## Key Concepts Demonstrated
- SLA vs SLO vs SLI
- Real-time availability monitoring
- Breach detection and alerting
- AWS Well-Architected Operational Excellence Pillar

## How To Run
- Clone the repo
- pip install boto3 python-dotenv requests
- Add your AWS credentials and email to .env
- Run py monitor.py

## Part of my 30 cloud projects in 30 days series
Follow along: https://www.linkedin.com/in/aishatolatunji/