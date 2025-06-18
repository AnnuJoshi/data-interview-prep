def find_uncommon(l1, l2):
    """
    Find elements that are unique to either list using brute force method.

    Args:
        l1 (list): First input list
        l2 (list): Second input list

    Returns:
        list: Elements that appear in only one of the lists
    """
    if not isinstance(l1, list) or not isinstance(l2, list):
        raise TypeError("Inputs must be lists")

    uncommon = []

    # Find elements in l1 that are not in l2
    for i in l1:
        if i not in l2:
            uncommon.append(i)

    # Find elements in l2 that are not in l1
    for i in l2:
        if i not in l1:
            uncommon.append(i)

    return uncommon

def format_employee_skills(employees):
    """
    Input: {'John': ['Python', 'SQL'], 'Alice': ['Java', 'C++', 'Python']}
    Output: ['John -> Python, SQL', 'Alice -> Java, C++, Python']
    """
    return [f"{name} -> {', '.join(skills)}" for name, skills in employees.items()]

# Test cases
employees = {
    'John': ['Python', 'SQL'],
    'Alice': ['Java', 'C++', 'Python'],
    'Bob': ['JavaScript']
}
# print(format_employee_skills(employees))


def format_inventory(inventory):
    """
    Input: {'apple': {'price': 0.5, 'quantity': 10}, 'banana': {'price': 0.3, 'quantity': 20}}
    Output: ['apple: 10 units at \$0.50 = \$5.00', 'banana: 20 units at \$0.30 = \$6.00']
    """
    result = []
    for item, details in inventory.items():
        price = details['price']
        quantity = details['quantity']
        total = price * quantity
        result.append(f"{item}: {quantity} units at ${price:.2f} = ${total:.2f}")
    return result

# Test cases
inventory = {
    'apple': {'price': 0.5, 'quantity': 10},
    'banana': {'price': 0.3, 'quantity': 20},
    'orange': {'price': 0.6, 'quantity': 15}
}
# print(format_inventory(inventory))


def generate_grade_report(grades):
    """
    Input: {
        'John': {'Math': [90, 85], 'Science': [88, 87]},
        'Alice': {'Math': [92, 94], 'Science': [85, 86]}
    }
    Output: ['John | Math: 87.5, Science: 87.5 | Overall: 87.5',
             'Alice | Math: 93.0, Science: 85.5 | Overall: 89.25']
    """
    report = []
    for student, subjects in grades.items():
        # Calculate average for each subject
        subject_averages = {
            subject: sum(scores)/len(scores)
            for subject, scores in subjects.items()
        }

        # Format subject averages
        subject_str = ', '.join(
            f"{subject}: {avg:.1f}"
            for subject, avg in subject_averages.items()
        )

        # Calculate overall average
        overall_avg = sum(subject_averages.values()) / len(subject_averages)

        # Create report line
        report.append(f"{student} | {subject_str} | Overall: {overall_avg:.2f}")

    return report

# Test cases
grades = {
    'John': {'Math': [90, 85], 'Science': [88, 87]},
    'Alice': {'Math': [92, 94], 'Science': [85, 86]},
    'Bob': {'Math': [78, 82], 'Science': [90, 93]}
}
# print(generate_grade_report(grades))

def format_order_summary(orders):
    """
    Input: {
        'Table1': {
            'Starters': {'Soup': 5.99, 'Salad': 4.99},
            'Main': {'Steak': 25.99},
            'Drinks': {'Wine': 8.99, 'Water': 1.99}
        }
    }
    Output: ['Table1:', '  Starters: Soup (\$5.99), Salad (\$4.99)',
             '  Main: Steak (\$25.99)', '  Drinks: Wine (\$8.99), Water (\$1.99)',
             '  Total: \$47.95']
    """
    summary = []
    for table, categories in orders.items():
        summary.append(f"{table}:")
        total = 0

        for category, items in categories.items():
            # Format items in category
            items_str = ', '.join(f"{item} (${price:.2f})"
                                for item, price in items.items())
            summary.append(f"  {category}: {items_str}")

            # Add to total
            total += sum(items.values())

        summary.append(f"  Total: ${total:.2f}")

    return summary

# Test cases
orders = {
    'Table1': {
        'Starters': {'Soup': 5.99, 'Salad': 4.99},
        'Main': {'Steak': 25.99},
        'Drinks': {'Wine': 8.99, 'Water': 1.99}
    },
    'Table2': {
        'Main': {'Pasta': 15.99, 'Fish': 22.99},
        'Drinks': {'Soda': 2.99}
    }
}
# print(format_order_summary(orders))

dictionary = {"hi":["annu"], 1:["234","787"], 3: "ubgjh"}
print(list(dictionary.values())) # type is <class 'dict_values'> 
lists = list(dictionary.values())
print((lists[0]+lists[1])) # list concatenation 

result1 = [item  for sublist in dictionary.values() if isinstance(sublist, list) for item in sublist ]
# checkout this format 
result2 = [sublist  for sublist in dictionary.values() if isinstance(sublist, list)  ]
print(f"result1 {result1}")
print(f"result2 {result2}")

def most_common_city(locations):
    """
    Find the most frequently occurring city across all locations.

    Args:
        locations (dict): Dictionary with locations as keys and lists of cities as values

    Returns:
        str: Name of the most common city
    """
    # Error 1: map is a built-in function, better use city_count
    city_count = {}

    # Loop through the locations dictionary
    for cities in locations.values():
        for city in cities:
            # Error 2: dict uses [] not add() method
            # Error 3: Better to use get() method for cleaner code
            city_count[city] = city_count.get(city, 0) + 1

    # Error 4: Initialize with None for empty dictionary case
    max_count = 0
    max_count_city = None

    # Find city with maximum count
    for city, count in city_count.items():
        if count > max_count:
            max_count = count
            max_count_city = city

    # Error 5: Return max_count_city, not city
    return max_count_city

def reverse_sort_numbers(s1):
    """
    Sort a string of numbers in descending order

    Args:
        s1 (str): String of numbers

    Returns:
        str: Sorted string in descending order
    """
    # Convert to list and sort in reverse
    num = list(s1)
    num.sort(reverse=True) # Remem
    # Join back to string
    return ''.join(num) # remem

def reverse_sort_numbers(s1):
    return ''.join(sorted(s1, reverse=True))

def calculate_average_price(prices):
    if not isinstance(prices, (list, tuple)):
        raise TypeError("Input must be a list or tuple")

    if not prices:
        return 0

    try:
        return round(sum(prices) / len(prices), 2)
    except (TypeError, ValueError):
        raise ValueError("All prices must be numbers")
    

def max_unique_books(prices, budget):
    # Edge case handling
    if not prices or budget <= 0:
        return 0

    # Sort prices in ascending order to maximize books
    sorted_prices = sorted(prices)
    book_count = 0
    total_cost = 0

    # Iterate through sorted prices
    for price in sorted_prices:
        if total_cost + price <= budget:
            total_cost += price
            book_count += 1
        else:
            break

    return book_count

def find_sequels(titles):
    sequels = []

    for title in titles:
        # Check if any other title contains this title as a prefix
        for other_title in titles:
            if other_title != title and other_title.startswith(title):
                sequels.append(other_title)

    return list(set(sequels))

#How would you optimize the sequel detection for large datasets?


