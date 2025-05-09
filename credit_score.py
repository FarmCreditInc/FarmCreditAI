import datetime
import json
from typing import Dict, Any, List, Optional

def calculate_credit_score(farmer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate the credit score for a rural farmer based on a traditional model.
    
    Args:
        farmer_data (Dict[str, Any]): JSON containing all relevant farmer data from database
        
    Returns:
        Dict[str, Any]: Credit score results including total score and component scores
    """
    # Initialize component scores
    component_scores = {
        "personal_demographic": 0,
        "financial_history": 0,
        "loan_history": 0, 
        "agricultural_factors": 0,
        "geographical": 0
    }
    
    max_points = {
        "personal_demographic": 100,  # 100 points (11.76%)
        "financial_history": 200,     # 200 points (23.53%)
        "loan_history": 250,          # 250 points (29.41%)
        "agricultural_factors": 200,  # 200 points (23.53%)
        "geographical": 100           # 100 points (11.76%)
    }
    
    # 1. Personal & Demographic Information (100 points max)
    component_scores["personal_demographic"] = calculate_personal_demographic_score(farmer_data)
    
    # 2. Financial History & Stability (200 points max)
    component_scores["financial_history"] = calculate_financial_history_score(farmer_data)
    
    # 3. Loan History (250 points max)
    component_scores["loan_history"] = calculate_loan_history_score(farmer_data)
    
    # 4. Agricultural Factors (200 points max)
    component_scores["agricultural_factors"] = calculate_agricultural_factors_score(farmer_data)
    
    # 5. Geographical & Environmental (100 points max)
    component_scores["geographical"] = calculate_geographical_score(farmer_data)
    
    # Calculate total raw score (0-850)
    raw_score = sum(component_scores.values())
    
    # Scale to final score range (300-850)
    min_possible = 0
    max_possible = sum(max_points.values())  # 850
    min_final = 300
    max_final = 850
    
    scaled_score = min_final + ((raw_score - min_possible) * (max_final - min_final) / (max_possible - min_possible))
    final_score = round(max(min_final, min(max_final, scaled_score)))
    
    # Determine credit rating
    credit_rating = get_credit_rating(final_score)
    
    # Prepare and return results
    results = {
        "credit_score": final_score,
        "credit_rating": credit_rating,
        "component_scores": component_scores,
        "max_component_points": max_points,
        "raw_score": raw_score,
        "max_possible": max_possible
    }
    
    return results

def get_credit_rating(score: int) -> str:
    """Determine credit rating based on score."""
    if score >= 750:
        return "Excellent"
    elif score >= 670:
        return "Good"
    elif score >= 580:
        return "Fair"
    elif score >= 500:
        return "Poor"
    else:
        return "Very Poor"

def calculate_personal_demographic_score(data: Dict[str, Any]) -> int:
    """
    Calculate score for personal and demographic factors.
    Max 100 points.
    """
    score = 0
    
    # Age factor (0-25 points)
    age = data.get("farmers", {}).get("age", 0)
    if age >= 30 and age <= 55:
        score += 25  # Prime age range
    elif age > 55 and age <= 65:
        score += 20
    elif age > 18 and age < 30:
        score += 15
    else:
        score += 10
    
    # Experience factor (0-25 points)
    experience_years = calculate_years_of_experience(data)
    if experience_years >= 5:
        score += 25
    elif experience_years >= 3:
        score += 20
    elif experience_years >= 1:
        score += 15
    else:
        score += 5
    
    # Education level (0-20 points)
    education = data.get("farmers", {}).get("highest_education", "").lower()
    if "university" in education or "degree" in education:
        score += 20
    elif "college" in education or "diploma" in education:
        score += 15
    elif "secondary" in education or "high school" in education:
        score += 10
    else:
        score += 5
    
    # Family support (0-30 points)
    next_of_kin = data.get("farmer_next_of_kin", [])
    if len(next_of_kin) > 0:
        score += 30
    
    return min(score, 100)  # Cap at max points

def calculate_years_of_experience(data: Dict[str, Any]) -> float:
    """Calculate years of experience based on farmers.created_at."""
    created_at_str = data.get("farmers", {}).get("created_at")
    if not created_at_str:
        return 0
    
    try:
        created_at = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        now = datetime.datetime.now(datetime.timezone.utc)
        return (now - created_at).days / 365.25
    except (ValueError, TypeError):
        return 0

def calculate_financial_history_score(data: Dict[str, Any]) -> int:
    """
    Calculate score for financial history and stability.
    Max 200 points.
    """
    score = 0
    
    # Wallet balance (0-50 points)
    wallet_balance = data.get("farmers", {}).get("mobile_wallet_balance", 0)
    if wallet_balance >= 100000:
        score += 50
    elif wallet_balance >= 50000:
        score += 40
    elif wallet_balance >= 10000:
        score += 30
    elif wallet_balance >= 1000:
        score += 20
    elif wallet_balance > 0:
        score += 10
    
    # BVN verification (0-50 points)
    if data.get("farmers", {}).get("bvn"):
        score += 50
    
    # Alternative income (0-40 points)
    if data.get("farmers", {}).get("other_sources_of_income"):
        score += 40
    
    # Transaction history (0-60 points)
    transactions = data.get("transaction_history", [])
    transaction_score = analyze_transactions(transactions)
    score += transaction_score
    
    return min(score, 200)  # Cap at max points

def analyze_transactions(transactions: List[Dict[str, Any]]) -> int:
    """Analyze transaction history and return a score out of 60."""
    if not transactions:
        return 0
        
    score = 0
    
    # Transaction frequency (0-20 points)
    if len(transactions) >= 10:
        score += 20
    elif len(transactions) >= 5:
        score += 15
    elif len(transactions) >= 2:
        score += 10
    elif len(transactions) == 1:
        score += 5
    
    # Calculate average and variance in transaction amounts
    amounts = []
    recent_count = 0
    now = datetime.datetime.now(datetime.timezone.utc)
    
    for tx in transactions:
        tx_data = tx.get("transaction_data", {})
        if isinstance(tx_data, str):
            try:
                tx_data = json.loads(tx_data)
            except:
                tx_data = {}
                
        amount = tx_data.get("amount", 0)
        if amount > 0:
            amounts.append(amount)
        
        # Check recency (transactions in last 3 months)
        tx_date_str = tx.get("created_at")
        if tx_date_str:
            try:
                tx_date = datetime.datetime.fromisoformat(tx_date_str.replace('Z', '+00:00'))
                if (now - tx_date).days <= 90:
                    recent_count += 1
            except (ValueError, TypeError):
                pass
    
    # Average transaction amount (0-20 points)
    if amounts:
        avg_amount = sum(amounts) / len(amounts)
        if avg_amount >= 50000:
            score += 20
        elif avg_amount >= 10000:
            score += 15
        elif avg_amount >= 1000:
            score += 10
        else:
            score += 5
    
    # Recency of transactions (0-20 points)
    if recent_count >= 5:
        score += 20
    elif recent_count >= 3:
        score += 15
    elif recent_count >= 1:
        score += 10
        
    return min(score, 60)  # Cap at max 60 points for transaction analysis

def calculate_loan_history_score(data: Dict[str, Any]) -> int:
    """
    Calculate score for loan history.
    Max 250 points.
    """
    score = 0
    
    # Get loan applications and contracts
    loan_applications = data.get("loan_application", [])
    loan_contracts = data.get("loan_contract", [])
    loan_repayments = data.get("loan_repayments", [])
    
    # Process repayment history if there are any loans
    if loan_contracts:
        repayment_score = analyze_loan_repayments(loan_contracts, loan_repayments)
        score += repayment_score  # Up to 150 points
    else:
        # No loan history, give partial credit (first-time borrowers)
        score += 75  # Half of the maximum repayment score
    
    # Existing debt load (0-100 points)
    debt_score = analyze_debt_load(loan_applications)
    score += debt_score
    
    return min(score, 250)  # Cap at max points

def analyze_loan_repayments(loan_contracts: List[Dict[str, Any]], loan_repayments: List[Dict[str, Any]]) -> int:
    """Analyze loan repayment history and return a score out of 150."""
    if not loan_contracts or not loan_repayments:
        return 75  # Neutral score for no history
    
    score = 0
    
    # Map repayments to their contracts
    contract_repayments = {}
    for repayment in loan_repayments:
        contract_id = repayment.get("loan_contract_id")
        if contract_id:
            if contract_id not in contract_repayments:
                contract_repayments[contract_id] = []
            contract_repayments[contract_id].append(repayment)
    
    total_on_time = 0
    total_repayments = 0
    days_late_sum = 0
    fully_repaid_loans = 0
    
    # Analyze each contract's repayments
    for contract in loan_contracts:
        contract_id = contract.get("id")
        if not contract_id or contract_id not in contract_repayments:
            continue
        
        repayments = contract_repayments[contract_id]
        contract_on_time = 0
        contract_total = len(repayments)
        contract_days_late = 0
        all_paid = True
        
        for repayment in repayments:
            due_date_str = repayment.get("due_date")
            date_paid_str = repayment.get("date_paid")
            
            if not due_date_str or not date_paid_str:
                all_paid = False
                continue
                
            try:
                due_date = datetime.datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                date_paid = datetime.datetime.fromisoformat(date_paid_str.replace('Z', '+00:00'))
                
                if date_paid <= due_date:
                    contract_on_time += 1
                else:
                    days_late = (date_paid - due_date).days
                    contract_days_late += days_late
            except (ValueError, TypeError):
                all_paid = False
                continue
        
        total_on_time += contract_on_time
        total_repayments += contract_total
        days_late_sum += contract_days_late
        
        if all_paid and contract_total > 0:
            fully_repaid_loans += 1
    
    # On-time payment ratio (0-60 points)
    if total_repayments > 0:
        on_time_ratio = total_on_time / total_repayments
        if on_time_ratio >= 0.95:
            score += 60
        elif on_time_ratio >= 0.9:
            score += 50
        elif on_time_ratio >= 0.8:
            score += 40
        elif on_time_ratio >= 0.7:
            score += 30
        elif on_time_ratio >= 0.6:
            score += 20
        else:
            score += 10
    else:
        score += 30  # Neutral score for no repayment history
    
    # Average days late (0-40 points)
    if total_repayments > 0:
        avg_days_late = days_late_sum / total_repayments
        if avg_days_late <= 0:
            score += 40
        elif avg_days_late <= 3:
            score += 30
        elif avg_days_late <= 7:
            score += 20
        elif avg_days_late <= 14:
            score += 10
        else:
            score += 0
    else:
        score += 20  # Neutral score for no history
    
    # Number of fully repaid loans (0-50 points)
    if fully_repaid_loans >= 3:
        score += 50
    elif fully_repaid_loans == 2:
        score += 40
    elif fully_repaid_loans == 1:
        score += 30
    else:
        score += 15  # Some credit for no fully repaid loans
    
    return min(score, 150)  # Cap at max points

def analyze_debt_load(loan_applications: List[Dict[str, Any]]) -> int:
    """Analyze existing debt load and return a score out of 100."""
    score = 0
    
    # Find the most recent loan application
    most_recent = None
    for application in loan_applications:
        if application.get("status") == "approved":
            if most_recent is None:
                most_recent = application
            else:
                app_date_str = application.get("created_at")
                recent_date_str = most_recent.get("created_at")
                
                if app_date_str and recent_date_str:
                    try:
                        app_date = datetime.datetime.fromisoformat(app_date_str.replace('Z', '+00:00'))
                        recent_date = datetime.datetime.fromisoformat(recent_date_str.replace('Z', '+00:00'))
                        
                        if app_date > recent_date:
                            most_recent = application
                    except (ValueError, TypeError):
                        pass
    
    if most_recent:
        # Check if there are existing loans
        has_existing_loans = most_recent.get("existing_loans", False)
        
        if not has_existing_loans:
            # No existing loans, full points
            score += 100
        else:
            # Existing loans, analyze debt load
            existing_loan_amount = most_recent.get("total_existing_loan_amount", 0)
            
            # Without income data, we'll use heuristics based on loan amount
            if existing_loan_amount <= 10000:
                score += 80
            elif existing_loan_amount <= 50000:
                score += 60
            elif existing_loan_amount <= 100000:
                score += 40
            elif existing_loan_amount <= 200000:
                score += 20
            else:
                score += 0
    else:
        # No loan applications, neutral score
        score += 50
    
    return min(score, 100)  # Cap at max points

def calculate_agricultural_factors_score(data: Dict[str, Any]) -> int:
    """
    Calculate score for agricultural factors.
    Max 200 points.
    """
    score = 0
    
    farms = data.get("farms", [])
    farm_production = data.get("farm_production", [])
    
    if not farms:
        return 50  # Minimal score if no farm data
    
    # Farm size (0-40 points)
    total_farm_size = sum(farm.get("size", 0) for farm in farms)
    if total_farm_size >= 10:
        score += 40
    elif total_farm_size >= 5:
        score += 30
    elif total_farm_size >= 2:
        score += 20
    elif total_farm_size > 0:
        score += 10
    
    # Crop diversity (0-40 points)
    crop_types = set()
    for production in farm_production:
        crop_type = production.get("type")
        if crop_type:
            crop_types.add(crop_type)
    
    if len(crop_types) >= 3:
        score += 40
    elif len(crop_types) == 2:
        score += 30
    elif len(crop_types) == 1:
        score += 20
    
    # Farming experience (0-40 points)
    farming_experience = calculate_farming_experience(farms)
    if farming_experience >= 10:
        score += 40
    elif farming_experience >= 5:
        score += 30
    elif farming_experience >= 2:
        score += 20
    elif farming_experience > 0:
        score += 10
    
    # Production history (0-40 points)
    production_score = analyze_production_history(farms, farm_production)
    score += production_score
    
    # Expected profit margin (0-40 points)
    profit_score = analyze_profit_margin(farm_production)
    score += profit_score
    
    return min(score, 200)  # Cap at max points

def calculate_farming_experience(farms: List[Dict[str, Any]]) -> float:
    """Calculate years of farming experience from the oldest farm start date."""
    if not farms:
        return 0
    
    oldest_start_date = None
    for farm in farms:
        start_date_str = farm.get("start_date")
        if not start_date_str:
            continue
            
        try:
            start_date = datetime.datetime.fromisoformat(start_date_str.replace('Z', '+00:00')).date()
            if oldest_start_date is None or start_date < oldest_start_date:
                oldest_start_date = start_date
        except (ValueError, TypeError):
            pass
    
    if oldest_start_date:
        now = datetime.datetime.now().date()
        return (now - oldest_start_date).days / 365.25
    return 0

def analyze_production_history(farms: List[Dict[str, Any]], 
                             farm_production: List[Dict[str, Any]]) -> int:
    """Analyze production history and return a score out of 40."""
    score = 0
    
    # Number of successful harvests (0-20 points)
    total_harvests = sum(farm.get("number_of_harvests", 0) for farm in farms)
    if total_harvests >= 10:
        score += 20
    elif total_harvests >= 5:
        score += 15
    elif total_harvests >= 2:
        score += 10
    elif total_harvests >= 1:
        score += 5
    
    # Expected yield (0-20 points)
    if farm_production:
        avg_yield = sum(prod.get("expected_yield", 0) for prod in farm_production) / len(farm_production)
        
        # Without context for what's a "good" yield, we'll use a heuristic
        if avg_yield > 0:
            score += 20  # Any positive expected yield gets full points
    
    return min(score, 40)  # Cap at max points

def analyze_profit_margin(farm_production: List[Dict[str, Any]]) -> int:
    """Analyze expected profit margins and return a score out of 40."""
    if not farm_production:
        return 0
    
    profit_margins = []
    for prod in farm_production:
        expected_profit = prod.get("expected_unit_profit", 0)
        if expected_profit > 0:
            profit_margins.append(expected_profit)
    
    if not profit_margins:
        return 0
    
    avg_profit_margin = sum(profit_margins) / len(profit_margins)
    
    # Score based on average profit margin
    if avg_profit_margin >= 1000:
        return 40
    elif avg_profit_margin >= 500:
        return 30
    elif avg_profit_margin >= 100:
        return 20
    elif avg_profit_margin > 0:
        return 10
    else:
        return 0

def calculate_geographical_score(data: Dict[str, Any]) -> int:
    """
    Calculate score for geographical and environmental factors.
    Max 100 points.
    """
    score = 0
    
    # Access address information from farms and farmer
    addresses = []
    
    # Get farmer address
    farmer_address_id = data.get("farmers", {}).get("address_id")
    if farmer_address_id:
        for address in data.get("address", []):
            if address.get("id") == farmer_address_id:
                addresses.append(address)
                break
    
    # Get farm addresses
    for farm in data.get("farms", []):
        farm_address_id = farm.get("address_id")
        if farm_address_id:
            for address in data.get("address", []):
                if address.get("id") == farm_address_id:
                    addresses.append(address)
                    break
    
    if not addresses:
        return 50  # Neutral score if no location data
    
    # Location risk score based on geopolitical zone (0-60 points)
    location_risk_score = 0
    risk_zones = {
        # Assign risk scores to different geopolitical zones
        # This is just a placeholder - replace with actual risk assessments
        "north central": 45,
        "north east": 30,  # Higher risk
        "north west": 40,
        "south east": 50,
        "south south": 50,
        "south west": 60
    }
    
    zone_scores = []
    for address in addresses:
        zone = address.get("geopolitical_zone", "").lower()
        if zone in risk_zones:
            zone_scores.append(risk_zones[zone])
    
    if zone_scores:
        location_risk_score = sum(zone_scores) / len(zone_scores)
    else:
        location_risk_score = 30  # Default if zone not recognized
    
    score += location_risk_score
    
    # Proximity to markets based on coordinates (0-40 points)
    # This is a simplified placeholder - in a real implementation
    # you would calculate actual distances to known markets
    has_coordinates = any(
        address.get("latitude") is not None and address.get("longitude") is not None
        for address in addresses
    )
    
    if has_coordinates:
        score += 40  # Full points if coordinates are available
    else:
        score += 20  # Partial points otherwise
    
    return min(score, 100)  # Cap at max points


def process_farmer_credit_score(farmer_data_json: str) -> Dict[str, Any]:
    """
    Process a JSON string containing farmer data and calculate credit score.
    
    Args:
        farmer_data_json (str): JSON string with farmer data
        
    Returns:
        Dict[str, Any]: Credit score results
    """
    try:
        farmer_data = json.loads(farmer_data_json)
        return calculate_credit_score(farmer_data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON input"}
    except Exception as e:
        return {"error": f"Error calculating credit score: {str(e)}"}


# Example usage
if __name__ == "__main__":
    # This is just a sample - replace with actual data
    sample_data = {
        "farmers": {
            "id": "123",
            "age": 10,
            "created_at": "2020-01-15T00:00:00Z",
            "highest_education": "Primary School",
            "gender": "Male",
            "mobile_wallet_balance": 2,
            "bvn": "12345678901",
            "other_sources_of_income": "Trading"
        },
        "farmer_next_of_kin": [
            {"id": "456", "farmer_id": "123", "full_name": "Jane Doe"}
        ],
        "farms": [
            {
                "id": "789",
                "farmer_id": "123",
                "size": 1,
                "start_date": "2025-03-10",
                "number_of_harvests": 0
            }
        ],
        "farm_production": [
            {
                "id": "101",
                "farm_id": "789",
                "type": "Maize",
                "expected_yield": 2000,
                "expected_unit_profit": 5
            },
            {
                "id": "102",
                "farm_id": "789",
                "type": "Cassava",
                "expected_yield": 3000,
                "expected_unit_profit": 3
            }
        ],
        "address": [
            {
                "id": "abc",
                "geopolitical_zone": "South West",
                "latitude": 6.5244,
                "longitude": 3.3792
            }
        ],
        "loan_application": [
            {
                "id": "def",
                "farmer_id": "123",
                "amount_requested": 10000,
                "existing_loans": False,
                "total_existing_loan_amount": 0,
                "status": "approved",
                "created_at": "2022-06-01T00:00:00Z"
            }
        ],
        "loan_contract": [
            {
                "id": "ghi",
                "loan_application_id": "def",
                "amount_disbursed": 100000,
                "interest_rate": 10,
                "created_at": "2022-06-05T00:00:00Z"
            }
        ],
        "loan_repayments": [
            {
                "id": "jkl",
                "loan_contract_id": "ghi",
                "periodic_repayment_amount": 27500,
                "interest_amount": 2500,
                "created_at": "2022-07-05T00:00:00Z",
                "date_paid": "2025-07-04T00:00:00Z",
                "due_date": "2022-07-05T00:00:00Z"
            },
            {
                "id": "mno",
                "loan_contract_id": "ghi",
                "periodic_repayment_amount": 27500,
                "interest_amount": 2500,
                "created_at": "2022-08-05T00:00:00Z",
                "date_paid": "2025-08-05T00:00:00Z",
                "due_date": "2022-08-05T00:00:00Z"
            }
        ],
        "transaction_history": [
            {
                "id": "pqr",
                "farmer_id": "123",
                "transaction_data": {"type": "deposit", "amount": 5},
                "created_at": "2022-05-01T00:00:00Z"
            },
            {
                "id": "stu",
                "farmer_id": "123",
                "transaction_data": {"type": "withdrawal", "amount": 2},
                "created_at": "2022-05-15T00:00:00Z"
            }
        ]
    }
    
    # Convert to JSON string as would be received by the function
    sample_json = json.dumps(sample_data)
    
    # Process and print results
    results = process_farmer_credit_score(sample_json)
    print(json.dumps(results, indent=2))