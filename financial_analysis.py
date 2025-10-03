"""
Financial Analysis Service
Handles loan calculations, affordability analysis, and financial metrics
"""

from typing import Dict, Any, List
import math

class FinancialAnalysisService:
    """Service for financial calculations and analysis"""
    
    def __init__(self):
        # Affordability guidelines (percentage of income)
        self.affordability_thresholds = {
            'conservative': 0.10,  # 10% of gross income
            'moderate': 0.15,      # 15% of gross income
            'aggressive': 0.20     # 20% of gross income
        }
    
    def calculate_loan_payments(self, loan_amount: float, interest_rate: float, 
                               loan_term_years: int, analysis_years: int) -> List[Dict[str, Any]]:
        """Calculate loan payment schedule"""
        
        if loan_amount <= 0 or interest_rate <= 0:
            return []
        
        # Convert to monthly values
        monthly_rate = interest_rate / 100 / 12
        total_months = loan_term_years * 12
        
        # Calculate monthly payment using PMT formula
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**total_months) / \
                            ((1 + monthly_rate)**total_months - 1)
        else:
            monthly_payment = loan_amount / total_months
        
        # Generate payment schedule
        schedule = []
        remaining_balance = loan_amount
        
        for year in range(1, min(analysis_years + 1, loan_term_years + 1)):
            year_interest = 0
            year_principal = 0
            
            for month in range(12):
                if remaining_balance <= 0:
                    break
                
                # Calculate monthly interest and principal
                monthly_interest = remaining_balance * monthly_rate
                monthly_principal = monthly_payment - monthly_interest
                
                # Ensure we don't pay more than remaining balance
                if monthly_principal > remaining_balance:
                    monthly_principal = remaining_balance
                    monthly_payment = monthly_principal + monthly_interest
                
                year_interest += monthly_interest
                year_principal += monthly_principal
                remaining_balance -= monthly_principal
            
            schedule.append({
                'year': year,
                'annual_payment': monthly_payment * 12,
                'annual_interest': year_interest,
                'annual_principal': year_principal,
                'remaining_balance': remaining_balance
            })
        
        return schedule
    
    def calculate_lease_payment(self, vehicle_msrp: float, residual_value_percent: float,
                              money_factor: float, lease_term_years: int,
                              down_payment: float = 0) -> Dict[str, Any]:
        """Calculate lease payment breakdown"""
        
        # Calculate residual value
        residual_value = vehicle_msrp * (residual_value_percent / 100)
        
        # Calculate depreciation amount
        depreciation_amount = vehicle_msrp - residual_value - down_payment
        
        # Monthly depreciation
        monthly_depreciation = depreciation_amount / (lease_term_years * 12)
        
        # Monthly finance charge (interest)
        monthly_finance_charge = (vehicle_msrp + residual_value) * money_factor
        
        # Total monthly payment (before taxes)
        monthly_payment = monthly_depreciation + monthly_finance_charge
        
        return {
            'monthly_payment': monthly_payment,
            'monthly_depreciation': monthly_depreciation,
            'monthly_finance_charge': monthly_finance_charge,
            'total_lease_cost': monthly_payment * lease_term_years * 12 + down_payment,
            'residual_value': residual_value,
            'depreciation_amount': depreciation_amount
        }
    
    def calculate_affordability(self, annual_cost: float, gross_income: float,
                              transaction_type: str = 'purchase') -> Dict[str, Any]:
        """Calculate affordability metrics and recommendations"""
        
        if gross_income <= 0:
            return {'is_affordable': False, 'percentage_of_income': 0}
        
        # Calculate percentage of income
        percentage_of_income = (annual_cost / gross_income) * 100
        
        # Determine affordability based on conservative threshold
        conservative_threshold = self.affordability_thresholds['conservative'] * 100
        moderate_threshold = self.affordability_thresholds['moderate'] * 100
        aggressive_threshold = self.affordability_thresholds['aggressive'] * 100
        
        is_affordable = percentage_of_income <= moderate_threshold
        
        # Affordability rating
        if percentage_of_income <= conservative_threshold:
            affordability_rating = "Excellent"
            rating_description = "Well within recommended budget guidelines"
        elif percentage_of_income <= moderate_threshold:
            affordability_rating = "Good" 
            rating_description = "Within reasonable budget guidelines"
        elif percentage_of_income <= aggressive_threshold:
            affordability_rating = "Marginal"
            rating_description = "At the upper limit of recommended spending"
        else:
            affordability_rating = "Poor"
            rating_description = "Exceeds recommended budget guidelines"
        
        # Calculate monthly impact
        monthly_cost = annual_cost / 12
        monthly_income = gross_income / 12
        monthly_budget_impact = monthly_cost
        
        return {
            'is_affordable': is_affordable,
            'percentage_of_income': percentage_of_income,
            'affordability_rating': affordability_rating,
            'rating_description': rating_description,
            'annual_cost': annual_cost,
            'monthly_cost': monthly_cost,
            'monthly_budget_impact': monthly_budget_impact,
            'recommended_max_annual': gross_income * self.affordability_thresholds['moderate'],
            'recommended_max_monthly': (gross_income * self.affordability_thresholds['moderate']) / 12,
            'over_budget_amount': max(0, annual_cost - (gross_income * self.affordability_thresholds['moderate']))
        }
    
    def calculate_total_cost_of_ownership_summary(self, annual_costs: List[float]) -> Dict[str, Any]:
        """Calculate TCO summary metrics"""
        
        if not annual_costs:
            return {}
        
        total_cost = sum(annual_costs)
        average_annual = total_cost / len(annual_costs)
        
        # Calculate year-over-year changes
        annual_changes = []
        for i in range(1, len(annual_costs)):
            change = annual_costs[i] - annual_costs[i-1]
            change_percent = (change / annual_costs[i-1]) * 100 if annual_costs[i-1] > 0 else 0
            annual_changes.append({
                'year': i + 1,
                'change_amount': change,
                'change_percent': change_percent
            })
        
        return {
            'total_cost': total_cost,
            'average_annual_cost': average_annual,
            'years_analyzed': len(annual_costs),
            'highest_annual_cost': max(annual_costs),
            'lowest_annual_cost': min(annual_costs),
            'cost_variation': max(annual_costs) - min(annual_costs),
            'annual_changes': annual_changes
        }
    
    def compare_financing_options(self, vehicle_price: float, scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare different financing scenarios"""
        
        comparison_results = []
        
        for scenario in scenarios:
            if scenario['type'] == 'cash':
                total_cost = vehicle_price
                monthly_payment = 0
                total_interest = 0
                
            elif scenario['type'] == 'loan':
                loan_schedule = self.calculate_loan_payments(
                    loan_amount=scenario['loan_amount'],
                    interest_rate=scenario['interest_rate'],
                    loan_term_years=scenario['loan_term'],
                    analysis_years=scenario['loan_term']
                )
                
                total_payments = sum(year['annual_payment'] for year in loan_schedule)
                total_interest = sum(year['annual_interest'] for year in loan_schedule)
                total_cost = vehicle_price - scenario['loan_amount'] + total_payments
                monthly_payment = loan_schedule[0]['annual_payment'] / 12 if loan_schedule else 0
                
            elif scenario['type'] == 'lease':
                lease_calc = self.calculate_lease_payment(
                    vehicle_msrp=vehicle_price,
                    residual_value_percent=scenario['residual_percent'],
                    money_factor=scenario['money_factor'],
                    lease_term_years=scenario['lease_term'],
                    down_payment=scenario.get('down_payment', 0)
                )
                
                total_cost = lease_calc['total_lease_cost']
                monthly_payment = lease_calc['monthly_payment']
                total_interest = lease_calc['monthly_finance_charge'] * scenario['lease_term'] * 12
            
            comparison_results.append({
                'scenario_name': scenario['name'],
                'type': scenario['type'],
                'total_cost': total_cost,
                'monthly_payment': monthly_payment,
                'total_interest': total_interest,
                'scenario_details': scenario
            })
        
        # Sort by total cost
        comparison_results.sort(key=lambda x: x['total_cost'])
        
        return {
            'scenarios': comparison_results,
            'best_option': comparison_results[0],
            'worst_option': comparison_results[-1],
            'savings_best_vs_worst': comparison_results[-1]['total_cost'] - comparison_results[0]['total_cost']
        }
    
    def calculate_break_even_analysis(self, lease_option: Dict[str, Any], 
                                    purchase_option: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate break-even point between lease and purchase"""
        
        # This is a simplified break-even analysis
        # In practice, this would be more complex considering depreciation, etc.
        
        lease_monthly = lease_option.get('monthly_payment', 0)
        purchase_monthly = purchase_option.get('monthly_payment', 0)
        
        if lease_monthly >= purchase_monthly:
            return {
                'break_even_months': 0,
                'recommendation': 'Purchase is always cheaper',
                'monthly_savings_purchase': lease_monthly - purchase_monthly
            }
        
        # Calculate break-even considering vehicle value retention
        purchase_total_cost = purchase_option.get('total_cost', 0)
        lease_total_cost = lease_option.get('total_cost', 0)
        
        monthly_difference = purchase_monthly - lease_monthly
        
        if monthly_difference > 0:
            break_even_months = (purchase_total_cost - lease_total_cost) / monthly_difference
        else:
            break_even_months = float('inf')
        
        return {
            'break_even_months': break_even_months,
            'break_even_years': break_even_months / 12,
            'monthly_difference': monthly_difference,
            'recommendation': 'Lease' if break_even_months > 36 else 'Purchase'
        }
    
    def generate_financial_insights(self, affordability: Dict[str, Any], 
                                  cost_breakdown: Dict[str, Any]) -> List[str]:
        """Generate financial insights and recommendations"""
        
        insights = []
        
        # Affordability insights
        if affordability['is_affordable']:
            insights.append(f"✅ This vehicle fits well within your budget at {affordability['percentage_of_income']:.1f}% of income")
        else:
            insights.append(f"⚠️ This vehicle may strain your budget at {affordability['percentage_of_income']:.1f}% of income")
            insights.append(f"💡 Consider a vehicle costing ${affordability['over_budget_amount']:,.0f} less to stay within guidelines")
        
        # Cost optimization insights
        largest_category = max(cost_breakdown.items(), key=lambda x: x[1])
        insights.append(f"💰 {largest_category[0].replace('_', ' ').title()} is your largest cost at ${largest_category[1]:,.0f}")
        
        # General financial advice
        insights.append("📊 Consider comparing lease vs purchase options for the same vehicle")
        insights.append("🔍 Shop around for insurance and financing to optimize costs")
        
        return insights

# Test function
def test_financial_analysis():
    """Test the financial analysis service"""
    service = FinancialAnalysisService()
    
    # Test affordability
    affordability = service.calculate_affordability(
        annual_cost=8000,
        gross_income=60000
    )
    
    print("Affordability Analysis:")
    print(f"Percentage of income: {affordability['percentage_of_income']:.1f}%")
    print(f"Affordable: {affordability['is_affordable']}")
    print(f"Rating: {affordability['affordability_rating']}")
    
    # Test loan calculation
    loan_schedule = service.calculate_loan_payments(
        loan_amount=25000,
        interest_rate=6.5,
        loan_term_years=5,
        analysis_years=5
    )
    
    print(f"\nLoan Schedule (first 3 years):")
    for year_data in loan_schedule[:3]:
        print(f"Year {year_data['year']}: Payment ${year_data['annual_payment']:,.0f}, "
              f"Interest ${year_data['annual_interest']:,.0f}")

if __name__ == "__main__":
    test_financial_analysis()