#!/usr/bin/env python3
import requests
import json

# Test data for employee calculation
test_data = {
    "employment_type": "employee",
    "gross_salary": 15000,
    "age": 30,
    "children": 2,
    "spouse": True,
    "spouse_income": 0,
    "disabled": False,
    "new_immigrant": False,
    "student": False,
    "reserve_duty": False,
    "pension_rate": 6
}

def test_api():
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print("Health check:", response.json())
    except Exception as e:
        print("Server not running. Start with: python start_server.py")
        return
    
    # Test calculation endpoint
    try:
        response = requests.post(
            f"{base_url}/api/v1/calculator/calculate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\nCalculation Result:")
            print(f"Gross Salary: ₪{result['gross_salary']:,.2f}")
            print(f"Net Salary: ₪{result['net_salary']:,.2f}")
            print(f"Credit Points: {result['credit_points']}")
            print(f"Effective Tax Rate: {result['effective_tax_rate']:.2f}%")
            print("\nTax Breakdown:")
            breakdown = result['tax_breakdown']
            print(f"  Income Tax: ₪{breakdown['income_tax']:,.2f}")
            print(f"  National Insurance: ₪{breakdown['national_insurance']:,.2f}")
            print(f"  Health Tax: ₪{breakdown['health_tax']:,.2f}")
            print(f"  Pension: ₪{breakdown['pension_employee']:,.2f}")
            print(f"  Total Deductions: ₪{breakdown['total_deductions']:,.2f}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"Error testing API: {e}")

if __name__ == "__main__":
    test_api()
