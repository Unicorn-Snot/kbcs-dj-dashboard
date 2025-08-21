def yearly_rainfall():
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    rainfall = []

    # Input rainfall for each month
    for month in months:
        amount = float(input(f"Enter rainfall for {month} (in inches): "))
        rainfall.append(amount)

    # Calculations
    total_rainfall = sum(rainfall)
    average_rainfall = total_rainfall / len(rainfall)
    max_rain = max(rainfall)
    min_rain = min(rainfall)
    max_month = months[rainfall.index(max_rain)]
    min_month = months[rainfall.index(min_rain)]

    # Output
    print("\nRainfall Report")
    print(f"Total rainfall: {total_rainfall:.2f} inches")
    print(f"Average monthly rainfall: {average_rainfall:.2f} inches")
    print(f"Highest rainfall: {max_rain:.2f} inches in {max_month}")
    print(f"Lowest rainfall: {min_rain:.2f} inches in {min_month}")

# Call the function
yearly_rainfall()
