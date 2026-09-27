import os
import random
from datetime import date, timedelta
from django.core.files import File
from django.contrib.auth import get_user_model
from apps.skills.models import Category, Skill
from apps.profiles.models import UserSkill, Experience, Certificate
from apps.hiring.models import HireRequest
from apps.reviews.models import Review

User = get_user_model()

def run_seed():
    print("Starting seed of 15 fully completed users...")
    
    cats = {
        'Tech': ['DevOps', 'Data Science', 'Machine Learning', 'Frontend Dev', 'Backend Dev'],
        'Creative': ['Video Editing', '3D Modeling', 'Photography', 'Animation', 'Illustration'],
        'Marketing': ['SEO Expert', 'Social Media', 'Email Marketing', 'PPC Ads', 'Brand Strategy'],
        'Education': ['Math Tutor', 'Language Teacher', 'Physics Tutor', 'Music Instructor', 'Chess Coach'],
        'Trades': ['HVAC Tech', 'Welding', 'Landscaping', 'Roofing', 'Masonry']
    }
    
    db_skills = {}
    for c_name, s_list in cats.items():
        cat, _ = Category.objects.get_or_create(name=c_name, defaults={'sort_order': 1})
        for s_name in s_list:
            sk, _ = Skill.objects.get_or_create(name=s_name, category=cat)
            db_skills[s_name] = sk
            
    images_folder = r"C:\movies\skill-trade\assets"
    images = [
        "csgsffd.jpg", "dsvs.jpg", "hjgun.jpg", "jbxvsd.jpg", "jhizsd.jpg",
        "jhszi.jpg", "jxbdvjc.jpg", "sdvsd.jpg", "svds.jpg", "svfsv.jpg",
        "svs.jpg", "xbzc.jpg", "xfhbz.jpg", "ygbuk.jpg", "z fzvdz.jpg"
    ]
    
    users_data = [
        ("Arjun", "Reynolds", "arjun@gmail.com", "arjun123456", "DevOps Engineer building scalable infra.", "Austin, TX", 85, "Tech", ["DevOps", "Backend Dev", "Data Science"]),
        ("Oliver", "Hayes", "oliver@gmail.com", "oliver123456", "Video Editor & Motion Graphics Artist.", "Los Angeles, CA", 60, "Creative", ["Video Editing", "Animation", "3D Modeling", "Photography"]),
        ("Benjamin", "Foster", "benjamin@gmail.com", "benjamin123456", "SEO Consultant helping brands rank.", "New York, NY", 70, "Marketing", ["SEO Expert", "PPC Ads", "Social Media", "Email Marketing"]),
        ("Noah", "Richardson", "noah@gmail.com", "noah123456", "Experienced Math & Physics Tutor.", "Chicago, IL", 45, "Education", ["Math Tutor", "Physics Tutor", "Language Teacher"]),
        ("William", "Anderson", "william@gmail.com", "william123456", "Licensed HVAC Technician.", "Houston, TX", 75, "Trades", ["HVAC Tech", "Welding", "Masonry"]),
        ("Jacob", "Sullivan", "jacob@gmail.com", "jacob123456", "Data Scientist with NLP focus.", "San Francisco, CA", 110, "Tech", ["Data Science", "Machine Learning", "Backend Dev"]),
        ("Christopher", "Mason", "christopher@gmail.com", "christopher123456", "Creative Photographer and Retoucher.", "Miami, FL", 55, "Creative", ["Photography", "Video Editing", "Illustration"]),
        ("Samuel", "Harrison", "samuel@gmail.com", "samuel123456", "Email Marketing Specialist.", "Denver, CO", 65, "Marketing", ["Email Marketing", "Brand Strategy", "SEO Expert"]),
        ("Andrew", "Bennett", "andrew@gmail.com", "andrew123456", "Professional Music Instructor.", "Nashville, TN", 50, "Education", ["Music Instructor", "Language Teacher", "Math Tutor"]),
        ("Joshua", "Phillips", "joshua@gmail.com", "joshua123456", "Expert Welder & Metal Fabricator.", "Detroit, MI", 80, "Trades", ["Welding", "Roofing", "Masonry"]),
        ("Gabriel", "Dawson", "gabriel@gmail.com", "gabriel123456", "Frontend Developer specializing in React.", "Seattle, WA", 90, "Tech", ["Frontend Dev", "Backend Dev", "Data Science"]),
        ("Isaac", "Montgomery", "isaac@gmail.com", "isaac123456", "3D Modeler for indie games.", "Portland, OR", 65, "Creative", ["3D Modeling", "Animation", "Illustration"]),
        ("Dylan", "Richardson", "dylan@gmail.com", "dylan123456", "Brand Strategist and Marketer.", "Atlanta, GA", 85, "Marketing", ["Brand Strategy", "PPC Ads", "Social Media"]),
        ("Connor", "Wallace", "connor@gmail.com", "connor123456", "Language Teacher (Spanish/English).", "Phoenix, AZ", 40, "Education", ["Language Teacher", "Music Instructor", "Chess Coach"]),
        ("Adam", "Fletcher", "adam@gmail.com", "adam123456", "Professional Landscaper and Designer.", "Dallas, TX", 55, "Trades", ["Landscaping", "Roofing", "Masonry"]),
    ]
    
    db_users = []
    
    for i, (fname, lname, email, pwd, bio, loc, rate, cat, skills) in enumerate(users_data):
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(
                email=email,
                password=pwd,
                first_name=fname,
                last_name=lname,
                bio=bio,
                location=loc,
                hourly_rate=rate,
                is_email_verified=True
            )
            
            img_path = os.path.join(images_folder, images[i])
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    user.profile_photo.save(images[i], File(f), save=True)
            print(f"Created user: {email}")
        else:
            print(f"User {email} already exists. Updating is_email_verified...")
            if not user.is_email_verified:
                user.is_email_verified = True
                user.save()
            if not user.profile_photo:
                img_path = os.path.join(images_folder, images[i])
                if os.path.exists(img_path):
                    with open(img_path, 'rb') as f:
                        user.profile_photo.save(images[i], File(f), save=True)
                        
        db_users.append((user, skills, fname, cat))

    for i, (user, skills, fname, cat_name) in enumerate(db_users):
        # Skills
        for sk_name in skills:
            UserSkill.objects.get_or_create(
                user=user,
                skill=db_skills[sk_name],
                defaults={'proficiency': 'expert', 'years_experience': random.randint(3, 15)}
            )
        
        # Experience
        Experience.objects.get_or_create(
            user=user,
            title=f"Senior {cat_name} Specialist",
            company=f"{fname} Services",
            start_date=date(2015, 6, 1),
            defaults={'is_current': True, 'description': f'Delivering high quality {cat_name} work.'}
        )
        
        # Certificate
        cert, created = Certificate.objects.get_or_create(
            user=user,
            name=f"Certified {cat_name} Professional",
            issuer=f"Global {cat_name} Board",
            issue_date=date(2018, 5, 10),
            defaults={'description': f'Official certification for {cat_name} expertise.'}
        )
        if created:
            cert_img_path = os.path.join(images_folder, images[i])
            if os.path.exists(cert_img_path):
                with open(cert_img_path, 'rb') as f:
                    cert.image.save(f"cert_{images[i]}", File(f), save=True)
                
    # Hire Requests & Reviews
    print("Creating Hire Requests and Reviews...")
    all_users = [u[0] for u in db_users]
    
    random.seed(101)
    
    for _ in range(25):
        client, provider = random.sample(all_users, 2)
        
        existing_hr = HireRequest.objects.filter(client=client, provider=provider).exists()
        if not existing_hr:
            first_skill = provider.user_skills.first()
            skill_name = first_skill.skill.name if first_skill else 'Consulting'
            
            hr = HireRequest.objects.create(
                client=client,
                provider=provider,
                title=f"Hiring for {skill_name}",
                description=f"Need help immediately with {skill_name}.",
                status=HireRequest.Status.COMPLETED,
                completed_at=date.today() - timedelta(days=random.randint(2, 60))
            )
            
            rating = random.choices([5, 4, 3], weights=[70, 20, 10])[0]
            comments = {
                5: "Absolutely fantastic! Delivered on time and exceeded expectations.",
                4: "Great work, very solid. Would hire again.",
                3: "It was okay, got the job done."
            }
            Review.objects.create(
                reviewer=client,
                reviewee=provider,
                hire_request=hr,
                rating=rating,
                comment=comments[rating]
            )

    print("\nSeed Complete!")

run_seed()
