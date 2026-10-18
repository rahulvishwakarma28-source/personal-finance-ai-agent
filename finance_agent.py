from langchain.tools import tool

from langchain.agents import create_agent

from langchain_openai import ChatOpenAI



@tool
def calculator(
    first_number: float,
    second_number: float,
    operation: str
) -> dict:
    """Calculate using add, subtract, multiply, divide, or percentage.
    For percentage, enter the percentage as first_number and the amount
    as second_number. Example: 20% of 85000 uses 20 and 85000.
    """

    if operation == "add":
        result = first_number + second_number
    elif operation == "subtract":
        result = first_number - second_number
    elif operation == "multiply":
        result = first_number * second_number
    elif operation == "divide":
        if second_number == 0:
            return {"error": "Cannot divide by zero."}
        result = first_number / second_number
    elif operation == "percentage":
        result = first_number * second_number / 100
    else:
        return {"error": "Choose add, subtract, multiply, divide, or percentage."}

    return {"Result": round(result, 2)}



@tool
def emi_calculator(
    loan_amount: float,
    annual_interest_rate: float,
    years: int
) -> dict:
    """Calculate loan EMI. Enter the annual interest rate as a percentage, such as 8 for 8%."""

    if loan_amount <= 0 or years <= 0 or annual_interest_rate < 0:
        return {"error": "Enter a positive loan amount and years, and a nonnegative interest rate."}

    months = years * 12
    monthly_rate = annual_interest_rate / 1200

    if monthly_rate == 0:
        emi = loan_amount / months
    else:
        emi = (
            loan_amount * monthly_rate
            / (1 - (1 + monthly_rate) ** (-months))
        )

    return {
        "Monthly EMI": round(emi, 2),
        "Total repayment": round(emi * months, 2),
        "Total interest": round(emi * months - loan_amount, 2)
    }



@tool
def sip_calculator(
    monthly_investment: float,
    annual_return_rate: float,
    years: int
) -> dict:
    """Estimate monthly investment growth. Enter the annual return as a percentage, such as 10 for 10%."""

    if monthly_investment <= 0 or years <= 0 or annual_return_rate < 0:
        return {"error": "Enter a positive investment and years, and a nonnegative return rate."}

    months = years * 12
    monthly_rate = annual_return_rate / 1200
    total_invested = monthly_investment * months

    if monthly_rate == 0:
        future_value = total_invested
    else:
        future_value = monthly_investment * (
            ((1 + monthly_rate) ** months - 1) / monthly_rate
        )

    return {
        "Total invested": round(total_invested, 2),
        "Estimated future value": round(future_value, 2),
        "Estimated gain": round(future_value - total_invested, 2)
    }



@tool
def savings_goal_calculator(
    target_amount: float,
    annual_return_rate: float,
    years: int
) -> dict:
    """Calculate monthly savings needed to reach a target, starting from zero.
    Use end-of-month payments and an annual return percentage.
    Enter 0 for saving without investment growth.
    """

    if target_amount <= 0 or years <= 0 or annual_return_rate < 0:
        return {"error": "Enter a positive target and years, and a nonnegative return rate."}

    months = years * 12
    monthly_rate = annual_return_rate / 1200

    if monthly_rate == 0:
        monthly_savings = target_amount / months
    else:
        monthly_savings = (
            target_amount * monthly_rate
            / ((1 + monthly_rate) ** months - 1)
        )

    return {
        "Target amount": round(target_amount, 2),
        "Monthly savings needed": round(monthly_savings, 2),
        "Annual return assumed (%)": annual_return_rate,
        "Years": years
    }



@tool
def budget_planner(monthly_income: float) -> dict:
    """Divide monthly take-home income using the 50-30-20 budget rule."""

    if monthly_income <= 0:
        return {"error": "Enter a monthly income greater than zero."}

    return {
        "Monthly income": round(monthly_income, 2),
        "Needs (50%)": round(monthly_income * 0.50, 2),
        "Wants (30%)": round(monthly_income * 0.30, 2),
        "Savings (20%)": round(monthly_income * 0.20, 2)
    }



FINANCE_INSTRUCTIONS = "\nYou are a personal finance calculator assistant.\n\nChoose the correct tool for the user's question.\nAlways use tools for calculations.\nAsk for missing details instead of guessing.\nConvert lakh and crore amounts into numbers before using tools.\nInterest and return rates are annual percentages.\nUse whole years for EMI and SIP calculations. Ask for clarification\nif the requested period cannot be entered as whole years.\n\nExplain the tool results briefly in simple English.\nShow money in Indian rupees unless another currency is specified.\nFor SIP results, mention that returns are estimates, not guaranteed.\nFor budgets, explain that the allocation follows the 50-30-20 rule.\nIf a tool returns an error, explain it and ask for corrected details.\n\nUse savings_goal_calculator for monthly savings needed to reach a target.\nIt assumes zero starting savings and end-of-month payments.\nAsk for the expected annual return if it is missing.\nDo not assume a return rate. For positive returns, explain that the\nresult is an estimate and actual returns can vary.\n"


def build_finance_agent(api_key):
    model = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=api_key,
        temperature=0,
        timeout=30,
        max_retries=0,
        default_headers={"Accept-Encoding": "identity"}
    )

    return create_agent(
        model=model,
        tools=[
            calculator,
            emi_calculator,
            sip_calculator,
            savings_goal_calculator,
            budget_planner
        ],
        system_prompt=FINANCE_INSTRUCTIONS
    )
