from fastapi import FastAPI, HTTPException
import json
import credit_score as cs
import rag.querying
import converse 
from mangum import Mangum
from models.request import CreditScoreRequestModel, QueryFAQRequestModel, ConversationRequestModel


app = FastAPI(debug=True)
#handler = Mangum(app)

@app.get("/")
def read_root():
    return {"Status": "OK", "Message": "Welcome to the Credit Score API!"}

@app.post("/calculate_credit_score")
def calculate_credit_score(request: CreditScoreRequestModel):
    try:
        # Convert the request object to a dictionary using model_dump
        request_data = request.model_dump()
        request_data
        # Pass the dictionary to the calculate_credit_score function
        credit_scoring_details = cs.calculate_credit_score(request_data)

        return {
            "responseCode": 200,
            "responseMessage": "Credit score calculated successfully",
            "data": credit_scoring_details
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query_faq")
def query_faq(request: QueryFAQRequestModel):
    try:
        # Convert the request object to a dictionary using model_dump
        request_data = request.model_dump()
        query = request_data['query']
        
        # Pass the dictionary to the query_faq function
        faq_response = rag.querying.rag_pipeline(query)

        return {
            "responseCode": 200,
            "responseMessage": "FAQ query processed successfully",
            "data": {
                "query": query,
                "answer": faq_response
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/converse")
def conversation(request: ConversationRequestModel):
    try:
        # Convert the request object to a dictionary using model_dump
        request_data = request.model_dump()
        query = request_data['query']
        user_info = request_data['user_info']
        context = request_data['context']
        
        print("Query:", query)
        print("User Info:", user_info)
        print("Context:", context)
        
        # Pass the dictionary to the query_faq function
        respone = converse.converse_pipeline(query, user_info, context)

        return {
            "responseCode": 200,
            "responseMessage": "FAQ query processed successfully",
            "data": {
                "query": query,
                "answer": respone
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))