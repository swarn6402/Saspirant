from __future__ import annotations

import logging
import re
from datetime import date, datetime
from typing import Any


class MatchingService:
    """
    Determine whether a job notification matches user preferences.

    Example:
        matcher = MatchingService()
        if matcher.is_match(job_notification, user_prefs, user.date_of_birth):
            # Send alert to user
            pass
    """

    QUALIFICATION_RANK = {
        "10th": 1,
        "12th": 2,
        "graduate": 3,
        "post-graduate": 4,
        "doctorate": 5,
    }

    INDIA_LOCATIONS = {
        "all india",
        "andhra pradesh",
        "arunachal pradesh",
        "assam",
        "bihar",
        "chhattisgarh",
        "goa",
        "gujarat",
        "haryana",
        "himachal pradesh",
        "jharkhand",
        "karnataka",
        "kerala",
        "madhya pradesh",
        "maharashtra",
        "manipur",
        "meghalaya",
        "mizoram",
        "nagaland",
        "odisha",
        "punjab",
        "rajasthan",
        "sikkim",
        "tamil nadu",
        "telangana",
        "tripura",
        "uttar pradesh",
        "uttarakhand",
        "west bengal",
        "delhi",
        "jammu and kashmir",
        "ladakh",
        "andaman and nicobar",
        "chandigarh",
        "dadra and nagar haveli",
        "daman and diu",
        "lakshadweep",
        "puducherry",
    }

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def is_match(
        self,
        job_notification: Any,
        user_preferences: Any,
        user_dob: date | datetime,
        user_qualification: str | None = None,
    ) -> bool:
        """
        Check whether a job notification matches user preferences and eligibility.

        Args:
            job_notification: JobNotification-like object.
            user_preferences: UserPreference object or list of UserPreference objects.
            user_dob: User date of birth.
            user_qualification: Optional user qualification; if omitted, tries to read from
                preferences or defaults to "10th".

        Returns:
            True if job should be alerted to the user, False otherwise.
        """
        prefs = self._normalize_preferences(user_preferences)
        print("\n=== MATCHING DEBUG ===")
        print(f"Job: {getattr(job_notification, 'job_title', 'Unknown')}")
        print(f"Job Category: {getattr(job_notification, 'exam_category', None)}")

        if not prefs:
            print("[X] FAILED: no user preferences available")
            self.logger.info("Match failed: no user preferences available.")
            print("======================\n")
            return False

        user_categories = [getattr(p, "exam_category", None) for p in prefs]
        print(f"User Categories: {user_categories}")

        # 1) Category check
        job_category = (getattr(job_notification, "exam_category", "") or "").strip()
        category_match = any((c or "").strip().lower() == job_category.lower() for c in user_categories)
        print(f"Category Match: {category_match}")
        if not category_match:
            print(f"[X] FAILED: Category '{job_category}' not in {user_categories}")
            self.logger.info(
                "Category mismatch: job_category=%s, preferred_categories=%s",
                job_category or "not specified",
                sorted({(c or '').strip().lower() for c in user_categories if c}),
            )
            print("======================\n")
            return False

        # 2) Age check
        age = self.calculate_age(user_dob)
        print(f"User Age: {age}")
        print(f"Job Age Limit: {getattr(job_notification, 'age_limit', None)}")
        if age is None:
            print("[X] FAILED: invalid user DOB")
            self.logger.info("Match failed: invalid user DOB.")
            print("======================\n")
            return False

        age_limit_raw = getattr(job_notification, "age_limit", None)
        if age_limit_raw:
            parsed = self.parse_age_limit(age_limit_raw)
            print(f"Parsed Age Limits: {parsed}")
            if parsed:
                min_age = parsed.get("min", 0)
                max_age = parsed.get("max", 999)
                age_eligible = min_age <= age <= max_age
                print(f"Age Check: {min_age} <= {age} <= {max_age} = {age_eligible}")
                if not age_eligible:
                    print(f"[X] FAILED: Age {age} not in range {min_age}-{max_age}")
                    self.logger.info("Age mismatch: user=%s, range=%s-%s", age, min_age, max_age)
                    print("======================\n")
                    return False
            else:
                print("[!] Could not parse age limit, assuming eligible")
        else:
            print("[!] No age limit specified, assuming eligible")

        pref_mins = [getattr(p, "min_age", None) for p in prefs if getattr(p, "min_age", None) is not None]
        pref_maxs = [getattr(p, "max_age", None) for p in prefs if getattr(p, "max_age", None) is not None]
        if pref_mins and age < min(pref_mins):
            print(f"[X] FAILED: user age {age} below preference min {min(pref_mins)}")
            self.logger.info("Preference age mismatch: user=%s, preference minimum=%s", age, min(pref_mins))
            print("======================\n")
            return False
        if pref_maxs and age > max(pref_maxs):
            print(f"[X] FAILED: user age {age} above preference max {max(pref_maxs)}")
            self.logger.info("Preference age mismatch: user=%s, preference maximum=%s", age, max(pref_maxs))
            print("======================\n")
            return False

        # 3) Qualification check
        required_qual = getattr(job_notification, "qualification_required", None) or "10th"
        print(f"Job Qualification: {required_qual}")

        effective_user_qual = user_qualification or self._get_user_qualification_from_prefs(prefs)
        if not effective_user_qual:
            print("[!] Cannot determine user qualification, assuming match baseline")
            effective_user_qual = required_qual
        print(f"User Qualification: {effective_user_qual}")

        qual_match = self.compare_qualifications(effective_user_qual, required_qual)
        print(f"Qualification Match: {qual_match}")
        if not qual_match:
            print(
                f"[X] FAILED: User qual '{effective_user_qual}' "
                f"doesn't meet required '{required_qual}'"
            )
            self.logger.info(
                "Qualification mismatch: user=%s, required=%s",
                effective_user_qual,
                required_qual,
            )
            print("======================\n")
            return False

        # 4) Location check
        location_ok = self._is_location_match(job_notification, prefs)
        print(f"Location Match: {location_ok}")
        if not location_ok:
            print("[X] FAILED: location mismatch")
            print("======================\n")
            return False

        print("[OK] MATCHED: All criteria passed!")
        print("======================\n")
        return True

    def parse_age_limit(self, age_limit_string: str | None) -> dict[str, int]:
        """
        Parse age text into min/max bounds.

        Input examples:
            "21-35 years", "Below 30 years", "Not exceeding 32 years"
        """
        if not age_limit_string:
            return {}

        text = age_limit_string.lower()
        parsed: dict[str, int] = {}

        range_match = re.search(r"(\d{1,2})\s*(?:-|to)\s*(\d{1,2})", text)
        if range_match:
            parsed["min"] = int(range_match.group(1))
            parsed["max"] = int(range_match.group(2))

        below_match = re.search(r"(?:below|under|not\s+exceeding|max(?:imum)?)\s*(\d{1,2})", text)
        if below_match:
            parsed["max"] = int(below_match.group(1))

        min_match = re.search(r"(?:minimum|min)\s*(\d{1,2})", text)
        if min_match:
            parsed["min"] = int(min_match.group(1))

        # If relaxation for categories is present, upper limit is more reliable.
        if any(token in text for token in ["sc", "st", "obc", "relax", "relaxation"]) and "max" in parsed:
            parsed.pop("min", None)

        return parsed

    def calculate_age(self, dob: date | datetime | str | None) -> int | None:
        """Calculate age in years from date of birth."""
        if dob is None:
            return None

        if isinstance(dob, str):
            try:
                dob = datetime.fromisoformat(dob).date()
            except ValueError:
                return None
        elif isinstance(dob, datetime):
            dob = dob.date()

        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def compare_qualifications(self, user_qual: str, required_qual: str | None) -> bool:
        """
        Return True if user qualification meets or exceeds required qualification.
        """
        user_rank = self._qualification_rank(user_qual or "10th")
        required_rank = self._qualification_rank(required_qual or "10th")
        return user_rank >= required_rank

    def extract_location_from_job(self, job_title: str | None, full_details: str | None) -> list[str]:
        """
        Extract location mentions from job title/details.

        Returns list of normalized locations; empty list means uncertain/ambiguous.
        """
        text = f"{job_title or ''} {full_details or ''}".lower()
        found = [loc for loc in self.INDIA_LOCATIONS if loc in text]

        if "all india" in text or "across india" in text or "pan india" in text:
            return ["all india"]
        return sorted(set(found))

    def _is_exam_category_match(self, job_notification: Any, prefs: list[Any]) -> bool:
        job_category = (getattr(job_notification, "exam_category", "") or "").strip().lower()
        preferred = {
            (getattr(pref, "exam_category", "") or "").strip().lower()
            for pref in prefs
            if getattr(pref, "exam_category", None)
        }
        if job_category and job_category in preferred:
            return True

        self.logger.info(
            "Category mismatch: job_category=%s, preferred_categories=%s",
            job_category or "not specified",
            sorted(preferred),
        )
        return False

    def _is_age_eligible(self, job_notification: Any, prefs: list[Any], age: int) -> bool:
        age_limit_raw = getattr(job_notification, "age_limit", None)
        parsed = self.parse_age_limit(age_limit_raw)

        if "min" in parsed and age < parsed["min"]:
            self.logger.info("Age mismatch: user=%s, job minimum=%s", age, parsed["min"])
            return False
        if "max" in parsed and age > parsed["max"]:
            self.logger.info("Age mismatch: user=%s, job maximum=%s", age, parsed["max"])
            return False

        pref_mins = [getattr(p, "min_age", None) for p in prefs if getattr(p, "min_age", None) is not None]
        pref_maxs = [getattr(p, "max_age", None) for p in prefs if getattr(p, "max_age", None) is not None]
        if pref_mins and age < min(pref_mins):
            self.logger.info("Preference age mismatch: user=%s, preference minimum=%s", age, min(pref_mins))
            return False
        if pref_maxs and age > max(pref_maxs):
            self.logger.info("Preference age mismatch: user=%s, preference maximum=%s", age, max(pref_maxs))
            return False

        # Missing age limit in notification implies eligible.
        return True

    def _is_location_match(self, job_notification: Any, prefs: list[Any]) -> bool:
        preferred_locations: list[str] = []
        for pref in prefs:
            locs = getattr(pref, "preferred_locations", None)
            if isinstance(locs, list):
                preferred_locations.extend([str(loc).strip().lower() for loc in locs if str(loc).strip()])

        preferred_unique = sorted(set(preferred_locations))
        if not preferred_unique:
            return True
        if "all india" in preferred_unique:
            return True

        job_locations = self.extract_location_from_job(
            getattr(job_notification, "job_title", None),
            getattr(job_notification, "full_details", None),
        )

        # Ambiguous location details in notification should not block a match.
        if not job_locations:
            return True
        if "all india" in [loc.lower() for loc in job_locations]:
            return True

        if any(job_loc.lower() in preferred_unique for job_loc in job_locations):
            return True

        self.logger.info(
            "Location mismatch: job_locations=%s, preferred_locations=%s",
            job_locations,
            preferred_unique,
        )
        return False

    def _normalize_preferences(self, user_preferences: Any) -> list[Any]:
        if user_preferences is None:
            return []
        if isinstance(user_preferences, list):
            return user_preferences
        if isinstance(user_preferences, tuple):
            return list(user_preferences)
        return [user_preferences]

    def _qualification_rank(self, qualification: str) -> int:
        text = (qualification or "").strip().lower()

        if "phd" in text or "doctorate" in text:
            return self.QUALIFICATION_RANK["doctorate"]
        if "post" in text and "graduate" in text:
            return self.QUALIFICATION_RANK["post-graduate"]
        if "master" in text:
            return self.QUALIFICATION_RANK["post-graduate"]
        if "graduate" in text or "degree" in text or "engineering" in text:
            return self.QUALIFICATION_RANK["graduate"]
        if "12" in text or "intermediate" in text or "higher secondary" in text:
            return self.QUALIFICATION_RANK["12th"]
        if "10" in text or "matric" in text or "secondary" in text:
            return self.QUALIFICATION_RANK["10th"]

        # Edge case: missing/unknown required qualification -> minimum eligibility.
        return self.QUALIFICATION_RANK["10th"]

    def _get_user_qualification_from_prefs(self, prefs: list[Any]) -> str | None:
        for pref in prefs:
            value = getattr(pref, "highest_qualification", None)
            if isinstance(value, str) and value.strip():
                return value.strip()
            user = getattr(pref, "user", None)
            user_value = getattr(user, "highest_qualification", None) if user is not None else None
            if isinstance(user_value, str) and user_value.strip():
                return user_value.strip()
        return None

