# Database Schema for Skill Swap

## App: Authentication (apps.authentication)

### Table: `users` (Model: `User`)
| Field Name | Type | Properties |
|---|---|---|
| `logentry` | ForeignKey | Null, FK -> LogEntry |
| `outstandingtoken` | ForeignKey | Null, FK -> OutstandingToken |
| `otp_codes` | ForeignKey | Null, FK -> OTPCode |
| `user_skills` | ForeignKey | Null, FK -> UserSkill |
| `experiences` | ForeignKey | Null, FK -> Experience |
| `education_entries` | ForeignKey | Null, FK -> Education |
| `certificates` | ForeignKey | Null, FK -> Certificate |
| `portfolio_items` | ForeignKey | Null, FK -> Portfolio |
| `sent_hire_requests` | ForeignKey | Null, FK -> HireRequest |
| `received_hire_requests` | ForeignKey | Null, FK -> HireRequest |
| `sent_messages` | ForeignKey | Null, FK -> Message |
| `received_messages` | ForeignKey | Null, FK -> Message |
| `notifications` | ForeignKey | Null, FK -> Notification |
| `reviews_given` | ForeignKey | Null, FK -> Review |
| `reviews_received` | ForeignKey | Null, FK -> Review |
| `bookmarks` | ForeignKey | Null, FK -> Bookmark |
| `bookmarked_by` | ForeignKey | Null, FK -> Bookmark |
| `reports_filed` | ForeignKey | Null, FK -> Report |
| `reports_against` | ForeignKey | Null, FK -> Report |
| `id` | BigAutoField | PK, Unique, Blank |
| `password` | CharField | - |
| `last_login` | DateTimeField | Null, Blank |
| `is_superuser` | BooleanField | - |
| `is_staff` | BooleanField | - |
| `date_joined` | DateTimeField | - |
| `email` | CharField | Unique |
| `first_name` | CharField | - |
| `last_name` | CharField | - |
| `phone` | CharField | Blank |
| `profile_photo` | FileField | Null, Blank |
| `bio` | TextField | Blank |
| `location` | CharField | Blank |
| `github_url` | CharField | Blank |
| `linkedin_url` | CharField | Blank |
| `hourly_rate` | DecimalField | Null, Blank |
| `languages` | JSONField | Blank |
| `availability` | CharField | - |
| `is_admin` | BooleanField | - |
| `is_verified` | BooleanField | - |
| `is_active` | BooleanField | - |
| `is_deleted` | BooleanField | - |
| `deleted_at` | DateTimeField | Null, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `groups` | ManyToManyField | Blank, FK -> Group |
| `user_permissions` | ManyToManyField | Blank, FK -> Permission |

### Table: `otp_codes` (Model: `OTPCode`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `user` | ForeignKey | FK -> User |
| `code` | CharField | - |
| `purpose` | CharField | - |
| `is_used` | BooleanField | - |
| `expires_at` | DateTimeField | - |
| `created_at` | DateTimeField | Blank |

## App: Skills & Categories (apps.skills)

### Table: `categories` (Model: `Category`)
| Field Name | Type | Properties |
|---|---|---|
| `skills` | ForeignKey | Null, FK -> Skill |
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `is_deleted` | BooleanField | - |
| `deleted_at` | DateTimeField | Null, Blank |
| `name` | CharField | Unique |
| `icon` | CharField | Blank |
| `description` | TextField | Blank |
| `sort_order` | IntegerField | - |
| `is_active` | BooleanField | - |

### Table: `skills` (Model: `Skill`)
| Field Name | Type | Properties |
|---|---|---|
| `user_skills` | ForeignKey | Null, FK -> UserSkill |
| `portfolio_items` | ForeignKey | Null, FK -> Portfolio |
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `is_deleted` | BooleanField | - |
| `deleted_at` | DateTimeField | Null, Blank |
| `name` | CharField | Unique |
| `description` | TextField | Blank |
| `category` | ForeignKey | FK -> Category |
| `is_active` | BooleanField | - |

## App: User Profiles (apps.profiles)

### Table: `user_skills` (Model: `UserSkill`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `user` | ForeignKey | FK -> User |
| `skill` | ForeignKey | FK -> Skill |
| `proficiency` | CharField | - |
| `price` | DecimalField | Null, Blank |
| `description` | TextField | Blank |
| `years_experience` | PositiveIntegerField | - |
| `is_active` | BooleanField | - |

