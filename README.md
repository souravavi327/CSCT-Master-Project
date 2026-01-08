# CSCT-Master-Project
Privacy Risk Monitoring Dashboard for Small Healthcare Clinics

Project Overview:

This project addresses the "monitoring gap" in small UK healthcare clinics that lack the resources for expensive security tools. It features a functional Power BI Dashboard designed to help non-technical managers detect internal data privacy risks, such as unauthorized "snooping" or credential misuse.

Key Features

Statistical Anomaly Detection: Utilizes Z-score analysis to automatically flag users whose access volume significantly exceeds their role-based average.
Temporal Risk Analysis: A high-density heatmap identifies suspicious access events during off-hours or early morning spikes.
Sensitivity-Aware Monitoring: Maps data sensitivity levels against user roles to highlight potential policy violations regarding High-Sensitivity records.
Low-Code Architecture: Built using Microsoft Power BI and a star-schema data model for high performance and cost-effectiveness.

Repository Contents

Dashboard.pbix: The primary Power BI artifact containing the visualizations and DAX measures.
privacy_risk_monitoring_dataset.csv: The synthetic dataset containing over 200,000 clinical access logs used for testing.
README.md: Project documentation.

Tools Used

Microsoft Power BI: Dashboard development and DAX (Data Analysis Expressions).
Python (Pandas & Faker): Used to generate the high-volume synthetic clinical dataset.
