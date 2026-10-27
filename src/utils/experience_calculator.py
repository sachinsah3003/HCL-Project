import re
from datetime import date, datetime
from typing import Optional, Dict, Any, List, Tuple


def _parse_date_range(
    start_date: Optional[str],
    end_date: Optional[str],
) -> Optional[Tuple[int, int, bool]]:
    """Return inclusive start/end month indexes and an estimate flag."""

    if not start_date or not end_date:
        return None

        
    
    def parse(value, is_end=False):
        if not value:
            return None

        value = value.strip()
        normalized = re.sub(r"\s+", " ", value)

        if normalized.lower() in ("present", "current", "ongoing", "now"):
            today = date.today()
            return today.year * 12 + today.month - 1, True

        # Month/year formats: 2026-06, 06/2026, 06-2026
        month_year_patterns = [
            (r"^(\d{4})-(\d{1,2})$", "ym"),
            (r"^(\d{1,2})/(\d{4})$", "my"),
            (r"^(\d{1,2})-(\d{4})$", "my"),
        ]

        for pattern, format_type in month_year_patterns:
            match = re.fullmatch(pattern, normalized)
            if match:
                if format_type == "ym":
                    year, month = int(match.group(1)), int(match.group(2))
                else:
                    month, year = int(match.group(1)), int(match.group(2))

                if not 1 <= month <= 12:
                    return None

                return year * 12 + month - 1, False

        # Month names: Jun 2026, June 2026
        for fmt in ("%b %Y", "%B %Y"):
            try:
                parsed = datetime.strptime(normalized, fmt)
                return parsed.year * 12 + parsed.month - 1, False
            except ValueError:
                pass

        # ISO dates: 2026-06-01
        try:
            parsed = datetime.strptime(normalized, "%Y-%m-%d")
            return parsed.year * 12 + parsed.month - 1, False
        except ValueError:
            pass

        # Year-only dates: 2026
        if re.fullmatch(r"\d{4}", normalized):
            year = int(normalized)
            month = 11 if is_end else 0
            return year * 12 + month, True

        # Unsupported or ambiguous formats must not be guessed.
        return None



    start = parse(start_date)
    end = parse(end_date, is_end=True)

    if start is None or end is None:
        return None

    start_month, start_estimated = start
    end_month, end_estimated = end

    if end_month < start_month:
        return None

    return (
        start_month,
        end_month,
        start_estimated or end_estimated,
    )


def calculate_total_experience(
    work_experience: List[Any],
) -> Dict[str, Any]:
    """Calculate the union of dated employment periods."""

    intervals = []
    has_estimated_dates = False

    for job in work_experience:
        start_date = job.start_date
        end_date = job.end_date

        parsed = _parse_date_range(start_date, end_date)

        if parsed is None:
            continue

        start, end, date_estimated = parsed

        # Exclude explicit roles identified as unpaid or unrelated
        # only if your application defines such a policy separately.
        intervals.append((start, end))
        has_estimated_dates = (
            has_estimated_dates
            or date_estimated
            or job.dates_are_estimated
        )

    if not intervals:
        return {
            "total_experience_years": None,
            "experience_estimated": False,
            "dated_roles_count": 0,
        }

    intervals.sort()
    merged = []
    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:
        if start <= current_end + 1:
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end

    merged.append((current_start, current_end))

    total_months = sum(
        end - start + 1
        for start, end in merged
    )

    return {
        "total_experience_years": round(total_months / 12.0, 2),
        "experience_estimated": has_estimated_dates,
        "dated_roles_count": len(intervals),
    }
