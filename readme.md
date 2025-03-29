Technical Resume of the Project
=====================================================

1. Project Overview
-------------------

This project appears to be a Django-based investment management platform. Its purpose is to provide users with tools to manage investment plans, wallets, and transactions. The platform integrates with blockchain APIs and supports cryptocurrency-based transactions. It aims to simplify investment tracking and automate returns calculation for users.

2. Technology Stack
-------------------

* Backend Framework: Django (Python)
* Frontend Framework: Not explicitly mentioned, but likely integrated with Django templates or a separate frontend.
* Database: SQLite (development), potentially PostgreSQL in production (based on psycopg2-binary).
* Libraries/Packages:
	+ Django Extensions: django.contrib.auth, django.db.models
	+ Cryptocurrency Integration: Blockchain-related fields in models
	+ Email: Flask-Mail (for email notifications)
	+ Task Queue: Celery (for asynchronous tasks)
	+ ORM: Django ORM
	+ Validation: Pydantic
	+ Other Utilities: Werkzeug, Jinja2, Click, Blinker, Authlib, Cryptography

3. Existing Functionalities
---------------------------

* User Profiles:
	+ Managed via the Profile model in model.py
	+ Includes fields like first_name, last_name, date_of_birth, and address.
* Investment Plans:
	+ Defined in the Plans model in models.py.
	+ Includes attributes like name, duration, and rate.
* Wallet Management:
	+ Managed via the Wallet model in models.py.
	+ Supports multiple cryptocurrencies (BTC, ETH, USDT, TRX).
* Transactions:
	+ Handled by the Transactions model in models.py.
	+ Tracks balances, blockchain details, and transaction statuses.
* Investments:
	+ Defined in the Investments model in models.py.
	+ Links users, wallets, and plans to track investment details.
* Asynchronous Task Handling:
	+ Celery is integrated for background tasks (e.g., email notifications, blockchain interactions).

4. API Endpoints & Data Flow
---------------------------

* Authentication:
	+ Likely uses Django's built-in authentication system (django.contrib.auth).
	+ May include token-based authentication for API endpoints.
* Endpoints:
	+ Investments: CRUD operations for investments.
	+ Wallets: Manage wallet balances and transactions.
	+ Plans: Retrieve available investment plans.
	+ Profiles: Update user profile information.
* Middleware:
	+ Likely includes Django's default middleware for security, sessions, and CSRF protection.
* Third-Party Services:
	+ Blockchain APIs for cryptocurrency transactions.
	+ Flask-Mail for email notifications.

5. Database Structure
---------------------

* Key Models:
	+ User: Default Django User model.
	+ Profile: One-to-one relationship with User.
	+ Plans: Tracks investment plans.
	+ Wallet: Tracks user balances and cryptocurrency types.
	+ Transactions: Tracks wallet transactions and statuses.
	+ Investments: Links users, wallets, and plans.
* Relationships:
	+ Profile → User (One-to-One)
	+ Wallet → User (ForeignKey)
	+ Transactions → Wallet & User (ForeignKey)
	+ Investments → Wallet, User, & Plans (ForeignKey)

6. What's Left to Be Done
-------------------------

* Unfinished Features:
	+ Commented-out code in models.py suggests incomplete avatar handling.
	+ Blockchain API integration fields (blockchain_in, blockchain_out) in Transactions are placeholders without implementation.
	+ No explicit frontend integration details are provided.
* TODOs:
	+ Resizing and handling profile avatars.
	+ Implementing blockchain API calls for transactions.
	+ Adding comprehensive unit tests for models and views.

7. Code Architecture & Best Practices
--------------------------------------

* Architecture:
	+ Follows the MVC pattern (Models, Views, Controllers).
	+ Organized into Django apps (auth, core, investments, plans, profiles).
* Best Practices:
	+ Models are well-structured with appropriate relationships.
	+ Use of UUIDs for unique identification in models.
	+ Separation of concerns across apps.
* Areas for Improvement:
	+ Add docstrings and comments for better code readability.
	+ Implement service layers for complex business logic.
	+ Use environment variables for sensitive data (e.g., API keys).

8. Challenges & Considerations
------------------------------

* Potential Bottlenecks:
	+ SQLite may not scale well for production; consider PostgreSQL.
	+ Blockchain API calls could introduce latency; caching or asynchronous handling is recommended.
* Technical Debt:
	+ Lack of unit tests and commented-out code indicate incomplete implementation.
	+ Hardcoded values (e.g., token choices in Wallet) could be dynamic.
* Suggestions:
	+ Use Docker for consistent development and deployment environments.
	+ Integrate Swagger or Postman for API documentation.
	+ Optimize database queries using Django's select_related and prefetch_related.

Next Steps
==========

To move forward with the project, address the following:

1. Address Unfinished Features
	* Blockchain Integration:
		- Implement the blockchain API calls for the Transactions model in models.py.
		- Ensure proper handling of blockchain_in and blockchain_out fields.
	* Profile Avatars:
		- Complete the avatar resizing and handling logic in models.py.
	* Unit Tests:
		- Write comprehensive unit tests for all models, views, and serializers in the auth, investments, plans, and profiles apps.
2. Optimize Database
	* Switch to PostgreSQL:
		- Update the database configuration in settings.py to use PostgreSQL for production.
		- Migrate the existing SQLite database to PostgreSQL using tools like pgloader or Django's migration system.
	* Optimize Queries:
		- Use select_related and prefetch_related in views to reduce database query overhead.
3. Improve Code Quality
	* Add Documentation:
		- Add docstrings to all functions, classes, and modules for better maintainability.
		- Use tools like drf-spectacular to generate API documentation.
	* Refactor Code:
		- Implement service layers for complex business logic to improve separation of concerns.
		- Remove any commented-out or unused code.
4. Enhance Security
	* Enable CSRF Protection:
		- Re-enable the django.middleware.csrf.CsrfViewMiddleware in settings.py.
	* Environment Variables:
		- Move sensitive data (e.g., database credentials, API keys) to environment variables using python-decouple or django-environ.
5. Frontend Integration
	* API Testing:
		- Test all API endpoints using tools like Postman or Swagger to ensure they work as expected.
	* Frontend Development:
		- If a separate frontend exists, ensure proper integration with the backend APIs.
		- If using Django templates, implement the necessary views and templates.
6. Deployment
	* Containerization:
		- Create a Dockerfile and docker-compose.yml for consistent development and production environments.
	* Hosting:
		- Configure deployment to a cloud provider (e.g., AWS, Heroku, or Vercel) using the existing vercel.json file.
	* Static Files:
		- Use WhiteNoise for serving static files in production.
7. Monitor and Maintain
	* Logging and Monitoring:
		- Set up logging using Django's logging framework.
		- Integrate monitoring tools like Sentry for error tracking.
	* Task Queue:
		- Ensure Celery is properly configured for background tasks and integrate a message broker like RabbitMQ or Redis.
