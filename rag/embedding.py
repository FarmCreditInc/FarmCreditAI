import json
import boto3
from pinecone import Pinecone,ServerlessSpec
import uuid


# Initialize Pinecone connection
pc = Pinecone(api_key="pcsk_5pEARi_DNbj63Mj7ABLU113t4z64p68KZeFwK5UoYMvRHzjWcGycbb3PUi5WNE1LsZ76vs")

# Initialize Bedrock client for embedding generation
bedrock = boto3.client(service_name='bedrock-runtime')
modelId = "amazon.titan-embed-text-v2:0"

# Create or connect to the farmcredit index
index_name = "farmcredit"
dimension = 512  # Reduced dimension to 512
metric = "cosine"  # Similarity metric


# Check if index already exists to avoid re-creation
if index_name not in pc.list_indexes().names():
    # Create index with the serverless spec for AWS
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric=metric,
        spec=ServerlessSpec(
            cloud="aws",  # Ensure to specify the cloud provider (AWS)
            region="us-east-1"  # Specify the region (AWS region in this case)
        )
    )

# Connect to the created index
index = pc.Index(index_name)

def embed_and_upsert_chunks(chunks, bedrock=bedrock, modelId=modelId, index=index):
    """
    Embeds a list of FAQ chunks using AWS Titan and upserts them into the Pinecone index.

    Args:
    - chunks (list): List of dictionaries containing 'question' and 'answer' keys
    - bedrock (boto3.client): The Boto3 client for AWS Bedrock to generate embeddings
    - modelId (str): The model ID for the embedding model
    - index (pinecone.Index): The Pinecone index to upsert the embeddings into
    """
    
    for chunk in chunks:
        question = chunk['question']
        answer = chunk['answer']
        
        # Prepare the input for the embedding model
        input_text = f"Q: {question}\nA: {answer}"

        # Create the input_data for the embedding request
        input_data = {
            "inputText": input_text,  
            "dimensions": 512,
            "normalize": True
        }

        # Serialize the data to JSON
        body = json.dumps(input_data).encode('utf-8')

        # Invoke Bedrock to get embeddings for this chunk
        response = bedrock.invoke_model(
            modelId=modelId,
            contentType="application/json",
            accept="*/*",
            body=body
        )

        response_body = response['body'].read()
        response_json = json.loads(response_body)

        # Extract the embedding for this chunk
        chunk_embedding = response_json['embedding']
        
        # Generate a new ID using UUID for uniqueness
        new_id = str(uuid.uuid4())

        # Prepare the vector for upsert into Pinecone
        vectors = [
            (
                new_id,  # Unique ID for the vector
                chunk_embedding,  # Embedding vector
                {"question": question, "answer": answer}  # Metadata with question and answer
            )
        ]

        # Upsert the vector into the Pinecone index
        index.upsert(vectors=vectors)

    print("Chunks upserted successfully to Pinecone.")

