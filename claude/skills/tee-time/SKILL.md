---
name: slc-golf-tee-times
description: Check available tee times at Salt Lake City area golf courses including municipal courses (Bonneville, Glendale, Rose Park, Forest Dale, Nibley Park, Mountain Dell) and other public courses (River Oaks, South Mountain, Bountiful Ridge, Old Mill, Meadow Brook, Riverbend, Wing Pointe). Use when the user asks about golf tee times, available slots, or course availability in the SLC area.
allowed-tools: WebFetch
---
# SLC Area Golf Tee Times
This skill queries the Chronogolf API to find available tee times at Salt Lake City area golf courses.
## Known Courses & IDs
| Club | Course | UUID | Holes | Booking URL (date is dynamic) |
|------|--------|------|-------|-------------------------------|
| **Bonneville** | Bonneville (main) | `bc27ab7a-6218-4b61-9aa8-0838f7c44ce3` | 9/18 | `https://www.chronogolf.com/club/bonneville-golf-course?date=YYYY-MM-DD` |
| **Bonneville** | Bonneville 10th Tee | `caa8142a-4a42-482b-8d35-4239ce26f7b0` | 9 | `https://www.chronogolf.com/club/bonneville-golf-course?date=YYYY-MM-DD` |
| **Glendale** | Glendale (9 or 18) | `547936f8-0f45-4bea-b557-d15a4de485ad` | 9/18 | `https://www.chronogolf.com/club/glendale-golf-course?date=YYYY-MM-DD` |
| **Glendale** | Glendale Back 9 (10th Tee) | `4984e272-06a5-446a-8e24-8402e3591b7c` | 9 | `https://www.chronogolf.com/club/glendale-golf-course?date=YYYY-MM-DD` |
| **Rose Park** | Rose Park GC | `19a5558e-3821-4935-b6bd-0cbc99693d91` | 9/18 | `https://www.chronogolf.com/club/rose-park-golf-course?date=YYYY-MM-DD` |
| **Rose Park** | Rose Park Back 9 | `f899015b-2109-4028-8640-d670ada581e4` | 9 | `https://www.chronogolf.com/club/rose-park-golf-course?date=YYYY-MM-DD` |
| **Forest Dale** | Forest Dale | `41ea25ca-ffcb-4f14-a86d-de0ef84510e0` | 9 | `https://www.chronogolf.com/club/forest-dale-golf-course?date=YYYY-MM-DD` |
| **Nibley Park** | Nibley Park | `997cd01f-4ce8-4462-a459-594762efb606` | 9 | `https://www.chronogolf.com/club/nibley-park-golf-course?date=YYYY-MM-DD` |
| **Mountain Dell** | Canyon Course | `bd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e` | 9/18 | `https://www.chronogolf.com/club/mountain-dell-golf-club?date=YYYY-MM-DD` |
| **Mountain Dell** | Lake Course | `2c162b65-6803-4bad-9a21-4c1ca88bb242` | 9/18 | `https://www.chronogolf.com/club/mountain-dell-golf-club?date=YYYY-MM-DD` |
| **Mountain Dell** | Lake Back 9 | `77dca1a2-edae-47d2-a202-a1e9391cc305` | 9 | `https://www.chronogolf.com/club/mountain-dell-golf-club?date=YYYY-MM-DD` |
| **River Oaks** | River Oaks Golf Course | `026599af-6569-4b0f-aaf9-aefedc607e3c` | 18 | `https://www.chronogolf.com/club/river-oaks-golf-course-utah?date=YYYY-MM-DD` |
| **River Oaks** | River Oaks Opposite 9 | `79c03256-be52-4e3d-aba8-9c64df6e12b2` | 9 | `https://www.chronogolf.com/club/river-oaks-golf-course-utah?date=YYYY-MM-DD` |
| **Bountiful Ridge** | Bountiful Ridge | `48078d3b-6ec6-488f-9662-84f10cf80e7c` | 18 | `https://www.chronogolf.com/club/bountiful-ridge-golf-course?date=YYYY-MM-DD` |
| **Wing Pointe** | Wing Pointe | `73196cef-df15-416c-b70d-842079b3adb2` | 18 | `https://www.chronogolf.com/club/wing-pointe-golf-course?date=YYYY-MM-DD` |
### Booking URL Format
Chronogolf booking links use the club slug and date — individual tee time slots are selected client-side after the page loads. There is no deep-link URL per tee time slot.
```
https://www.chronogolf.com/club/<slug>?date=YYYY-MM-DD
```
**Always include this link when displaying tee times**, grouped by club, with the actual date substituted in.
### Club-level IDs (for reference)
| Club | Slug | Club UUID | Club ID |
|------|------|-----------|---------|
| Bonneville | `bonneville-golf-course` | `92260e9d-a76a-4dc3-9caa-147be81b97f5` | 14158 |
| Glendale | `glendale-golf-course` | `d2b39c47-3d5b-4955-9709-685061c7dbfa` | 14185 |
| Rose Park | `rose-park-golf-course` | `bbd94e88-ca9f-4dda-97bb-60c469949b08` | 14222 |
| Forest Dale | `forest-dale-golf-course` | `011bf6d7-60ef-489c-851e-3eefea9f06a0` | 14180 |
| Nibley Park | `nibley-park-golf-course` | `2c86e33d-eb5d-4828-9dc5-6f395975d476` | 14207 |
| Mountain Dell | `mountain-dell-golf-club` | `51013801-2e79-47eb-b0f9-49da4212e876` | 14203 |
| River Oaks | `river-oaks-golf-course-utah` | `914ff5cc-8d63-4c19-b184-72e20fcb8039` | 18885 |
| South Mountain | `south-mountain-slco` | `3e15af92-a962-4bf2-8b42-0535f62cce74` | 14235 |
| Bountiful Ridge | `bountiful-ridge-golf-course` | `c1fb64d3-c23b-4dbd-8230-c16e6e1e80da` | 14159 |
| Old Mill | `old-mill-slco` | `99cc98d7-03aa-400c-a8b6-c5e5f3665ca4` | 14210 |
| Meadow Brook | `meadow-brook-slco` | `566ced7b-bc15-494f-94f2-cc2f162c8162` | 14198 |
| Riverbend | `riverbend-slco` | `d7cbb808-fc97-4a34-a33f-6f11d1c736f8` | 14219 |
| Wing Pointe | `wing-pointe-golf-course` | `37a853f1-1454-4ea7-a791-7b84c9fb301e` | 14262 |
---
## Tee Time API
### Endpoint
```
GET https://www.chronogolf.com/marketplace/v2/teetimes
```
### Key Parameters
| Parameter | Example | Notes |
|-----------|---------|-------|
| `start_date` | `2026-02-27` | Date in YYYY-MM-DD format |
| `course_ids` | `uuid1%2Cuuid2` | Comma-separated (URL-encoded) course UUIDs |
| `holes` | `9%2C18` | Filter by holes: `9`, `18`, or both |
| `start_time` | `00%3A00` | Earliest tee time (HH:MM, URL-encoded) |
| `page` | `1` | Page number — each page holds ~24 results |
### Pagination
The API returns ~24 slots per page. When querying all courses together, paginate until you receive an empty `teetimes` array or a `"sold_out"` status. Typically 2 pages covers a full day across all SLC courses.
### Displaying Results
Always display tee times grouped by club with:
- A clickable booking link for the club (substituting the actual date): `[Book at Bonneville](https://www.chronogolf.com/club/bonneville-golf-course?date=2026-03-01)`
- A table per club with columns: **Time | Holes | Spots | Price**
- **Holes**: show what can be booked — `9`, `18`, or `9/18` (from the API's `bookable_holes` or `holes` field)
- **Spots**: number of available spots from `available_spots` — never show the internal tee time ID
- **Price**: from `green_fee_price_range.min` (divide by 100, cents → dollars)
### Sample Full URL (all SLC area courses with course UUIDs, all day)
```
https://www.chronogolf.com/marketplace/v2/teetimes?start_date=2026-02-27&course_ids=bc27ab7a-6218-4b61-9aa8-0838f7c44ce3%2Ccaa8142a-4a42-482b-8d35-4239ce26f7b0%2C547936f8-0f45-4bea-b557-d15a4de485ad%2C4984e272-06a5-446a-8e24-8402e3591b7c%2C19a5558e-3821-4935-b6bd-0cbc99693d91%2Cf899015b-2109-4028-8640-d670ada581e4%2C41ea25ca-ffcb-4f14-a86d-de0ef84510e0%2C997cd01f-4ce8-4462-a459-594762efb606%2Cbd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e%2C2c162b65-6803-4bad-9a21-4c1ca88bb242%2C77dca1a2-edae-47d2-a202-a1e9391cc305%2C026599af-6569-4b0f-aaf9-aefedc607e3c%2C79c03256-be52-4e3d-aba8-9c64df6e12b2%2C48078d3b-6ec6-488f-9662-84f10cf80e7c%2C73196cef-df15-416c-b70d-842079b3adb2&holes=9%2C18&start_time=00%3A00&page=1
```

**Note:** Some courses (South Mountain, Old Mill, Meadow Brook, Riverbend) only have club UUIDs without separate course UUIDs. These courses are often seasonal or have online booking disabled. They can be queried using the `club_uuids` parameter instead of `course_ids` when they're operational.
---
## Sample Python Script
```python
import httpx
from datetime import date
COURSE_IDS = [
    # Bonneville
    "bc27ab7a-6218-4b61-9aa8-0838f7c44ce3",  # Bonneville 18h
    "caa8142a-4a42-482b-8d35-4239ce26f7b0",  # Bonneville 10th Tee
    # Glendale
    "547936f8-0f45-4bea-b557-d15a4de485ad",  # Glendale 9/18h
    "4984e272-06a5-446a-8e24-8402e3591b7c",  # Glendale Back 9
    # Rose Park
    "19a5558e-3821-4935-b6bd-0cbc99693d91",  # Rose Park GC
    "f899015b-2109-4028-8640-d670ada581e4",  # Rose Park Back 9
    # Forest Dale
    "41ea25ca-ffcb-4f14-a86d-de0ef84510e0",  # Forest Dale
    # Nibley Park
    "997cd01f-4ce8-4462-a459-594762efb606",  # Nibley Park
    # Mountain Dell
    "bd6e3c42-7ae5-4d97-b6d0-60ebf9957a7e",  # Canyon Course
    "2c162b65-6803-4bad-9a21-4c1ca88bb242",  # Lake Course
    "77dca1a2-edae-47d2-a202-a1e9391cc305",  # Lake Back 9
    # River Oaks
    "026599af-6569-4b0f-aaf9-aefedc607e3c",  # River Oaks 18h
    "79c03256-be52-4e3d-aba8-9c64df6e12b2",  # River Oaks Opposite 9
    # Bountiful Ridge
    "48078d3b-6ec6-488f-9662-84f10cf80e7c",  # Bountiful Ridge 18h
    # Wing Pointe
    "73196cef-df15-416c-b70d-842079b3adb2",  # Wing Pointe 18h
]
def fetch_tee_times(target_date: date, start_time: str = "00:00") -> list[dict]:
    """Fetch all available tee times across SLC municipal courses for a given date."""
    base_url = "https://www.chronogolf.com/marketplace/v2/teetimes"
    params = {
        "start_date": target_date.isoformat(),
        "course_ids": ",".join(COURSE_IDS),
        "holes": "9,18",
        "start_time": start_time,
    }
    headers = {"Accept": "application/json"}
    all_teetimes = []
    page = 1
    while True:
        params["page"] = page
        response = httpx.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        teetimes = data.get("teetimes", [])
        if not teetimes:
            break
        for slot in teetimes:
            all_teetimes.append({
                "course": slot["course"]["name"],
                "time": slot["date"],        # ISO datetime string
                "holes": slot["holes"],
                "spots": slot["available_spots"],
                "price": slot["green_fee_price_range"]["min"] / 100,  # cents -> dollars
            })
        page += 1
    return all_teetimes

if __name__ == "__main__":
    teetimes = fetch_tee_times(date.today())
    for t in teetimes:
        print(f"{t['time'][11:16]}  {t['course']:<35} {t['holes']}h  {t['spots']} spots  ${t['price']:.2f}")
```
---
## How to Add a New Course
When asked to add a new course or find a course that isn't listed above:
### 1. Find the Chronogolf club slug
The slug is the URL path component on `chronogolf.com/club/<slug>`. Try common patterns:
- `<course-name>-golf-course`
- `<course-name>-golf-club`
- `<course-name>`
### 2. Fetch the club page to extract IDs
Use WebFetch on `https://www.chronogolf.com/club/<slug>` with this prompt:
> "Find all course UUIDs (GUIDs like xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx), club UUIDs, numeric course IDs, and club IDs embedded in the page HTML or JSON data."
The page embeds a JSON blob containing all course UUIDs, club UUIDs, and numeric IDs.
### 3. Update this skill file
Edit this file (`~/.claude/skills/slc-golf-tee-times/SKILL.md`) to add the new course to:
- The **Known Courses & IDs** table — including the booking URL (`https://www.chronogolf.com/club/<slug>?date=YYYY-MM-DD`)
- The **Club-level IDs** table
- The `COURSE_IDS` list in the Python script
- The full sample URL's `course_ids` parameter
This keeps the skill self-contained and up to date for future queries.

---

## Course Status Notes

### Seasonal Courses
Many Utah golf courses are **seasonal** and close for winter (typically November-March). Courses will show `"status": "closed"` in the API when not operational.

### Courses with Booking Restrictions
- **South Mountain** (`south-mountain-slco`): Online booking unavailable until Spring 2026
- **Meadow Brook** (`meadow-brook-slco`): Online booking disabled; PGA Passbook holders must call for reservations
- **Old Mill** (`old-mill-slco`): May be seasonal
- **Riverbend** (`riverbend-slco`): May be seasonal
- **Bountiful Ridge** (`bountiful-ridge-golf-course`): Inactive for online booking
- **Wing Pointe** (`wing-pointe-golf-course`): May be permanently closed (verify with course directly)

### Currently Operational (Feb 2026)
- **River Oaks** - Sandy (both 18-hole and 9-hole Opposite courses operational)
- **All SLC Municipal courses** - Bonneville, Glendale, Rose Park, Forest Dale, Nibley Park, Mountain Dell
