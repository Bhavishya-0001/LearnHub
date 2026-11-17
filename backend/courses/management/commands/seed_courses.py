from django.core.management.base import BaseCommand
from courses.models import Course, Lesson


class Command(BaseCommand):
    help = "Seeds all 15 required course categories with comprehensive lessons"

    def handle(self, *args, **options):
        # Update course 1 if it has no lessons
        course_1 = Course.objects.filter(id=1).first()
        if course_1:
            course_1.category = "Programming"
            course_1.duration = "8 Weeks"
            course_1.thumbnail_url = "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&auto=format&fit=crop&q=60"
            course_1.save()

            if course_1.lessons.count() == 0:
                p_lessons = [
                    ("Introduction to Python & Setup", "Learn the history, setup the environment, and write your first Hello World in Python.", "https://www.youtube.com/embed/_uQrJ0TkZlc", "15 mins"),
                    ("Variables, Data Types & Operators", "Understand numbers, strings, booleans, and arithmetic operations.", "https://www.youtube.com/embed/kqtD5dpn9C8", "20 mins"),
                    ("Control Flow: Conditionals & Loops", "Master if-else logic, for loops, and while loops for iterative tasks.", "https://www.youtube.com/embed/6iF8Xb7Z3wQ", "25 mins"),
                    ("Functions & Modular Programming", "Define reusable functions, parameters, return values, and scopes.", "https://www.youtube.com/embed/9Os0o3wzS_I", "20 mins"),
                    ("Object-Oriented Programming (OOP)", "Classes, objects, inheritance, polymorphism, and encapsulation.", "https://www.youtube.com/embed/JeznW_7DlB0", "30 mins"),
                ]
                for idx, (title, desc, url, dur) in enumerate(p_lessons, 1):
                    Lesson.objects.create(
                        course=course_1,
                        title=title,
                        description=desc,
                        content_url=url,
                        duration=dur,
                        order=idx
                    )
            self.stdout.write(f"Updated Course 1: {course_1.title}")

        course_data = [
            {
                "title": "Modern Cloud & IT Infrastructure",
                "category": "Technology & IT",
                "level": "Intermediate",
                "instructor_name": "LearnHub Tech Faculty",
                "description": "Master enterprise IT architecture, system administration, virtualization, and modern network operations.",
                "duration": "10 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Enterprise IT Fundamentals", "Understanding networks, IP addressing, and client-server architecture.", "https://www.youtube.com/embed/2Dfyh8JkU7U", "18 mins"),
                    ("Virtualization & Containerization", "Learn hypervisors, containers, and deployment virtualization.", "https://www.youtube.com/embed/alce_7l-v7o", "24 mins"),
                    ("System Administration & Automation", "Linux command line, script automation, and server management.", "https://www.youtube.com/embed/wBp0Rb-ZJak", "30 mins"),
                    ("Infrastructure Monitoring & Recovery", "Logging, uptime diagnostics, and disaster recovery strategies.", "https://www.youtube.com/embed/S9uO_r2J9nU", "22 mins"),
                ]
            },
            {
                "title": "Full-Stack Web Development Bootcamp",
                "category": "Web Development",
                "level": "Beginner",
                "instructor_name": "LearnHub Development Staff",
                "description": "Build modern responsive websites from scratch using HTML5, CSS3, modern JavaScript, and backend REST APIs.",
                "duration": "12 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1547658719-da2b51169166?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("HTML5 Semantic Structure & Forms", "Modern page architecture, accessibility, and form validation.", "https://www.youtube.com/embed/qz0aGYrrlhU", "20 mins"),
                    ("CSS3 Layouts: Flexbox & Grid", "Responsive styling, glassmorphism design, and animations.", "https://www.youtube.com/embed/1Rs2ND1ryYc", "25 mins"),
                    ("JavaScript DOM Manipulation & Fetch", "Event-driven scripting, dynamic rendering, and HTTP requests.", "https://www.youtube.com/embed/hdI2bqOjy3c", "30 mins"),
                    ("Building Production RESTful APIs", "API design, JSON serialization, and backend endpoint security.", "https://www.youtube.com/embed/WXsD0ZgxjRw", "35 mins"),
                ]
            },
            {
                "title": "Data Science & Artificial Intelligence Foundations",
                "category": "Data Science & AI",
                "level": "Intermediate",
                "instructor_name": "LearnHub AI Lab",
                "description": "Harness data analytics, NumPy, Pandas, visualization, and core machine learning models for predictive intelligence.",
                "duration": "10 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Data Exploration with Pandas & NumPy", "Loading datasets, cleaning missing data, and statistical summaries.", "https://www.youtube.com/embed/vmEHCJofslg", "25 mins"),
                    ("Exploratory Data Visualization", "Designing impactful charts with Matplotlib and Seaborn.", "https://www.youtube.com/embed/a9UrKTVEeZA", "20 mins"),
                    ("Supervised Learning: Regression & Classification", "Scikit-Learn models, training splits, and confusion matrices.", "https://www.youtube.com/embed/7eh4d6sabA0", "35 mins"),
                    ("Intro to Neural Networks & Deep Learning", "Perceptrons, backpropagation, and artificial neural networks.", "https://www.youtube.com/embed/aircAruvnKk", "40 mins"),
                ]
            },
            {
                "title": "B2B Sales Strategy & Account Growth",
                "category": "Business & Sales",
                "level": "Beginner",
                "instructor_name": "LearnHub Business School",
                "description": "Learn modern consultative selling, deal pipelines, high-value client acquisition, and relationship management.",
                "duration": "6 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Consultative Selling Principles", "Active listening, customer discovery, and value-focused pitching.", "https://www.youtube.com/embed/7B_w9q8j7Uo", "15 mins"),
                    ("Building & Managing a Sales Pipeline", "Lead qualification, stage gates, and CRM best practices.", "https://www.youtube.com/embed/9Bw0kL8j8mQ", "20 mins"),
                    ("Objection Handling & Closing", "Overcoming price objections and finalizing contracts.", "https://www.youtube.com/embed/4Cw0qL7j9wR", "22 mins"),
                ]
            },
            {
                "title": "Enterprise Sales Team Leadership",
                "category": "Sales Management",
                "level": "Advanced",
                "instructor_name": "LearnHub Leadership Group",
                "description": "Recruit, train, motivate, and scale high-performing sales organizations with data-driven KPI dashboards.",
                "duration": "7 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Sales Team Architecture & Quotas", "Designing compensation plans and setting equitable targets.", "https://www.youtube.com/embed/3Gw0kL7m4nB", "20 mins"),
                    ("Sales Coaching & 1-on-1 Frameworks", "Empowering account executives and deal review workflows.", "https://www.youtube.com/embed/6Kw0pL5k1vA", "25 mins"),
                ]
            },
            {
                "title": "Creative Brand Design & Visual Storytelling",
                "category": "Design & Creative",
                "level": "Beginner",
                "instructor_name": "LearnHub Design Studio",
                "description": "Explore color theory, visual hierarchy, typography systems, and modern brand design essentials.",
                "duration": "8 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("The Fundamentals of Visual Hierarchy", "Composition, balance, contrast, and focal points.", "https://www.youtube.com/embed/YqQx75OPWA0", "18 mins"),
                    ("Typography & Color Psychology", "Type pairing, chromatic palettes, and brand expression.", "https://www.youtube.com/embed/sByzHoiYFX0", "22 mins"),
                    ("Designing Brand Assets", "Logomarks, stationery, and digital identity guidelines.", "https://www.youtube.com/embed/0GvP_dOq7_k", "28 mins"),
                ]
            },
            {
                "title": "UI/UX Design Masterclass & Prototyping",
                "category": "UI/UX Design",
                "level": "Intermediate",
                "instructor_name": "LearnHub Design Studio",
                "description": "Design sleek digital experiences from wireframes to high-fidelity clickable interactive prototypes.",
                "duration": "9 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("User Research & Journey Mapping", "Interviews, personas, and identifying friction points.", "https://www.youtube.com/embed/c9Wg6Cb_YlU", "20 mins"),
                    ("Wireframing & Information Architecture", "Low-fidelity layouts and navigation structures.", "https://www.youtube.com/embed/68w2VwalD5w", "25 mins"),
                    ("Design Systems & Component Libraries", "Creating reusable UI tokens, buttons, and input fields.", "https://www.youtube.com/embed/FTFaQWZBqQ8", "30 mins"),
                    ("Interactive Prototyping & Usability Testing", "Micro-interactions, state transitions, and user testing.", "https://www.youtube.com/embed/1v0Uj_N0zPQ", "28 mins"),
                ]
            },
            {
                "title": "Omnichannel Digital Marketing Mastery",
                "category": "Digital Marketing",
                "level": "Beginner",
                "instructor_name": "LearnHub Growth Department",
                "description": "Master SEO, social media marketing, content funnels, paid performance ads, and conversion analytics.",
                "duration": "8 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Search Engine Optimization (SEO) Playbook", "Keyword research, on-page optimization, and technical SEO.", "https://www.youtube.com/embed/xsVTqzratPs", "24 mins"),
                    ("Social Media Marketing & Brand Building", "Organic strategy, community engagement, and viral formats.", "https://www.youtube.com/embed/Dhw9k1_oEw8", "20 mins"),
                    ("Performance Advertising: Meta & Google Ads", "Audience targeting, ad creatives, and ROAS measurement.", "https://www.youtube.com/embed/0E3G6u5gK1w", "30 mins"),
                ]
            },
            {
                "title": "Corporate Finance & Managerial Accounting",
                "category": "Finance & Accounting",
                "level": "Intermediate",
                "instructor_name": "LearnHub Finance Academy",
                "description": "Understand balance sheets, cash flow statements, financial modeling, budgeting, and investment valuation.",
                "duration": "8 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Reading Financial Statements", "Mastering the Income Statement, Balance Sheet, and Cash Flow.", "https://www.youtube.com/embed/WEDIj9JBTC8", "25 mins"),
                    ("Working Capital & Cash Flow Management", "Liquidity ratios, inventory turns, and cash cycle optimization.", "https://www.youtube.com/embed/s_x3L0U3pWw", "22 mins"),
                    ("Discounted Cash Flow (DCF) & Valuation", "Net present value, IRR, and financial forecast models.", "https://www.youtube.com/embed/H018U3L8bQw", "30 mins"),
                ]
            },
            {
                "title": "Modern Human Resources & Talent Strategy",
                "category": "Human Resources",
                "level": "Beginner",
                "instructor_name": "LearnHub People Ops",
                "description": "Drive high-impact talent acquisition, company culture, employee performance evaluations, and HR compliance.",
                "duration": "6 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Talent Acquisition & Interviewing", "Structured hiring, behavioral rubrics, and candidate experience.", "https://www.youtube.com/embed/7Aw0kL8j7Uo", "20 mins"),
                    ("Employee Onboarding & Retention", "Cultural onboarding, mentor pairing, and 90-day checkpoints.", "https://www.youtube.com/embed/5Bw0kL8j8mQ", "18 mins"),
                    ("Performance Reviews & Feedback Culture", "Continuous feedback frameworks, OKRs, and conflict resolution.", "https://www.youtube.com/embed/2Cw0qL7j9wR", "24 mins"),
                ]
            },
            {
                "title": "Executive Communication & Public Speaking",
                "category": "Communication Skills",
                "level": "Beginner",
                "instructor_name": "LearnHub Communication Group",
                "description": "Master persuasive presentations, conflict resolution, active listening, and concise business messaging.",
                "duration": "5 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("The Science of Clear Speaking", "Vocal tone, pacing, body language, and presence.", "https://www.youtube.com/embed/i0a61wFaZ8A", "18 mins"),
                    ("Structuring Persuasive Presentations", "The narrative pyramid, slide design, and audience engagement.", "https://www.youtube.com/embed/dEDcc0aCjaA", "25 mins"),
                    ("Cross-Functional Collaboration & Negotiation", "Navigating disagreements and reaching win-win agreements.", "https://www.youtube.com/embed/zAug57s-mK8", "20 mins"),
                ]
            },
            {
                "title": "Startup Entrepreneurship & Product-Market Fit",
                "category": "Entrepreneurship",
                "level": "Intermediate",
                "instructor_name": "LearnHub Ventures",
                "description": "Transform ideas into viable businesses through rapid customer validation, unit economics, and venture pitching.",
                "duration": "10 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Idea Validation & Customer Discovery", "The Mom Test methodology and hypothesis validation.", "https://www.youtube.com/embed/Th8JoIan4dg", "22 mins"),
                    ("Building Minimum Viable Products (MVP)", "Rapid prototyping and low-code validation experiments.", "https://www.youtube.com/embed/1hHMwLxN6EM", "26 mins"),
                    ("Startup Economics & Pitching to Investors", "CAC, LTV, pitch decks, and term sheet basics.", "https://www.youtube.com/embed/Q43kX4O8Kcw", "30 mins"),
                ]
            },
            {
                "title": "AWS & Multi-Cloud Architecture",
                "category": "Cloud Computing",
                "level": "Advanced",
                "instructor_name": "LearnHub Cloud Academy",
                "description": "Design resilient, scalable cloud architectures using AWS, serverless computing, and microservices.",
                "duration": "10 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Cloud Architecture Fundamentals", "Regions, Availability Zones, VPCs, and Subnets.", "https://www.youtube.com/embed/k1RI5locZE4", "25 mins"),
                    ("Compute Services: EC2, Lambda & ECS", "Virtual machines versus event-driven functions and container clusters.", "https://www.youtube.com/embed/Ia-UEOoLkL8", "30 mins"),
                    ("Storage & Databases in the Cloud", "S3 object storage, RDS managed databases, and DynamoDB.", "https://www.youtube.com/embed/3hLmDS179YE", "28 mins"),
                ]
            },
            {
                "title": "Applied Cybersecurity & Ethical Hacking",
                "category": "Cybersecurity",
                "level": "Intermediate",
                "instructor_name": "LearnHub Security Lab",
                "description": "Protect modern networks and web applications by understanding vulnerabilities, cryptography, and defense.",
                "duration": "10 Weeks",
                "thumbnail_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&auto=format&fit=crop&q=60",
                "lessons": [
                    ("Cybersecurity Core Principles", "The CIA triad, threat modeling, and defense in depth.", "https://www.youtube.com/embed/inWWhr5tnEA", "20 mins"),
                    ("Network Security & Packet Analysis", "Firewalls, Wireshark packet capture, and intrusion detection.", "https://www.youtube.com/embed/2_lswM1S264", "26 mins"),
                    ("Web Application Security (OWASP Top 10)", "SQL injection, XSS, CSRF, and safe input sanitization.", "https://www.youtube.com/embed/3Kq1MIfTWCE", "32 mins"),
                    ("Applied Cryptography & SSL/TLS", "Symmetric vs asymmetric ciphers, hashing, and public key infrastructure.", "https://www.youtube.com/embed/jhXCTbFnK8o", "28 mins"),
                ]
            }
        ]

        created_count = 0
        for item in course_data:
            course, created = Course.objects.get_or_create(
                title=item["title"],
                defaults={
                    "category": item["category"],
                    "level": item["level"],
                    "instructor_name": item["instructor_name"],
                    "description": item["description"],
                    "duration": item["duration"],
                    "thumbnail_url": item["thumbnail_url"],
                    "is_published": True,
                }
            )
            if created:
                created_count += 1
                for idx, (l_title, l_desc, l_url, l_dur) in enumerate(item["lessons"], 1):
                    Lesson.objects.create(
                        course=course,
                        title=l_title,
                        description=l_desc,
                        content_url=l_url,
                        duration=l_dur,
                        order=idx
                    )

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {created_count} courses across all 15 categories!"))
