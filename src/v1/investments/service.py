import parsedatetime
import datetime


cal = parsedatetime.Calendar()
date_string = "dd"
# Parse a human-readable time string
time_struct, parse_status = cal.parse(date_string)
# Convert to just date
parsed_date = datetime.date(*time_struct[:3])
# plan_details["duration"] = parsed_date


def calculate_roi(plans):
    time_units = {"days": 365, "weeks": 52, "months": 12, "years": 1}  # Conversion to yearly factor
    results = []

    for plan in plans:
        name, cost, roi_percent, duration, unit = plan
        roi_decimal = roi_percent / 100

        # Calculate total return dynamically (capital + profit)
        total_return = cost + (cost * roi_decimal)

        # Convert duration to years
        if unit not in time_units:
            raise ValueError(f"Invalid time unit: {unit}. Use 'days', 'weeks', 'months', or 'years'.")
        duration_in_years = duration / time_units[unit]

        # Calculate annualized ROI
        annualized_roi = ((1 + roi_decimal) ** (1 / duration_in_years) - 1) * 100  

        results.append({
            "Plan": name,
            "Capital ($)": cost,
            "ROI (%)": roi_percent,
            "Duration": f"{duration} {unit}",
            "Total Return ($)": round(total_return, 2),
            "Annualized ROI (%)": round(annualized_roi, 2)
        })
    
    # Sort by Annualized ROI in descending order
    results = sorted(results, key=lambda x: x["Annualized ROI (%)"], reverse=True)

    return results


# Example plans: (name, cost, ROI %, duration, unit)
plans = [
    ("Plan A", 1000, 50, 3, "weeks"),
    ("Plan B", 2000, 75, 1, "months"),
    ("Plan C", 5000, 140, 6, "months"),
    ("Plan D", 7000, 185.71, 2, "years"),
]

# Run the function
roi_results = calculate_roi(plans)

# Print the results
for res in roi_results:
    print(res)