### Table: `experiences` (Model: `Experience`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `user` | ForeignKey | FK -> User |
| `title` | CharField | - |
| `company` | CharField | - |
| `start_date` | DateField | - |
| `end_date` | DateField | Null, Blank |
| `description` | TextField | Blank |
| `is_current` | BooleanField | - |

### Table: `education` (Model: `Education`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `user` | ForeignKey | FK -> User |
| `degree` | CharField | - |
| `institution` | CharField | - |
| `field_of_study` | CharField | Blank |
| `start_date` | DateField | - |
| `end_date` | DateField | Null, Blank |
| `description` | TextField | Blank |

### Table: `certificates` (Model: `Certificate`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `user` | ForeignKey | FK -> User |
| `name` | CharField | - |
| `issuer` | CharField | - |
| `credential_url` | CharField | Blank |
| `credential_id` | CharField | Blank |
| `issue_date` | DateField | - |
| `expiry_date` | DateField | Null, Blank |
| `image` | FileField | Null, Blank |

### Table: `portfolio` (Model: `Portfolio`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `user` | ForeignKey | FK -> User |
| `title` | CharField | - |
| `description` | TextField | Blank |
| `url` | CharField | Blank |
| `image` | FileField | Null, Blank |
| `skill` | ForeignKey | Null, Blank, FK -> Skill |

## App: Hiring & Requests (apps.hiring)

### Table: `hire_requests` (Model: `HireRequest`)
| Field Name | Type | Properties |
|---|---|---|
| `messages` | ForeignKey | Null, FK -> Message |
| `reviews` | ForeignKey | Null, FK -> Review |
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `client` | ForeignKey | FK -> User |
| `provider` | ForeignKey | FK -> User |
| `title` | CharField | - |
| `description` | TextField | - |
| `budget` | DecimalField | Null, Blank |
| `deadline` | DateField | Null, Blank |
| `attachments` | JSONField | Blank |
| `status` | CharField | - |
| `rejection_reason` | TextField | Blank |
| `completed_at` | DateTimeField | Null, Blank |

## App: Messaging (apps.messaging)

### Table: `messages` (Model: `Message`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `sender` | ForeignKey | FK -> User |
| `receiver` | ForeignKey | FK -> User |
| `hire_request` | ForeignKey | Null, Blank, FK -> HireRequest |
| `content` | TextField | - |
| `attachment` | FileField | Null, Blank |
| `is_read` | BooleanField | - |
| `read_at` | DateTimeField | Null, Blank |

## App: Notifications (apps.notifications)

### Table: `notifications` (Model: `Notification`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `user` | ForeignKey | FK -> User |
| `title` | CharField | - |
| `message` | TextField | - |
| `type` | CharField | - |
| `data` | JSONField | Blank |
| `is_read` | BooleanField | - |
| `read_at` | DateTimeField | Null, Blank |

## App: Reviews & Ratings (apps.reviews)

### Table: `reviews` (Model: `Review`)
| Field Name | Type | Properties |
|---|---|---|
| `reports` | ForeignKey | Null, FK -> Report |
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `is_deleted` | BooleanField | - |
| `deleted_at` | DateTimeField | Null, Blank |
| `reviewer` | ForeignKey | FK -> User |
| `reviewee` | ForeignKey | FK -> User |
| `hire_request` | ForeignKey | FK -> HireRequest |
| `rating` | PositiveSmallIntegerField | - |
| `comment` | TextField | Blank |
| `screenshot` | FileField | Null, Blank |
| `is_reported` | BooleanField | - |

## App: Bookmarks (apps.bookmarks)

### Table: `bookmarks` (Model: `Bookmark`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `user` | ForeignKey | FK -> User |
| `bookmarked_user` | ForeignKey | FK -> User |

## App: Reports & Moderation (apps.reports)

### Table: `reports` (Model: `Report`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `created_at` | DateTimeField | Blank |
| `updated_at` | DateTimeField | Blank |
| `reporter` | ForeignKey | FK -> User |
| `reported_user` | ForeignKey | Null, Blank, FK -> User |
| `reported_review` | ForeignKey | Null, Blank, FK -> Review |
| `type` | CharField | - |
| `reason` | TextField | - |
| `status` | CharField | - |
| `admin_notes` | TextField | Blank |
| `resolved_at` | DateTimeField | Null, Blank |

## App: Admin Panel (apps.admin_panel)

### Table: `admin_settings` (Model: `AdminSettings`)
| Field Name | Type | Properties |
|---|---|---|
| `id` | BigAutoField | PK, Unique, Blank |
| `key` | CharField | Unique |
| `value` | TextField | Blank |
| `description` | CharField | Blank |
| `updated_at` | DateTimeField | Blank |
