
# FarmCredit API Documentation

## Overview

The **FarmCredit API** provides a set of endpoints to calculate credit scores, process FAQ queries, and handle real-time conversations for farmers using a variety of data sources. It supports loan and transaction information, provides dynamic responses to FAQ queries, and facilitates interactive conversations to assist farmers.


---

## Endpoints

### 1. **GET /**

**Description:**
Returns a simple status message confirming the API is running.

**Response:**

```json
{
  "Status": "OK",
  "Message": "Welcome to the Credit Score API!"
}
```

---

### 2. **POST /calculate\_credit\_score**

**Description:**
Calculates the credit score for a farmer based on the provided data.

**Request Body:**

```json
{
  "farmers": {
    "id": "string",
    "age": 30,
    "created_at": "2020-01-01T00:00:00Z",
    "highest_education": "University",
    "gender": "Male",
    "mobile_wallet_balance": 10000.00,
    "bvn": "12345678901",
    "other_sources_of_income": "Trading"
  },
  "farmer_next_of_kin": [
    {
      "id": "123",
      "farmer_id": "123",
      "full_name": "Jane Doe"
    }
  ],
  "farms": [
    {
      "id": "1",
      "farmer_id": "123",
      "size": 2.5,
      "start_date": "2015-01-01T00:00:00Z",
      "number_of_harvests": 5
    }
  ],
  "farm_production": [
    {
      "id": "1",
      "farm_id": "1",
      "type": "Maize",
      "expected_yield": 2000,
      "expected_unit_profit": 5.0
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
      "id": "1",
      "farmer_id": "123",
      "amount_requested": 10000,
      "existing_loans": false,
      "total_existing_loan_amount": 0,
      "status": "approved",
      "created_at": "2022-06-01T00:00:00Z"
    }
  ],
  "loan_contract": [
    {
      "id": "1",
      "loan_application_id": "1",
      "amount_disbursed": 10000,
      "interest_rate": 10,
      "created_at": "2022-06-01T00:00:00Z"
    }
  ],
  "loan_repayments": [
    {
      "id": "1",
      "loan_contract_id": "1",
      "periodic_repayment_amount": 27500,
      "interest_amount": 2500,
      "created_at": "2022-07-05T00:00:00Z",
      "date_paid": "2022-07-04T00:00:00Z",
      "due_date": "2022-07-05T00:00:00Z"
    }
  ],
  "transaction_history": [
    {
      "id": "1",
      "farmer_id": "123",
      "transaction_data": {"type": "deposit", "amount": 5000},
      "created_at": "2022-05-01T00:00:00Z"
    }
  ]
}
```

**Response:**

```json
{
  "responseCode": 200,
  "responseMessage": "Credit score calculated successfully",
  "data": {
    "credit_score": 750,
    "credit_rating": "Excellent",
    "component_scores": {
      "personal_demographic": 80,
      "financial_history": 150,
      "loan_history": 200,
      "agricultural_factors": 180,
      "geographical": 90
    },
    "max_component_points": {
      "personal_demographic": 100,
      "financial_history": 200,
      "loan_history": 250,
      "agricultural_factors": 200,
      "geographical": 100
    },
    "raw_score": 800,
    "max_possible": 850
  }
}
```

**Errors:**

* `500 Internal Server Error`: If there is an error during the credit score calculation process.

---

### 3. **POST /query\_faq**

**Description:**
Processes a FAQ query from the user and returns the response from the AI system.

**Request Body:**

```json
{
  "query": "How do I apply for a loan?"
}
```

**Response:**

```json
{
  "responseCode": 200,
  "responseMessage": "FAQ query processed successfully",
  "data": {
    "query": "How do I apply for a loan?",
    "answer": "To apply for a loan, please fill out the application form on the Farm Credit app and submit the required documents."
  }
}
```

**Errors:**

* `500 Internal Server Error`: If there is an error processing the FAQ query.

---

### 4. **POST /converse**

**Description:**
Handles a conversational query from the user, providing personalized and contextual responses.

**Request Body:**

```json
{
  "user_info": {
    "name": "John Doe",
    "wallet_balance": 15000,
    "available_loans": [
      {
        "id": "1",
        "loan_application_id": "1",
        "amount_disbursed": 10000,
        "interest_rate": 10,
        "created_at": "2022-06-01T00:00:00Z"
      }
    ],
    "credit_score": 750
  },
  "query": "Can I get a loan for my farm?",
  "context": [
    {
      "message_position": 1,
      "sender": "user",
      "message": "Can I get a loan for my farm?"
    }
  ]
}
```

**Response:**

```json
{
  "responseCode": 200,
  "responseMessage": "FAQ query processed successfully",
  "data": {
    "query": "Can I get a loan for my farm?",
    "answer": "Based on your current credit score and available loan products, you are eligible to apply for a loan. Please check the available options in the app."
  }
}
```

**Errors:**

* `500 Internal Server Error`: If there is an error during the conversation processing.

---

## Models

### CreditScoreRequestModel

* `farmers`: Farmer data including personal and financial information.
* `farmer_next_of_kin`: Information about the farmer's next of kin.
* `farms`: Information about the farms owned by the farmer.
* `farm_production`: Information about farm production.
* `address`: The address details of the farmer.
* `loan_application`: Details of the loan application.
* `loan_contract`: Information about loan contracts.
* `loan_repayments`: Repayment history of loans.
* `transaction_history`: Transaction history linked to the farmer’s wallet.

### QueryFAQRequestModel

* `query`: A string containing the FAQ query.

### ConversationRequestModel

* `user_info`: Details about the user, including wallet balance, available loans, and credit score.
* `query`: The query or question from the user.
* `context`: Contextual information to understand the conversation history.

---

## Running the Application

1. Install dependencies:

   ```bash
   pip install fastapi mangum pydantic
   ```

2. Run the app with Uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

3. Use the `/docs` endpoint to interact with the API through Swagger UI.

---

## License

This project is licensed under the MIT License.