# Example usage: List of FAQ chunks to embed and upsert
faq_chunks = [
    {
        "question": "Who is eligible to register on the platform?",
        "answer": "Nigerian youth farmers between the ages of 18-35 who own or operate agricultural businesses are eligible to register. You'll need basic personal information, details about your farm, and some financial history."
    },
    {
        "question": "How is my credit score calculated?",
        "answer": "Your credit score is calculated based on multiple factors including your farm size, crop types, years of experience, past loan history, income estimates, farming practices, and membership in cooperatives. The scoring system is transparent, and you'll receive a breakdown of factors affecting your score."
    },
    {
        "question": "What types of loans are available?",
        "answer": "The platform offers various types of agricultural loans including working capital loans for inputs (seeds, fertilizers), equipment financing, expansion loans, and emergency funds. Loan amounts, interest rates, and terms vary based on your credit score and specific needs."
    },
    {
        "question": "How long does the loan approval process take?",
        "answer": "Once you submit a complete application, the initial assessment typically takes 3-5 business days. If approved, fund disbursement can take an additional 2-3 business days depending on the financial institution and your banking details."
    },
    {
        "question": "What happens if I can't repay my loan on time?",
        "answer": "We understand that agricultural businesses face unique challenges. If you anticipate difficulty making a payment, contact us immediately. We can work with you to restructure your repayment plan. However, consistent late payments or defaults will negatively impact your credit score."
    },
    {
        "question": "How can I improve my credit score?",
        "answer": "You can improve your score by: joining a registered cooperative, adopting modern farming practices, maintaining accurate records of your farm activities and finances, building a positive repayment history with smaller loans, and completing educational modules on our platform."
    },
    {
        "question": "How do I get started with FarmCredit?",
        "answer": "To get started, simply register on the platform by providing your personal details, farm information, and some financial history. After registration, you'll build your credit profile, receive your credit score, and can apply for financing options."
    },
    {
        "question": "Is my information secure on the platform?",
        "answer": "Yes, we prioritize the security of your personal and financial information. Our platform uses industry-standard encryption and security protocols to ensure your data is kept safe and private."
    },
    {
        "question": "What if I don't have a credit history?",
        "answer": "No problem! Our platform provides the opportunity for farmers with little or no credit history to build their credit score. Your farm's data, financial records, and involvement in cooperatives will contribute towards creating your score."
    },
    {
        "question": "Can I apply for loans if I am a member of a cooperative?",
        "answer": "Yes, being a member of a registered cooperative can strengthen your credit profile, potentially leading to better loan terms and access to more financing options."
    },
    {
        "question": "What are the repayment terms for loans?",
        "answer": "Repayment terms are flexible and depend on the loan type, amount, and your financial situation. You will be able to review the terms during the application process before confirming your loan agreement."
    },
    {
        "question": "What happens after I receive a loan?",
        "answer": "Once your loan is disbursed, you can use the funds to invest in your farm, improve your farming practices, and grow your agricultural business. The platform also provides tools to help you track your business growth and manage loan repayments."
    },
    {
        "question": "Can I get an emergency loan?",
        "answer": "Yes, emergency loans are available for farmers facing unexpected challenges. These loans are designed to help you continue operations during critical times, with fast application and approval processes."
    },
    {
        "question": "Do I need to provide collateral for loans?",
        "answer": "In most cases, no collateral is required. The platform focuses on building your credit profile based on your farm and financial data. However, for larger loans, additional documentation may be required."
    },
    {
        "question": "How often is my credit score updated?",
        "answer": "Your credit score is updated regularly based on new data such as repayment history, farm activities, and other factors that may affect your creditworthiness."
    },
    {
        "question": "Can I apply for more than one loan at a time?",
        "answer": "Yes, you can apply for multiple loans, but each loan application will be evaluated independently based on your credit score and current financial standing."
    },
    {
        "question": "How can I contact customer support?",
        "answer": "You can reach out to our customer support team through the 'Contact Us' section on the platform. We are available to assist you with any questions or concerns you may have."
    },
    {
        "question": "Are there any fees to register on the platform?",
        "answer": "No, registration on the FarmCredit platform is completely free. You can register, build your credit profile, and apply for loans without incurring any upfront costs."
    },
    {
        "question": "Can I use the loan for non-farming purposes?",
        "answer": "Our loans are specifically designed to support agricultural activities. Funds should be used for farm-related expenses such as purchasing inputs, equipment, or expanding your farm."
    },
    {
        "question": "What is FarmCredit's mission?",
        "answer": "FarmCredit's mission is to empower Nigerian youth farmers by providing accessible financial services and educational resources that enable them to build sustainable agricultural businesses and achieve financial independence."
    },
    {
        "question": "Who founded FarmCredit?",
        "answer": "FarmCredit was founded by Adebayo Ogunlesi, who recognized the challenges faced by Nigerian youth farmers in accessing financial resources to grow their agricultural businesses."
    },
    {
        "question": "What inspired the creation of FarmCredit?",
        "answer": "The creation of FarmCredit was inspired by the founder's firsthand experience with the struggles of young farmers who had the skills to succeed but lacked access to the financial resources they needed to thrive."
    },
    {
        "question": "How does FarmCredit assess a farmer's creditworthiness?",
        "answer": "FarmCredit uses alternative data and tailored credit scoring models to assess farmers' creditworthiness, addressing the lack of credit history that many young farmers face."
    },
    {
        "question": "What services does FarmCredit offer to farmers?",
        "answer": "FarmCredit offers a platform that facilitates access to loans, provides educational resources to improve financial literacy, and helps farmers improve their agricultural practices."
    },
    {
        "question": "What is FarmCredit's vision for Nigeria?",
        "answer": "FarmCredit envisions a Nigeria where every youth farmer has the financial resources and knowledge needed to thrive, contributing to food security, economic growth, and rural development across the country."
    },
    {
        "question": "What values guide FarmCredit's operations?",
        "answer": "FarmCredit is guided by the following core values: Accessibility, Innovation, Transparency, Empowerment, Collaboration, and Integrity."
    },
    {
        "question": "How does FarmCredit support Nigerian youth farmers?",
        "answer": "FarmCredit supports Nigerian youth farmers by providing access to financial services, educational resources, and a transparent and fair credit scoring system that empowers them to build sustainable agricultural businesses."
    },
    {
        "question": "What are some key achievements of FarmCredit?",
        "answer": "FarmCredit has facilitated over ₦500M in loans, supported 10,000+ registered farmers, partnered with 25+ financial institutions, and covered 32 Nigerian states."
    },
    {
        "question": "What are FarmCredit's core principles?",
        "answer": "FarmCredit's core principles are: Accessibility, Innovation, Transparency, Empowerment, Collaboration, and Integrity."
    },
    {
        "question": "When was FarmCredit founded?",
        "answer": "FarmCredit was founded in 2020 as a solution to address the financing gap faced by Nigerian youth farmers."
    },
    {
        "question": "What milestone did FarmCredit reach in 2021?",
        "answer": "In 2021, FarmCredit conducted extensive research on agricultural finance and credit scoring models for smallholder farmers."
    },
    {
        "question": "What was FarmCredit's focus in 2022?",
        "answer": "In 2022, FarmCredit focused on developing and testing the initial version of the platform with an emphasis on user experience."
    },
    {
        "question": "When was the FarmCredit platform officially launched?",
        "answer": "FarmCredit was officially launched in 2023, allowing Nigerian youth farmers to access credit through the platform."
    },
    {
        "question": "What expansion did FarmCredit undergo in 2024?",
        "answer": "In 2024, FarmCredit expanded its services to include educational resources and partnerships with more financial institutions."
    },
    {
        "question": "How many farmers are registered on the FarmCredit platform?",
        "answer": "FarmCredit has registered over 10,000 farmers on its platform."
    },
    {
        "question": "How many financial partners does FarmCredit have?",
        "answer": "FarmCredit has partnered with over 25 financial institutions to provide loan access to youth farmers."
    },
    {
        "question": "How many Nigerian states does FarmCredit cover?",
        "answer": "FarmCredit covers 32 Nigerian states, providing access to agricultural finance across the country."
    },
    {
        "question": "What has been the journey of FarmCredit from its inception to today?",
        "answer": "FarmCredit's journey began in 2020 with the idea conception to address the financing gap faced by Nigerian youth farmers. In 2021, the company conducted extensive research on agricultural finance and credit scoring models. By 2022, the platform was developed and tested with a focus on user experience. FarmCredit officially launched in 2023, providing access to credit for Nigerian youth farmers. In 2024, the company expanded its services, adding educational resources and building partnerships with more financial institutions to enhance its impact."
    },
    {
        "question": "What is FarmCredit's mission?",
        "answer": "FarmCredit's mission is to transform agricultural finance in Nigeria by providing innovative credit solutions and empowering Nigerian youth farmers with access to financial resources and educational tools."
    },
    {
        "question": "Who are the core team members behind FarmCredit?",
        "answer": "The core team at FarmCredit includes Ozigbo Chidera (CTO), Nancy Amandi (Head of Data Infrastructure), Frank Felix (Lead AI/ML Scientist), and Oluwatobi Afintinni (Financial Data Analytics Manager)."
    },
    {
        "question": "Who are the members of FarmCredit's Board of Advisors?",
        "answer": "FarmCredit's Board of Advisors includes Dr. Obinna Ezeocha (Board Chairman), Mrs. Funmi Adebanjo, Mr. Tanko Musa Danjuma, Prof. Nneka Okafor, and Mr. Ayodele Ighodalo."
    },
    {
        "question": "How does FarmCredit empower Nigerian farmers?",
        "answer": "FarmCredit empowers Nigerian farmers by providing access to financial tools through innovative credit scoring, loan facilitation, and educational resources to help them build sustainable agricultural businesses."
    },
    {
        "question": "What does FarmCredit offer to those interested in joining the team?",
        "answer": "FarmCredit offers opportunities for talented individuals passionate about agricultural finance and technology to join the team and contribute to its mission of empowering Nigerian youth farmers."
    },
    {
        "question": "How do I manage my account on FarmCredit?",
        "answer": "To manage your FarmCredit account, start by creating an account with basic personal and farm information. You can update your profile by logging into your dashboard and accessing the 'Profile Settings' section. Here, you can edit personal details, farm information, and upload required documents. For account security, ensure you enable two-factor authentication (2FA) and update your password regularly to prevent unauthorized access. In case of password issues, you can reset it using the 'Forgot Password' option. Always remember to log out after use, especially on shared devices, and use strong passwords to protect your account."
    },
    {
        "question": "What resources are available for farmers on the FarmCredit platform?",
        "answer": "FarmCredit offers a variety of resources tailored to help farmers succeed. These include financial resources such as loans, with easy application processes and competitive rates. Farmers can upload relevant farm documents such as identification, land ownership, and crop reports for loan applications. The platform also provides tools for tracking application statuses in real-time, ensuring transparency throughout the process. Additionally, FarmCredit supports farmers with educational resources like farming guides, financial literacy courses, and cooperative-building advice, all of which are designed to improve both financial knowledge and agricultural practices."
    },
    {
        "question": "How do lenders get involved in Nigerian agriculture through FarmCredit?",
        "answer": "Lenders can get involved by signing up as investors on the FarmCredit platform. Once registered, they can review farmer profiles that include key data such as credit scores, farming history, and financial standing. The investment process is simple: lenders choose which farmers to support based on their creditworthiness and project needs. FarmCredit ensures that all investments are backed by transparent data, including projected returns on investment (ROI). Lenders can track their investments through their dashboard, receiving periodic updates on repayment schedules, loan statuses, and overall performance of the farmers they support."
    },
    {
        "question": "What should I do if I encounter issues while using the FarmCredit platform?",
        "answer": "If you encounter problems while using FarmCredit, several troubleshooting solutions are available. For login issues, ensure your credentials are correct or use the 'Forgot Password' option to reset. If you're having trouble uploading documents, verify that your files are in the supported formats (PDF, JPG, PNG) and meet the size requirements. Payment difficulties can often be resolved by checking your payment method or ensuring your bank account details are accurate. If you're using the mobile app and encounter issues, ensure the app is updated to the latest version, and check for any server-related problems in your area. For any other issues, reach out to our support team through the 'Help Center' for personalized assistance."
    },
    {
        "question": "What is the timeline and process for applying for a loan on FarmCredit?",
        "answer": "The loan application process on FarmCredit is straightforward but requires some time for thorough review. First, complete your application by providing your personal details, farm information, and financial history. Upload all required documents such as your ID, proof of farm ownership, and financial statements. Once submitted, the application enters the verification phase where we assess the authenticity of your documents and the accuracy of your information. This can take up to 3-5 business days. After verification, we review your loan eligibility based on our credit scoring system. If approved, you will receive the loan offer, which includes terms, interest rates, and repayment schedules. Funds are typically disbursed within 2-3 business days following approval."
    },
    {
        "question": "What are the first steps for getting started on FarmCredit?",
        "answer": "Getting started on FarmCredit is easy. First, create an account by providing your personal details and farm information. Once your account is set up, you'll be prompted to choose your role—either as a farmer or lender. Afterward, familiarize yourself with the platform's features through our 'Getting Started' guide, which walks you through how to complete your profile, upload documents, and apply for loans (if you're a farmer) or make investments (if you're a lender). Understand our mission of empowering Nigerian youth farmers and contributing to rural development. For first-time users, we recommend visiting our Education Hub for guides on how to improve your farming practices and financial literacy."
    }
]

# Call the function to embed and upsert chunks
#embed_and_upsert_chunks(faq_chunks)
