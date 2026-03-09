📌 Overview

This capstone project is an AI-powered lead generation and automation platform that captures leads from Telegram, processes them using AI, and automatically routes them to different platforms such as Slack, email, and databases for follow-up and tracking.

The system uses automation workflows, AI agents, and real-time integrations to eliminate manual lead management and improve response time.

This project demonstrates how modern tools like AI, workflow automation, and cloud databases can work together to build scalable business automation systems.

🧠 Key Features
1️⃣ AI Lead Capture

Leads submit information through Telegram

AI agent extracts important details such as:

Name

Email

Lead category

Meeting information

2️⃣ Intelligent Lead Categorization

The AI automatically classifies leads into categories such as:

Hot Leads 🔥

Warm Leads 🌤️

Cold Leads ❄️

This helps sales teams prioritize high-value prospects.

3️⃣ Automated Routing

Based on lead classification, the system automatically routes leads to:

Slack channels

Email notifications

Supabase database

This ensures teams receive leads instantly without manual work.

4️⃣ Database Storage

All leads are stored in Supabase, which allows:

Lead tracking

Data analytics

Historical record keeping

CRM-style monitoring

5️⃣ AI Email Response System

The system includes an AI Email Response Agent that:

Reads incoming replies from leads

Generates intelligent responses

Sends follow-up emails automatically

6️⃣ Error Handling & Workflow Resilience

Using n8n automation features, the system includes:

Error triggers

Retry mechanisms

Fail-safe workflow execution

This ensures the automation runs reliably even when errors occur.

🏗️ System Architecture

Workflow Overview:

Telegram → n8n Workflow → AI Processing → Lead Categorization
          ↓
      Supabase Database
          ↓
     Slack Notifications
          ↓
      Email Automation
⚙️ Technologies Used
Technology	Purpose
n8n	Workflow automation
Supabase	Cloud database
Telegram Bot API	Lead capture interface
Slack API	Team notifications
Zapier	Additional integrations
OpenAI / AI Agent	Lead analysis and response generation
GitHub	Version control and project hosting
📊 Example Use Case

A potential client sends a message through Telegram.

The system will automatically:

1️⃣ Capture the message
2️⃣ Extract lead details using AI
3️⃣ Categorize the lead (Hot / Warm / Cold)
4️⃣ Store the lead in Supabase
5️⃣ Send a notification to Slack
6️⃣ Trigger AI-powered email follow-up

All of this happens automatically within seconds.

🎯 Project Goals

The main goals of this project were:

Demonstrate AI-powered workflow automation

Build a real-world lead management system

Integrate multiple APIs into one seamless workflow

Reduce manual work in sales pipelines

Show how AI agents can improve business processes

👨‍💻 Author

Emma Nduaguba
