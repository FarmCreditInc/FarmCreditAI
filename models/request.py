from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class Farmer(BaseModel):
    id: str
    age: int
    created_at: datetime
    highest_education: str
    gender: str
    mobile_wallet_balance: float
    bvn: str
    other_sources_of_income: str

class FarmerNextOfKin(BaseModel):
    id: str
    farmer_id: str
    full_name: str

class Farm(BaseModel):
    id: str
    farmer_id: str
    size: float
    start_date: datetime
    number_of_harvests: int

class FarmProduction(BaseModel):
    id: str
    farm_id: str
    type: str
    expected_yield: int
    expected_unit_profit: float

class Address(BaseModel):
    id: str
    geopolitical_zone: str
    latitude: float
    longitude: float

class LoanApplication(BaseModel):
    id: str
    farmer_id: str
    amount_requested: float
    existing_loans: bool
    total_existing_loan_amount: float
    status: str
    created_at: datetime

class LoanContract(BaseModel):
    id: str
    loan_application_id: str
    amount_disbursed: float
    interest_rate: float
    created_at: datetime

class LoanRepayment(BaseModel):
    id: str
    loan_contract_id: str
    periodic_repayment_amount: float
    interest_amount: float
    created_at: datetime
    date_paid: datetime
    due_date: datetime

class TransactionHistory(BaseModel):
    id: str
    farmer_id: str
    transaction_data: Dict[str, float]
    created_at: datetime

class CreditScoreRequestModel(BaseModel):
    farmers: Farmer
    farmer_next_of_kin: List[FarmerNextOfKin]
    farms: List[Farm]
    farm_production: List[FarmProduction]
    address: List[Address]
    loan_application: List[LoanApplication]
    loan_contract: List[LoanContract]
    loan_repayments: List[LoanRepayment]
    transaction_history: List[TransactionHistory]

class QueryFAQRequestModel(BaseModel):
    query: str

class UserInfo(BaseModel):
    name: str
    wallet_balance: float
    available_loans: List[LoanContract]
    credit_score: float

class Context(BaseModel):
    message_position: int
    sender: str
    message: str

class ConversationRequestModel(BaseModel):
    user_info: UserInfo
    query: str
    context: List[Context]
