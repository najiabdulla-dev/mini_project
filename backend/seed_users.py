import random
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from apps.skills.models import Category, Skill
from apps.profiles.models import UserSkill, Experience
from apps.hiring.models import HireRequest
from apps.reviews.models import Review

User = get_user_model()

def run_seed():
    print("Starting seed process...")
    
    # 1. Categories & Skills
    cats = {
        'Tech': ['Web Development', 'Mobile App Dev', 'Python Scripting'],
        'Design': ['Graphic Design', 'UI/UX Design', 'Logo Creation'],
        'Writing': ['Content Writing', 'Copywriting', 'Proofreading'],
        'Services': ['Plumbing', 'Electrician', 'Carpentry']
    }
    db_skills = {}
    for c_name, s_list in cats.items():
        cat, _ = Category.objects.get_or_create(name=c_name, defaults={'sort_order': 1})
        for s_name in s_list:
            sk, _ = Skill.objects.get_or_create(name=s_name, category=cat)
            db_skills[s_name] = sk

    # 2. Users Data
    users_data = [
        ("Kevin", "Stark", "kevin@gmail.com", "kevin123456", "Senior Web Developer building scalable backends.", "New York, NY", 50, "Tech", ["Web Development", "Python Scripting"]),
        ("Daniel", "Carter", "daniel@gmail.com", "daniel123456", "UI/UX Designer focusing on mobile apps.", "San Francisco, CA", 65, "Design", ["UI/UX Design", "Logo Creation"]),
        ("Michael", "Brooks", "michael@gmail.com", "michael123456", "Certified Plumber with 10 years experience.", "Chicago, IL", 80, "Services", ["Plumbing"]),
        ("Ryan", "Cooper", "ryan@gmail.com", "ryan123456", "Mobile App Developer (Flutter/React Native).", "Austin, TX", 55, "Tech", ["Mobile App Dev"]),
        ("Alex", "Morgan", "alex@gmail.com", "alex123456", "Freelance Copywriter & Content Strategist.", "Seattle, WA", 45, "Writing", ["Copywriting", "Content Writing"]),
        ("James", "Wilson", "james@gmail.com", "james123456", "Master Electrician for residential and commercial.", "Boston, MA", 90, "Services", ["Electrician"]),
        ("Matthew", "Clark", "matthew@gmail.com", "matthew123456", "Full-stack Developer and Python expert.", "Denver, CO", 60, "Tech", ["Web Development", "Python Scripting"]),
        ("Ethan", "Parker", "ethan@gmail.com", "ethan123456", "Graphic Designer & Illustrator.", "Portland, OR", 40, "Design", ["Graphic Design", "Logo Creation"]),
        ("Sophia", "Bennett", "sophia@gmail.com", "sophia123456", "Proofreader and editor for tech blogs.", "Miami, FL", 35, "Writing", ["Proofreading", "Content Writing"]),
        ("Emma", "Collins", "emma@gmail.com", "emma123456", "Expert UI Designer for SaaS platforms.", "Atlanta, GA", 70, "Design", ["UI/UX Design"]),
        ("Lucas", "Turner", "lucas@gmail.com", "lucas123456", "Carpenter and custom furniture builder.", "Nashville, TN", 75, "Services", ["Carpentry"]),
        ("Nathan", "Mitchell", "nathan@gmail.com", "nathan123456", "Backend Developer and Cloud Architect.", "Los Angeles, CA", 85, "Tech", ["Web Development"]),
    ]

    db_users = []
    
    # Create Users
    for fname, lname, email, pwd, bio, loc, rate, cat, skills in users_data:
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(
                email=email,
                password=pwd,
                first_name=fname,
                last_name=lname,
                bio=bio,
                location=loc,
                hourly_rate=rate
            )
            print(f"Created user: {email}")
        else:
            print(f"User {email} already exists. Skipping creation.")
        db_users.append((user, skills, fname, cat))

    # Create Skills & Experience
    for user, skills, fname, cat_name in db_users:
        for sk_name in skills:
            UserSkill.objects.get_or_create(
                user=user,
                skill=db_skills[sk_name],
                defaults={'proficiency': 'expert', 'years_experience': random.randint(2, 10)}
            )
        
        # Experience
        Experience.objects.get_or_create(
            user=user,
            title=f"Senior {cat_name} Specialist",
            company=f"{fname} Consulting LLC",
            start_date=date(2018, 1, 1),
            defaults={'is_current': True, 'description': 'Providing top-tier services to various clients.'}
        )

    # Hire Requests & Reviews (Random spread)
    print("Creating Hire Requests and Reviews...")
    all_users = [u[0] for u in db_users]
    created_reviews = 0
    
    # Fixed random seed for a bit of predictability in distribution
    random.seed(42)
    
    for _ in range(30):
        client, provider = random.sample(all_users, 2)
        
        # Check if they already have a completed hire request
        existing_hr = HireRequest.objects.filter(client=client, provider=provider).exists()
        if not existing_hr:
            first_skill = provider.user_skills.first()
            skill_name = first_skill.skill.name if first_skill else 'Project'
            
            hr = HireRequest.objects.create(
                client=client,
                provider=provider,
                title=f"Need help with {skill_name}",
                description=f"Looking for expert assistance on a {skill_name} project.",
                status=HireRequest.Status.COMPLETED,
                completed_at=date.today() - timedelta(days=random.randint(1, 30))
            )
            
            # Review from Client to Provider
            rating = random.choices([5, 4, 3], weights=[60, 30, 10])[0]
            comments = {
                5: "Excellent work, highly recommended! Very professional.",
                4: "Good job, but took a bit longer than expected.",
                3: "Average work, communication could be better."
            }
            Review.objects.create(
                reviewer=client,
                reviewee=provider,
                hire_request=hr,
                rating=rating,
                comment=comments[rating]
            )
            created_reviews += 1

    print(f"\nSeed Complete!")
    print(f"Users in system: {User.objects.count()}")
    print(f"Profiles/UserSkills total: {UserSkill.objects.count()}")
    print(f"Reviews created total: {Review.objects.count()}")

run_seed()
