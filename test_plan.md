# Academic Advisor Chatbot - Comprehensive Test Plan

## Overview

This test plan covers the **UPM Academic Advisor Chatbot** built on Rasa Pro CALM architecture with GPT-4o-mini LLM integration. The chatbot helps students with course information, prerequisites, academic procedures, and general inquiries.

---

## System Under Test

| Component | Technology | Description |
|-----------|------------|-------------|
| NLU Pipeline | Rasa Pro CALM + GPT-4o-mini | Intent recognition and dialogue management |
| Custom Actions | Python + Rasa SDK | Database queries and OpenAI fallback |
| Database | SQLite (`academic.db`) | Course and prerequisite data |
| Tracker Store | SQLite (`tracker.db`) | Conversation history |
| Channels | Telegram, REST API | User interfaces |

---

## Test Categories

### 1. Unit Tests - Custom Actions

#### 1.1 `ActionGetCourseDetails`

| Test ID | Test Case | Input | Expected Result |
|---------|-----------|-------|-----------------|
| UT-001 | Valid course code (uppercase) | `course_code="CCS3101"` | Returns course_name, credits, synopsis, prereq_list, return_value="course_found" |
| UT-002 | Valid course code (lowercase) | `course_code="ccs3101"` | Normalizes to uppercase, returns course details |
| UT-003 | Invalid course code | `course_code="INVALID999"` | Returns return_value="course_not_found" |
| UT-004 | Empty course code | `course_code=""` | Returns return_value="course_not_found" |
| UT-005 | None course code | `course_code=None` | Returns return_value="course_not_found" |
| UT-006 | Course with prerequisites | Course having prereqs | Returns formatted prereq_list |
| UT-007 | Course without prerequisites | Course without prereqs | Returns prereq_list="None" |
| UT-008 | Database connection error | Simulated DB failure | Returns return_value="course_not_found" |

#### 1.2 `ActionCheckPrerequisites`

| Test ID | Test Case | Input | Expected Result |
|---------|-----------|-------|-----------------|
| UT-009 | Course with prerequisites | Valid course with prereqs | Returns has_prerequisites=True, formatted prereq_list |
| UT-010 | Course without prerequisites | Valid course without prereqs | Returns has_prerequisites=False, prereq_list="None" |
| UT-011 | Non-existent course | Invalid course code | Returns return_value="course_not_found" |
| UT-012 | Null course code slot | None | Returns return_value="course_not_found" |

#### 1.3 `ActionOpenAIResponse`

| Test ID | Test Case | Input | Expected Result |
|---------|-----------|-------|-----------------|
| UT-013 | Valid user message | "What courses are available?" | Returns OpenAI-generated response |
| UT-014 | Empty user message | "" | Returns fallback message asking to rephrase |
| UT-015 | OpenAI API error | Simulate API failure | Returns error message with contact info |
| UT-016 | Context retrieval test | Query with matching keywords | Returns relevant context from database |

#### 1.4 Database Helper Functions

| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| UT-017 | `get_db_connection()` | Returns valid SQLite connection |
| UT-018 | `get_prerequisites_for_course()` with valid course | Returns formatted prerequisite list |
| UT-019 | `get_prerequisites_for_course()` with no prereqs | Returns None |

---

### 2. Integration Tests - Flows

> [!IMPORTANT]
> This section covers **all 24 conversation flows** organized by category.

---

#### 2.1 Database-Connected Flows (Custom Actions)

##### `get_course_info` Flow

| Test ID | Test Case | User Input | Expected Bot Response |
|---------|-----------|------------|----------------------|
| IT-001 | Complete flow - valid course | "Tell me about CCS3101" | Course details with name, credits, synopsis, prerequisites |
| IT-002 | Flow with course code prompt | "I want course information" → "CCS3101" | Asks for course code, then returns details |
| IT-003 | Flow with invalid course | "Tell me about XYZ999" | Course not found message with suggestions |
| IT-004 | Flow interruption | User changes topic mid-flow | Graceful handling or context switch |

##### `check_prerequisite` Flow

| Test ID | Test Case | User Input | Expected Bot Response |
|---------|-----------|------------|----------------------|
| IT-005 | Check prereqs (has prereqs) | "What are the prerequisites for CSC4600?" | Lists prerequisites with course names |
| IT-006 | Check prereqs (no prereqs) | Course without prereqs | "No prerequisites required!" message |
| IT-007 | Invalid course check | "Prerequisites for FAKE123" | Course not found error message |
| IT-008 | Slot collection test | "Check prerequisites" → "CSC4600" | Prompts for course code, then returns result |

---

#### 2.2 Academic Information Flows (9 flows)

