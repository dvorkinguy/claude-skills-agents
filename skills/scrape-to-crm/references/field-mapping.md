# Field Mapping Reference

## LinkedIn Profile → Attio People

| Apify Field (varies by actor) | Normalized Key | Attio Field | Attio Attribute |
|-------------------------------|---------------|-------------|-----------------|
| `fullName`, `name`, `firstName`+`lastName` | `full_name` | `name` | `full_name` |
| `email`, `emailAddress` | `email` | `email_addresses` | `email_address` |
| `phone`, `phoneNumber` | `phone` | `phone_numbers` | `original_phone_number` |
| `title`, `headline`, `position` | `title` | `job_title` | `value` |
| `linkedInUrl`, `profileUrl`, `url` | `linkedin_url` | `linkedin` | `value` |
| `location`, `geoLocation` | `location` | `location` | `value` |
| `companyName`, `company` | `company_name` | _(used for company linking)_ | — |
| `profileImage`, `avatar` | `avatar_url` | _(not pushed)_ | — |
| `connectionDegree` | `connection` | _(not pushed)_ | — |
| `summary`, `about` | `bio` | `description` | `value` |

## LinkedIn Company → Attio Companies

| Apify Field (varies by actor) | Normalized Key | Attio Field | Attio Attribute |
|-------------------------------|---------------|-------------|-----------------|
| `name`, `companyName` | `company_name` | `name` | `value` |
| `website`, `companyUrl` | `domain` | `domains` | `domain` |
| `industry` | `industry` | `categories` | `value` |
| `employeeCount`, `staffCount` | `employee_count` | `employee_range` | `value` |
| `description`, `about` | `description` | `description` | `value` |
| `linkedInUrl`, `url` | `linkedin_url` | `linkedin` | `value` |
| `headquarters`, `location` | `hq_location` | `primary_location` | `value` |
| `founded`, `foundedYear` | `founded_year` | `founded_date` | `value` |
| `specialties`, `tags` | `specialties` | _(not pushed)_ | — |
| `logo`, `logoUrl` | `logo_url` | _(not pushed)_ | — |

## Data Normalization Rules

### Phone Numbers (E.164)
1. Strip all non-digit characters
2. Israeli mobile (`05X...`, 10 digits) → replace `0` with `+972`
3. Israeli landline (`0X...`, 9-10 digits) → replace `0` with `+972`
4. Already has country code (`972...`) → prepend `+`
5. US numbers (10 digits, no prefix) → prepend `+1`
6. All others → prepend `+` if missing

### Email
- Lowercase, trim whitespace
- Skip if invalid (no `@` or no `.` after `@`)

### LinkedIn URLs
- Normalize to `https://www.linkedin.com/in/<slug>/` (profiles)
- Normalize to `https://www.linkedin.com/company/<slug>/` (companies)
- Strip query parameters and trailing fragments

### Names
- Trim whitespace
- If only `firstName`/`lastName` available, join with single space
- Skip honorifics (Dr., Mr., Mrs.) — Attio handles display

### Location
- Pass as-is; Attio normalizes locations internally
- For Israeli locations, prefer English transliteration (e.g., "Tel Aviv" not "תל אביב")
