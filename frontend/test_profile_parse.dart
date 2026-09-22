import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';

// Copy models here
class UserProfile {
  final int id;
  final String email;
  final String firstName;
  final String lastName;
  final String fullName;
  final double hourlyRate;
  final String availability;
  final List skills;
  final List experiences;
  final List education;
  final List certificates;
  final List portfolio;
  final double? averageRating;
  final int totalReviews;

  UserProfile({
    required this.id, required this.email, required this.firstName, required this.lastName, required this.fullName, required this.hourlyRate, required this.availability, required this.skills, required this.experiences, required this.education, required this.certificates, required this.portfolio, this.averageRating, required this.totalReviews,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      id: json['id'],
      email: json['email'],
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      fullName: json['full_name'] ?? '',
      hourlyRate: double.tryParse(json['hourly_rate']?.toString() ?? '0') ?? 0.0,
      availability: json['availability'] ?? 'UNAVAILABLE',
      skills: json['skills'] ?? [],
      experiences: json['experiences'] ?? [],
      education: json['education'] ?? [],
      certificates: json['certificates'] ?? [],
      portfolio: json['portfolio'] ?? [],
      averageRating: json['average_rating'] != null ? (json['average_rating'] as num).toDouble() : null,
      totalReviews: json['total_reviews'] ?? 0,
    );
  }
}

void main() {
  final jsonString = '''
{
  "id": 19,
  "email": "usera_3265@example.com",
  "first_name": "TestClient",
  "last_name": "A",
  "full_name": "TestClient A",
  "phone": "",
  "profile_photo": null,
  "bio": "",
  "location": "",
  "github_url": "",
  "linkedin_url": "",
  "hourly_rate": null,
  "languages": [],
  "availability": "available",
  "skills": [],
  "experiences": [],
  "education": [],
  "certificates": [],
  "portfolio": [],
  "average_rating": null,
  "total_reviews": 0,
  "created_at": "2026-09-22T21:53:53.957660+05:30"
}
  ''';
  
  try {
    final parsed = jsonDecode(jsonString);
    final profile = UserProfile.fromJson(parsed);
    print("SUCCESS: profile id \${profile.id}");
  } catch (e, st) {
    print("FAILED: \$e\\n\$st");
  }
}