| Test ID | Flow | Sample User Input | Expected Response Contains |
|---------|------|-------------------|---------------------------|
| IT-009 | `career_prospects` | "What jobs can I get with CS degree?" | Career options, industry info |
| IT-010 | `convocation_info` | "When is convocation?" / "graduation ceremony" | Ceremony date, registration, attire |
| IT-011 | `deans_list` | "What is Dean's List?" / "anugerah dekan" | CGPA requirements, rewards |
| IT-012 | `drop_course` | "How to drop a subject?" / "withdraw from course" | TD procedure, deadline, penalties |
| IT-013 | `exam_regulations` | "Exam dress code" / "what can I bring to exam?" | Rules, dress code, allowed items |
| IT-014 | `exam_schedule` | "When is my exam?" / "exam timetable" | Exam dates, venues, timetable info |
| IT-015 | `graduation_requirements` | "How to graduate?" / "how many credits needed?" | Credit requirements, CGPA, FYP |
| IT-016 | `muet_requirement` | "What MUET band do I need?" | Minimum band requirement |
| IT-017 | `registration_deadline` | "When is registration deadline?" / "add drop period" | Important dates, deadlines |

---

#### 2.3 Policy Flows (8 flows)

| Test ID | Flow | Sample User Input | Expected Response Contains |
|---------|------|-------------------|---------------------------|
| IT-018 | `change_program` | "How to change major?" / "switch from CS to SE" | Procedure, requirements, deadline |
| IT-019 | `credit_transfer` | "How to apply credit exemption?" | Transfer procedure, diploma credits |
| IT-020 | `deferment_info` | "How to defer?" / "take a break from study" | LOA procedure, deadline |
| IT-021 | `elective_options` | "What electives can I take?" / "easy electives" | Elective courses, recommendations |
| IT-022 | `grade_appeal` | "How to appeal grade?" / "my marks are wrong" | Appeal procedure, deadline, fees |
| IT-023 | `industrial_training` | "When can I do internship?" / "LI requirements" | LI requirements, registration |
| IT-024 | `probation_info` | "What is probation?" / "my CGPA is below 2.0" | P1/P2/P3 status, recovery steps |
| IT-025 | `repeat_policy` | "I failed a subject" / "how to repeat course?" | Repeat policy, grade replacement |

---

#### 2.4 Admin/Support Flows (6 flows)

| Test ID | Flow | Sample User Input | Expected Response Contains |
|---------|------|-------------------|---------------------------|
| IT-026 | `class_full` | "Class is full" / "cannot register" | Alternative options, waitlist |
| IT-027 | `fees_block` | "Fees block" / "financial hold" | Payment procedure, contact |
| IT-028 | `system_issues` | "Cannot login SMP" / "forgot password" | Portal help, password reset |
| IT-029 | `timetable_clash` | "Timetable clash" / "two subjects same time" | Conflict resolution |
| IT-030 | `verification_letter` | "Verification letter" | Request procedure |

---

#### 2.5 Critical Safety Flow ⚠️

> [!CAUTION]
> **Mental health support is a CRITICAL flow** that must be tested with care.

| Test ID | Flow | Sample User Input | Expected Response Contains |
|---------|------|-------------------|---------------------------|
| IT-031 | `mental_health_support` | "I want to give up" | Crisis resources, UPM counseling contact |
| IT-032 | `mental_health_support` | "feeling depressed" | Mental health resources, support info |
| IT-033 | `mental_health_support` | "stressed and cannot cope" | Coping resources, professional help |
| IT-034 | `mental_health_support` | "suicidal thoughts" | **IMMEDIATE** crisis hotline, emergency contacts |

---

#### 2.6 General Conversation Flows (5 flows)

| Test ID | Flow | Sample User Input | Expected Response |
|---------|------|-------------------|-------------------|
| IT-035 | `hello` | "Hello" / "Hi" | Friendly welcome message |
| IT-036 | `help` | "Help" / "What can you do?" | Capabilities list |
| IT-037 | `goodbye` | "Bye" / "Goodbye" | Farewell message |
| IT-038 | `thank_you` | "Thanks" / "Thank you" | Acknowledgment |
| IT-039 | `bot_identity` | "Who are you?" | UPM Academic Advisor intro |

---

### 3. End-to-End Tests - Channel Integration

#### 3.1 REST API Testing

| Test ID | Test Case | Endpoint | Method | Expected Result |
|---------|-----------|----------|--------|-----------------|
| E2E-001 | Send message | `/webhooks/rest/webhook` | POST | Valid JSON response with bot message |
| E2E-002 | Health check | `/` | GET | Server status 200 OK |
| E2E-003 | Multiple messages | Sequential requests | POST | Maintains conversation context |

#### 3.2 Telegram Channel Testing

| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| E2E-004 | Send text message | Bot responds appropriately |
| E2E-005 | Start command | Bot sends welcome message |
| E2E-006 | Help command | Bot lists capabilities |
| E2E-007 | Webhook connectivity | Messages reach Rasa server |

---

### 4. Database Tests

#### 4.1 Data Integrity

| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| DB-001 | Courses table exists | Table accessible with expected schema |
| DB-002 | Prerequisites table exists | Table accessible with expected schema |
| DB-003 | Prerequisites reference valid courses | All prereq_code values exist in courses table |
| DB-004 | Course codes are unique | No duplicate course_code entries |

#### 4.2 Query Performance

| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| DB-005 | Course lookup by code | Response < 100ms |
| DB-006 | Prerequisites join query | Response < 200ms |
| DB-007 | Keyword search for context | Response < 500ms |

---

### 5. LLM/NLU Tests

#### 5.1 Intent Recognition (CALM) - All 24 Flows

| Test ID | User Input | Expected Flow |
|---------|------------|---------------|
| NLU-001 | "Tell me about CCS3101" | `get_course_info` |
| NLU-002 | "Prerequisites for CSC4600" | `check_prerequisite` |
| NLU-003 | "What jobs can I get?" | `career_prospects` |
| NLU-004 | "When is convocation?" | `convocation_info` |
| NLU-005 | "What is Dean's List?" | `deans_list` |
| NLU-006 | "How to drop a subject?" | `drop_course` |
| NLU-007 | "Exam dress code" | `exam_regulations` |
| NLU-008 | "When is my exam?" | `exam_schedule` |
| NLU-009 | "How to graduate?" | `graduation_requirements` |
| NLU-010 | "What MUET band needed?" | `muet_requirement` |
| NLU-011 | "Registration deadline?" | `registration_deadline` |
| NLU-012 | "How to change major?" | `change_program` |
| NLU-013 | "Credit exemption?" | `credit_transfer` |
| NLU-014 | "How to defer studies?" | `deferment_info` |
| NLU-015 | "What electives available?" | `elective_options` |
| NLU-016 | "Appeal my grade" | `grade_appeal` |
| NLU-017 | "Internship requirements" | `industrial_training` |
| NLU-018 | "CGPA below 2.0" | `probation_info` |
| NLU-019 | "Failed a subject" | `repeat_policy` |
| NLU-020 | "Class is full" | `class_full` |
| NLU-021 | "Cannot login SMP" | `system_issues` |
| NLU-022 | "Timetable clash" | `timetable_clash` |
| NLU-023 | "Feeling stressed" | `mental_health_support` |
| NLU-024 | "Hello" / "Help" / "Bye" | General flows |

#### 5.2 Slot Extraction

| Test ID | User Input | Expected Slot |
|---------|------------|---------------|
| NLU-009 | "Tell me about CCS3101" | course_code="CCS3101" |
| NLU-010 | "Prerequisites for csc4600" | course_code="CSC4600" |
| NLU-011 | "Course info" (no code) | course_code=None (should prompt) |

#### 5.3 OpenAI Fallback

| Test ID | Test Case | Expected Result |
|---------|-----------|-----------------|
| NLU-012 | Out-of-scope query | Triggers `action_openai_response` |
| NLU-013 | Complex academic question | OpenAI provides contextual answer |
| NLU-014 | Non-academic query | Polite redirection to academic topics |

---

### 6. Error Handling Tests

| Test ID | Test Case | Expected Behavior |
|---------|-----------|-------------------|
| ERR-001 | Database unavailable | Graceful error message, no crash |
| ERR-002 | OpenAI API timeout | Fallback error message with contact info |
| ERR-003 | Invalid API key | Error logged, fallback response |
| ERR-004 | Malformed user input | Bot asks for clarification |
| ERR-005 | Empty message | Bot prompts for input |
| ERR-006 | Very long message | Handled without truncation errors |

---

### 7. Performance Tests

| Test ID | Test Case | Success Criteria |
|---------|-----------|------------------|
| PERF-001 | Response time (local) | < 3 seconds |
| PERF-002 | Concurrent users (5) | All requests handled |
| PERF-003 | Action server latency | < 500ms for DB queries |
| PERF-004 | Model loading time | < 30 seconds |

---

### 8. Security Tests

| Test ID | Test Case | Expected Behavior |
|---------|-----------|-------------------|
| SEC-001 | SQL injection attempt | Query sanitized, no data leak |
| SEC-002 | XSS in user input | Input escaped in responses |
| SEC-003 | API key exposure | Keys not logged or exposed |
| SEC-004 | Unauthorized tracker access | Tracker store protected |

---

## Test Execution Commands

### Prerequisites

