# Drucom

Data Analysis of the Drupal Community (Users & Contributions).

## Goals

Here's a list of KPIs to measure our acheivements.

### **1️⃣ Improve Contributor Retention & Engagement**  

- 🏆 **User Retention Rate** – Percentage of users still active **6 & 12 months** after registration.  
- 🔄 **Churn Rate** – Percentage of users who stop contributing after a certain period.  
- ⏳ **Average Contribution Lifespan** – How long an active user remains engaged.  
- 📈 **Contribution Frequency** – Number of commits, issue responses, or documentation edits per user.  
- 🎯 **Re-engagement Success Rate** – Percentage of previously inactive users who return after targeted interventions.  

---

### **2️⃣ Enhance Community Growth & Inclusivity**  

- 🌍 **New User Registrations by Region** – Growth in Drupal.org signups by country/continent.  
- 👩‍💻 **Diversity & Inclusion Metrics** – Percentage of new contributors from underrepresented groups (e.g., women, non-Western regions).  
- 🏅 **Onboarding Completion Rate** – Percentage of new users who complete suggested first contributions.  
- 📊 **Mentorship Program Impact** – How many new contributors stay engaged after mentorship.  
- 🗣️ **Forum & Issue Queue Participation** – Number of discussions & contributions in community help channels.  

---

### **3️⃣ Build AI-Powered Insights for Community Decision-Making**  

- 🤖 **Churn Prediction Model Accuracy** – How well the AI model predicts user inactivity.  
- 😃 **Sentiment Analysis Trends** – Changes in community sentiment over time (positive/neutral/negative feedback in discussions).  
- 📊 **Dashboard Usage Metrics** – Number of views/interactions with community analytics dashboards.  
- 🔥 **Early Issue Resolution Rate** – Speed at which high-priority issues are identified and resolved based on AI-driven insights.  
- 🎯 **Project Recommendation Effectiveness** – Percentage of users engaging with AI-recommended modules or projects.  


## Plan  

### Phase 1: Data Collection & Preprocessing

- [ ] 1. Gather User Data  
- Extract registered user data (join date, country, profile info, activity logs).  
- Collect metadata on user roles (developer, maintainer, casual user, etc.).  

- [ ] 2. Collect Contribution Data  
- Pull contribution records (commits, module/theme uploads, forum posts, issue queue activity).  
- Include timestamps, project categories, and contribution types.  

- [ ] 3. Data Cleaning & Transformation  
- Remove duplicate and inactive/spam accounts.  
- Standardize timestamps and format categorical data (e.g., contributor roles).  
- Merge datasets (users + contributions) for a unified view.  

### Phase 2: Exploratory Data Analysis (EDA)  
- [ ] 4. User Growth & Activity Trends  
- Analyze the number of new registrations over time (monthly/yearly).  
- Identify spikes in user registrations (e.g., post-DrupalCon events).  
- Measure the percentage of users who actively contribute vs. those who don’t.  

- [ ] 5. Contribution Patterns  
- Identify the most active contributors (top committers, forum participants, module maintainers).  
- Analyze contribution types (code commits, forum posts, bug fixes, theme development).  
- Find correlations between user activity and contribution levels (e.g., do early contributors stay active longer?).  

- [ ] 6. Geographic & Demographic Analysis  
- Map contributions by region to see where Drupal has the most active users.  
- Analyze engagement trends by experience level (newcomers vs. veteran developers).  

### Phase 3: Advanced AI/ML Analysis  
- [ ] 7. User Segmentation (Clustering)  
- Use K-Means or Hierarchical Clustering to group users based on their contribution patterns.  
- Segment users into categories: Core Contributors, Occasional Contributors, Passive Users, etc.  

- [ ] 8. Churn Prediction  
- Train a classification model (Random Forest, XGBoost) to predict which users are likely to stop contributing.  
- Use features like first-month activity, project involvement, and forum engagement.  

- [ ] 9. Sentiment Analysis of Community Discussions  
- Apply NLP techniques (BERT, VADER) to analyze user sentiment in forums and issue queues.  
- Track changes in sentiment over time (positive vs. negative feedback on Drupal releases).  

- [ ] 10. Contribution Recommendation System  
- Build a collaborative filtering model to suggest relevant Drupal projects, documentation, or forums based on user activity.  

### Phase 4: Reporting & Insights Generation  
- [ ] 11. Data Visualization & Dashboards  
- Develop Power BI/Tableau dashboards for real-time tracking of:  
  - New user registrations  
  - Contribution activity trends  
  - Geographic contribution heatmaps  
  - Churn risk analysis  

- [ ] 12. Actionable Insights & Community Growth Strategies  
- Identify key areas where community engagement is dropping.  
- Recommend strategies to retain contributors (e.g., targeted outreach, better onboarding).  
- Provide insights to the Drupal Association to enhance open-source participation.  

## Final Deliverables
- [ ] Interactive dashboards for tracking community health.  
- [ ] AI-powered user segmentation & churn prediction models.  
- [ ] Insights on how to improve engagement & retention.  
- [ ] A report summarizing Drupal’s community trends & growth opportunities.  

## Resources

* [Drupal.org](https://drupal.org/), the community website - managed by the Drupal Association.
* [Drupal GitLab](https://git.drupalcode.org/) instance, hosting core and all other contributed projects' code.
* [Drupal REST APIs](https://www.drupal.org/drupalorg/docs/apis/rest-and-other-apis) - used to source raw data.
* [GitLab REST API](https://docs.gitlab.com/api/rest/) - used to source raw data.