# Data Flow Diagrams (DFD) - Skill Trade

This document provides the complete Data Flow Diagram (DFD) specifications for the **Skill Trade** project, structured into **Level 0 (Context Diagram)**, **Level 1 (User & Core System Processes)**, and **Level 2 (Admin Moderation Processes)**.

---

## 1. DFD Level 0 (Context Diagram)

The **Level 0 Context Diagram** provides a high-level overview of the **Skill Trade System**, detailing external entities (User, Admin, Email Service, Cloudinary Storage) and the fundamental data flows into and out of the system.

```mermaid
graph TD
    User["👤 User (Client / Provider)"]
    Admin["⚙️ Admin / Moderator"]
    EmailSvc["📧 Email Service (OTP)"]
    Cloudinary["☁️ Cloudinary Storage"]

    System(("0.0 <br> Skill Trade <br> System"))

    %% User Flow
    User -->|Registration & Login Data| System
    User -->|Profile & Skill Details| System
    User -->|Hire Requests & Messages| System
    User -->|Reviews & Reports| System

    System -->|Auth Token & Notifications| User
    System -->|Skill Search & Profile Data| User
    System -->|Hire Request Status & Messages| User

    %% Admin Flow
    Admin -->|Admin Credentials| System
    Admin -->|Report Resolution & Moderation| System
    Admin -->|Category & Settings Config| System

    System -->|Moderation Reports & User Data| Admin
    System -->|System Analytics & Settings| Admin

    %% External Services Flow
    System -->|Send OTP Verification| EmailSvc
    System -->|Upload Profile/Media Files| Cloudinary
    Cloudinary -->|Return Media URLs| System
```

### Data Flow Descriptions (Level 0)

* **User Input**: Registration credentials, OTP verification codes, profile details, skills offered, hire requests, chat messages, ratings/reviews, content reports, bookmarks.
* **System Output to User**: JWT authentication tokens, search results, hire request status updates, real-time messages, in-app notifications, peer feedback.
* **Admin Input**: Login credentials, report resolution actions, category updates, user moderation flags, global platform settings.
* **System Output to Admin**: Pending moderation reports, platform analytics, system logs, user management lists.
* **External Systems**:
  * **Email Service**: Handles delivery of email OTP codes for user verification.
  * **Cloudinary**: Handles cloud-based storage for images (profile pictures, portfolio items, certificate proofs, review screenshots).

---

## 2. DFD Level 1 (User & Core System Processes)

The **Level 1 DFD** breaks down the central system into core functional processes and illustrates interactions with the primary database stores (`D1` through `D6`).

```mermaid
graph TD
    %% External Entities
    User["👤 User"]

    %% Data Stores
    D1[("D1: Users")]
    D2[("D2: Skills & Categories")]
    D3[("D3: Hire Requests")]
    D4[("D4: Messages")]
    D5[("D5: Reviews & Reports")]
    D6[("D6: Notifications")]

    %% Level 1 Processes
    P1(("1.0 <br> User Auth & Profile <br> Management"))
    P2(("2.0 <br> Skill & Portfolio <br> Management"))
    P3(("3.0 <br> Hiring & Request <br> Management"))
    P4(("4.0 <br> Messaging & <br> Notifications"))
    P5(("5.0 <br> Reviews & <br> Reporting"))

    %% Data Flows for P1
    User -->|1. Credentials / OTP / Profile Info| P1
    P1 -->|Store User Profile Data| D1
    D1 -->|Fetch User Credentials / Profile| P1
    P1 -->|JWT Token / Profile Response| User

    %% Data Flows for P2
    User -->|2. Search Skills / Add Skill & Portfolio| P2
    P2 -->|Save User Skills & Portfolio| D2
    D2 -->|Fetch Skill Categories & Skills Feed| P2
    P2 -->|Skill List & Search Results| User

    %% Data Flows for P3
    User -->|3. Create / Accept / Complete Hire Request| P3
    P3 -->|Write Hire Request State| D3
    D3 -->|Fetch Hire Request Details| P3
    D1 -->|Validate Client & Provider| P3
    P3 -->|Hire Request Status Updates| User

    %% Data Flows for P4
    User -->|4. Send Message / View Notifications| P4
    P4 -->|Store Message| D4
    P4 -->|Create Notification Record| D6
    D4 -->|Retrieve Chat History| P4
    D6 -->|Fetch User Notifications| P4
    P4 -->|Deliver Chat & Notifications| User

    %% Data Flows for P5
    User -->|5. Post Review / File Report| P5
    P5 -->|Write Review & Report Data| D5
    D3 -->|Verify Completed Request for Review| P5
    P5 -->|Confirmation / Review Feed| User
```

---

## 3. DFD Level 2 (Admin Moderation & Panel Processes)

The **Level 2 DFD** decomposes administrative control and moderation operations (Process `6.0`), showing how platform administrators inspect reports, moderate content, manage skill categories, and configure application settings.

```mermaid
graph TD
    %% External Entity
    Admin["⚙️ Admin / Moderator"]

    %% Data Stores
    D1[("D1: Users")]
    D2[("D2: Skills & Categories")]
    D5[("D5: Reviews & Reports")]
    D7[("D7: Admin Settings")]

    %% Level 2 Processes under 6.0 (Admin System)
    P6_1(("6.1 <br> Admin Auth & <br> Dashboard"))
    P6_2(("6.2 <br> Report & Content <br> Moderation"))
    P6_3(("6.3 <br> User & Category <br> Management"))
    P6_4(("6.4 <br> Platform Settings <br> Config"))

    %% P6.1 Admin Auth & Dashboard
    Admin -->|Admin Credentials| P6_1
    D1 -->|Verify Admin Privileges| P6_1
    P6_1 -->|Dashboard Statistics| Admin

    %% P6.2 Moderation
    Admin -->|Resolve / Dismiss Report| P6_2
    D5 -->|Fetch Pending Reports| P6_2
    P6_2 -->|Update Report Status & Admin Notes| D5
    P6_2 -->|Flag / Delete Abusive Review| D5

    %% P6.3 User & Category Management
    Admin -->|Manage Skill Categories / Soft Delete User| P6_3
    P6_3 -->|Update User Status / Soft Delete| D1
    P6_3 -->|Create / Update Categories| D2

    %% P6.4 System Config
    Admin -->|Update System Settings| P6_4
    P6_4 -->|Store Key-Value Configuration| D7
    D7 -->|Read Settings| P6_4
    P6_4 -->|Current Configuration State| Admin
```

---

## 4. Data Store Mapping Summary

| Data Store ID | Data Store Name | Description | Related Database Tables |
| :--- | :--- | :--- | :--- |
| **D1** | Users Store | Stores account credentials, profile details, availability, and verification metrics. | `users` |
| **D2** | Skills & Categories Store | Contains skill categories, master skills, individual user skill offerings, and portfolio items. | `categories`, `skills`, `user_skills`, `portfolio`, `experiences`, `education`, `certificates` |
| **D3** | Hire Requests Store | Manages contracts and status transitions (Pending, Accepted, Completed, Rejected, Cancelled). | `hire_requests` |
| **D4** | Messages Store | Stores 1:1 chat conversations between clients and providers. | `messages` |
| **D5** | Reviews & Reports Store | Manages peer feedback ratings, comments, and submitted moderation reports. | `reviews`, `reports` |
| **D6** | Notifications Store | Stores in-app user notifications and bookmarked profile links. | `notifications`, `bookmarks` |
| **D7** | Admin Settings Store | Key-value store for platform-wide options and administrative parameters. | `admin_settings` |