```bash
# Navigate to project directory
cd "c:\Users\ADMIN 2025\Documents\AcademicAdvisor-Chatbot-V3"

# Activate virtual environment
.\venv\Scripts\activate

# Ensure dependencies are installed
pip install -r requirements.txt
```

### 1. Validate Rasa Configuration

```bash
# Validate domain and training data
rasa data validate
```

### 2. Train Model

```bash
# Train the Rasa model
rasa train
```

### 3. Start Action Server (Terminal 1)

```bash
# Start the custom action server
rasa run actions --port 5055
```

### 4. Start Rasa Server (Terminal 2)

```bash
# Start the Rasa server with REST API
rasa run --enable-api --cors "*" --port 5005
```

### 5. Interactive Testing

```bash
# Test in shell mode
rasa shell

# Or with debug output
rasa shell --debug
```

### 6. REST API Testing

```bash
# Test via curl (PowerShell)
$body = @{ sender = "test_user"; message = "Tell me about CCS3101" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5005/webhooks/rest/webhook" -Method Post -Body $body -ContentType "application/json"
```

### 7. Unit Testing Custom Actions

```bash
# Create and run pytest tests
pytest tests/test_actions.py -v
```

---

## Test Data Requirements

### Sample Course Codes for Testing

| Course Code | Has Prerequisites | Notes |
|-------------|-------------------|-------|
| CCS3101 | Yes | Test with prerequisites |
| CSC4600 | Yes | Test with prerequisites |
| (Check DB for course without prereqs) | No | Test "no prerequisites" case |
| INVALID999 | N/A | Test "not found" case |

### Database Verification

```sql
-- Verify courses exist
SELECT COUNT(*) FROM courses;

-- Verify prerequisites exist
SELECT COUNT(*) FROM prerequisites;

-- Find course without prerequisites for testing
SELECT c.course_code 
FROM courses c 
LEFT JOIN prerequisites p ON c.course_code = p.course_code 
WHERE p.course_code IS NULL 
LIMIT 1;
```

---

## Acceptance Criteria

| Category | Pass Criteria |
|----------|---------------|
| Unit Tests | 100% pass rate |
| Integration Tests | 95% pass rate |
| E2E Tests | 90% pass rate |
| Performance | All within thresholds |
| Security | No critical vulnerabilities |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| OpenAI API rate limits | Medium | Medium | Implement caching, fallback responses |
| Database corruption | Low | High | Regular backups, validation |
| LLM hallucination | Medium | Medium | Context grounding, validation prompts |
| Telegram webhook failures | Medium | Low | Retry logic, monitoring |

---

## Test Environment Setup

```
┌─────────────────────────────────────────────────────────┐
│                   Test Environment                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Rasa      │    │   Action    │    │   SQLite    │  │
│  │   Server    │◄──►│   Server    │◄──►│   Database  │  │
│  │  :5005      │    │   :5055     │    │             │  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                                                │
│         ▼                                                │
│  ┌─────────────┐    ┌─────────────┐                      │
│  │   REST      │    │   Telegram  │                      │
│  │   Client    │    │   (Manual)  │                      │
│  └─────────────┘    └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

---

## Manual Test Scenarios

### Scenario 1: Complete Course Inquiry Flow

1. Start conversation: "Hello"
2. Ask for course info: "Tell me about CCS3101"
3. Verify response contains: course name, credits, synopsis, prerequisites
4. Ask follow-up: "What about CSC4600?"
5. End conversation: "Thank you, goodbye"

### Scenario 2: Prerequisite Check Flow

1. Start: "Hi, I need help"
2. Ask: "What are the prerequisites for CSC4600?"
3. Verify: Response lists prerequisite courses
4. Try invalid: "Prerequisites for FAKECOURSE"
5. Verify: Error message shown

### Scenario 3: Help and Navigation

1. Start: "Hello"
2. Ask: "What can you help me with?"
3. Verify: Help menu displayed
4. Try: "How do I drop a course?"
5. Verify: Relevant information provided

---

## Appendix: File Structure Reference

```
AcademicAdvisor-Chatbot-V3/
├── actions/
│   └── actions.py          # Custom actions (3 actions)
├── config.yml              # Rasa CALM config
├── credentials.yml         # Channel credentials
├── endpoints.yml           # Action server endpoint
├── db/
│   ├── academic.db         # Course data
│   └── tracker.db          # Conversation history
├── domain/
│   ├── academic/           # Academic domain files
│   ├── admin/              # Admin domain files
│   ├── general/            # General conversation
│   ├── policies/           # Policy information
│   └── system/             # System domain
└── data/
    ├── academic/           # Academic training data
    ├── admin/              # Admin training data
    ├── general/            # General training data
    └── policies/           # Policy training data
```
