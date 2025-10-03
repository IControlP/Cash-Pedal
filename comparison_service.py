"""
Vehicle Comparison Service
Handles multiple vehicle comparisons, rankings, and analysis
"""

from typing import Dict, Any, List
import pandas as pd
from services.prediction_service import PredictionService

class ComparisonService:
    """Service for comparing multiple vehicles"""
    
    def __init__(self):
        self.prediction_service = PredictionService()
    
    def compare_vehicles(self, vehicles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple vehicles and generate comprehensive analysis"""
        
        vehicle_results = []
        
        for vehicle in vehicles:
            try:
                # Calculate TCO using prediction service
                tco_results = self.prediction_service.calculate_total_cost_of_ownership(vehicle)
                
                # Extract key metrics for comparison
                vehicle_result = self._extract_comparison_metrics(vehicle, tco_results)
                vehicle_results.append(vehicle_result)
                
            except Exception as e:
                # Handle calculation errors gracefully
                vehicle_result = self._create_error_result(vehicle, str(e))
                vehicle_results.append(vehicle_result)
        
        # Generate comparison analysis
        comparison_analysis = self._analyze_vehicle_comparison(vehicle_results)
        
        # Create rankings
        rankings = self._create_vehicle_rankings(vehicle_results)
        
        # Generate insights
        insights = self._generate_comparison_insights(vehicle_results, comparison_analysis)
        
        return {
            'vehicles': vehicle_results,
            'analysis': comparison_analysis,
            'rankings': rankings,
            'insights': insights,
            'summary': self._create_comparison_summary(vehicle_results, rankings),
            'best_overall': rankings.get('best_annual_cost'),
            'cost_range': comparison_analysis.get('cost_statistics', {}).get('cost_range', 0),
            'average_annual_cost': comparison_analysis.get('cost_statistics', {}).get('avg_annual_cost', 0)
        }
    
    def _extract_comparison_metrics(self, vehicle: Dict[str, Any], 
                                  tco_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics for vehicle comparison"""
        
        summary = tco_results.get('summary', {})
        affordability = tco_results.get('affordability', {})
        category_totals = tco_results.get('category_totals', {})
        
        # CRITICAL FIX: Extract the correct annual cost
        annual_cost = summary.get('average_annual_cost', 0)
        
        # Get total cost - different field names for lease vs purchase
        if vehicle['transaction_type'].lower() == 'lease':
            total_cost = summary.get('total_lease_cost', 0)
        else:
            total_cost = summary.get('total_ownership_cost', 0)
        
        # Double-check: if annual cost is close to total cost, something's wrong
        analysis_years = vehicle.get('analysis_years', 5)
        if analysis_years > 1 and annual_cost > total_cost * 0.8:
            # This suggests annual_cost field contains total cost, fix it
            annual_cost = total_cost / analysis_years
            print(f"Fixed annual cost calculation for {vehicle['make']} {vehicle['model']}: ${annual_cost:,.0f}")
        
        # Calculate value score (lower cost per mile + affordability)
        cost_per_mile = summary.get('cost_per_mile', 0)
        affordability_score = affordability.get('percentage_of_income', 20)
        
        # Value score: inverse of cost factors (higher is better)
        if cost_per_mile > 0 and affordability_score > 0:
            value_score = 100 / (cost_per_mile * 1000 + affordability_score)
        else:
            value_score = 0
        
        return {
            'vehicle_name': f"{vehicle['year']} {vehicle['make']} {vehicle['model']} {vehicle['trim']}",
            'make': vehicle['make'],
            'model': vehicle['model'],
            'year': vehicle['year'],
            'trim': vehicle['trim'],
            'transaction_type': vehicle['transaction_type'],
            'annual_cost': annual_cost,  # FIXED: Now correctly using annual cost
            'total_cost': total_cost,
            'monthly_cost': annual_cost / 12,  # Based on corrected annual cost
            'cost_per_mile': cost_per_mile,
            'final_value': summary.get('final_vehicle_value', 0),
            'is_affordable': affordability.get('is_affordable', False),
            'affordability_score': affordability_score,
            'value_score': value_score,
            'cost_categories': category_totals,
            'analysis_years': analysis_years,
            'annual_mileage': vehicle.get('annual_mileage', 0),
            'purchase_price': vehicle.get('purchase_price', vehicle.get('trim_msrp', 0)),
            'calculation_successful': True,
            'raw_results': tco_results
        }
    
    def _create_error_result(self, vehicle: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """Create error result for failed calculations"""
        
        return {
            'vehicle_name': f"{vehicle['year']} {vehicle['make']} {vehicle['model']} {vehicle['trim']}",
            'make': vehicle['make'],
            'model': vehicle['model'],
            'year': vehicle['year'],
            'trim': vehicle['trim'],
            'transaction_type': vehicle['transaction_type'],
            'annual_cost': 0,
            'total_cost': 0,
            'monthly_cost': 0,
            'cost_per_mile': 0,
            'final_value': 0,
            'is_affordable': False,
            'affordability_score': 0,
            'value_score': 0,
            'cost_categories': {},
            'analysis_years': 0,
            'calculation_successful': False,
            'error_message': error_message
        }
    
    def _analyze_vehicle_comparison(self, vehicle_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the comparison results"""
        
        successful_results = [v for v in vehicle_results if v.get('calculation_successful', False)]
        
        if not successful_results:
            return {'error': 'No successful calculations to analyze'}
        
        # Extract costs for analysis (using corrected annual costs)
        annual_costs = [v['annual_cost'] for v in successful_results]
        total_costs = [v['total_cost'] for v in successful_results]
        
        analysis = {
            'vehicle_count': len(successful_results),
            'cost_statistics': {
                'min_annual_cost': min(annual_costs),
                'max_annual_cost': max(annual_costs),
                'avg_annual_cost': sum(annual_costs) / len(annual_costs),
                'cost_range': max(annual_costs) - min(annual_costs),  # Now using correct annual costs
                'min_total_cost': min(total_costs),
                'max_total_cost': max(total_costs),
                'avg_total_cost': sum(total_costs) / len(total_costs)
            },
            'affordability_analysis': {
                'affordable_count': sum(1 for v in successful_results if v['is_affordable']),
                'affordable_percentage': sum(1 for v in successful_results if v['is_affordable']) / len(successful_results) * 100,
                'avg_affordability_score': sum(v['affordability_score'] for v in successful_results) / len(successful_results)
            },
            'transaction_type_breakdown': {
                'lease_count': sum(1 for v in successful_results if v['transaction_type'].lower() == 'lease'),
                'purchase_count': sum(1 for v in successful_results if v['transaction_type'].lower() == 'purchase')
            }
        }
        
        return analysis
    
    def _create_vehicle_rankings(self, vehicle_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create vehicle rankings by different criteria"""
        
        successful_results = [v for v in vehicle_results if v.get('calculation_successful', False)]
        
        if not successful_results:
            return {}
        
        rankings = {
            'by_annual_cost': sorted(successful_results, key=lambda x: x['annual_cost']),
            'by_total_cost': sorted(successful_results, key=lambda x: x['total_cost']),
            'by_value_score': sorted(successful_results, key=lambda x: x['value_score'], reverse=True),
            'by_affordability': sorted([v for v in successful_results if v['affordability_score'] > 0], 
                                     key=lambda x: x['affordability_score']),
            'by_cost_per_mile': sorted([v for v in successful_results if v['cost_per_mile'] > 0], 
                                     key=lambda x: x['cost_per_mile'])
        }
        
        # Add best/worst for each category
        rankings['best_annual_cost'] = rankings['by_annual_cost'][0] if rankings['by_annual_cost'] else None
        rankings['best_total_cost'] = rankings['by_total_cost'][0] if rankings['by_total_cost'] else None
        rankings['best_value'] = rankings['by_value_score'][0] if rankings['by_value_score'] else None
        rankings['most_affordable'] = rankings['by_affordability'][0] if rankings['by_affordability'] else None
        rankings['best_efficiency'] = rankings['by_cost_per_mile'][0] if rankings['by_cost_per_mile'] else None
        
        return rankings
    
    def _generate_comparison_insights(self, vehicle_results: List[Dict[str, Any]], 
                                    analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from comparison analysis"""
        
        insights = []
        
        if analysis.get('error'):
            insights.append("Unable to generate insights due to calculation errors")
            return insights
        
        cost_stats = analysis.get('cost_statistics', {})
        affordability = analysis.get('affordability_analysis', {})
        transaction_breakdown = analysis.get('transaction_type_breakdown', {})
        
        # Cost range insights (now using corrected annual costs)
        cost_range = cost_stats.get('cost_range', 0)
        if cost_range > 5000:
            insights.append(f"Significant cost variation: ${cost_range:,.0f} difference between highest and lowest annual costs")
        elif cost_range < 1000:
            insights.append("All vehicles have similar annual costs - consider other factors for decision")
        
        # Affordability insights
        affordable_percentage = affordability.get('affordable_percentage', 0)
        if affordable_percentage == 100:
            insights.append("All vehicles in comparison are within your budget guidelines (≤10% of income)")
        elif affordable_percentage == 0:
            insights.append("None of the vehicles meet conservative affordability guidelines (≤10% of income)")
        else:
            insights.append(f"{affordable_percentage:.0f}% of vehicles meet affordability guidelines (≤10% of income)")
        
        # Transaction type insights
        lease_count = transaction_breakdown.get('lease_count', 0)
        purchase_count = transaction_breakdown.get('purchase_count', 0)
        
        if lease_count > 0 and purchase_count > 0:
            insights.append("Comparison includes both lease and purchase options - consider long-term value vs. lower monthly payments")
        
        # Cost efficiency insights
        min_annual = cost_stats.get('min_annual_cost', 0)
        max_annual = cost_stats.get('max_annual_cost', 0)
        avg_annual = cost_stats.get('avg_annual_cost', 0)
        
        if min_annual > 0:
            savings_potential = max_annual - min_annual
            if savings_potential > 3000:
                insights.append(f"Choosing the most cost-effective option could save ${savings_potential:,.0f} annually")
        
        return insights
    
    def _create_comparison_summary(self, vehicle_results: List[Dict[str, Any]], 
                                 rankings: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of comparison results"""
        
        successful_results = [v for v in vehicle_results if v.get('calculation_successful', False)]
        
        if not successful_results:
            return {'error': 'No successful calculations to summarize'}
        
        return {
            'total_vehicles': len(vehicle_results),
            'successful_calculations': len(successful_results),
            'failed_calculations': len(vehicle_results) - len(successful_results),
            'best_overall': rankings.get('best_annual_cost'),  # Use annual cost as primary ranking
            'most_affordable': rankings.get('most_affordable'),
            'best_value': rankings.get('best_value'),
            'cost_leader': rankings.get('best_annual_cost'),
            'recommendation': self._generate_overall_recommendation(rankings)
        }
    
    def _generate_overall_recommendation(self, rankings: Dict[str, Any]) -> str:
        """Generate overall recommendation based on rankings"""
        
        best_annual = rankings.get('best_annual_cost')
        most_affordable = rankings.get('most_affordable')
        best_value = rankings.get('best_value')
        
        if not best_annual:
            return "Unable to generate recommendation due to insufficient data"
        
        # Check if the same vehicle wins multiple categories
        if best_annual and most_affordable and best_annual['vehicle_name'] == most_affordable['vehicle_name']:
            return f"Clear winner: {best_annual['vehicle_name']} offers both lowest cost and best affordability"
        elif best_annual and best_value and best_annual['vehicle_name'] == best_value['vehicle_name']:
            return f"Excellent choice: {best_annual['vehicle_name']} provides the best overall value proposition"
        elif best_annual:
            return f"Cost-effective option: {best_annual['vehicle_name']} has the lowest annual ownership cost"
        else:
            return "Consider your priorities: cost, affordability, or overall value when making your decision"
    
    def export_comparison_csv(self, comparison_results: Dict[str, Any]) -> str:
        """Export comparison results to CSV format"""
        
        vehicles = comparison_results.get('vehicles', [])
        if not vehicles:
            return ""
        
        # Create DataFrame for export
        export_data = []
        
        for vehicle in vehicles:
            row = {
                'Vehicle': vehicle['vehicle_name'],
                'Transaction Type': vehicle['transaction_type'],
                'Annual Cost': vehicle['annual_cost'],
                'Total Cost': vehicle['total_cost'],
                'Monthly Cost': vehicle.get('monthly_cost', 0),
                'Cost per Mile': vehicle.get('cost_per_mile', 0),
                'Affordability Score': vehicle.get('affordability_score', 'N/A'),
                'Value Score': vehicle.get('value_score', 'N/A')
            }
            
            # Add cost category breakdowns
            cost_categories = vehicle.get('cost_categories', {})
            for category, amount in cost_categories.items():
                row[category.replace('_', ' ').title()] = amount
            
            export_data.append(row)
        
        df = pd.DataFrame(export_data)
        return df.to_csv(index=False)
    
    def get_vehicle_recommendations(self, comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed recommendations for each vehicle"""
        
        vehicles = comparison_results.get('vehicles', [])
        rankings = comparison_results.get('rankings', {})
        
        vehicle_recommendations = {}
        
        for vehicle in vehicles:
            if not vehicle.get('calculation_successful', False):
                continue
            
            vehicle_name = vehicle['vehicle_name']
            pros = []
            cons = []
            
            # Analyze relative performance
            annual_cost = vehicle['annual_cost']
            is_affordable = vehicle['is_affordable']
            cost_per_mile = vehicle['cost_per_mile']
            value_score = vehicle['value_score']
            
            # Cost analysis
            if rankings.get('best_annual_cost') and vehicle_name == rankings['best_annual_cost']['vehicle_name']:
                pros.append("Lowest annual ownership cost in comparison")
            elif annual_cost > 0:
                avg_cost = comparison_results.get('average_annual_cost', annual_cost)
                if annual_cost < avg_cost * 0.9:
                    pros.append("Below-average annual costs")
                elif annual_cost > avg_cost * 1.1:
                    cons.append("Above-average annual costs")
            
            # Affordability analysis
            if is_affordable:
                pros.append("Meets affordability guidelines for your income")
            else:
                cons.append("May strain your budget based on income guidelines")
            
            # Efficiency analysis
            if rankings.get('best_efficiency') and vehicle_name == rankings['best_efficiency']['vehicle_name']:
                pros.append("Most cost-efficient per mile driven")
            
            # Value analysis
            if rankings.get('best_value') and vehicle_name == rankings['best_value']['vehicle_name']:
                pros.append("Best overall value proposition")
            
            # Transaction type specific
            if vehicle['transaction_type'].lower() == 'lease':
                pros.append("Lower monthly payments and warranty coverage")
                cons.append("No equity building or ownership")
            else:
                pros.append("Build equity and own the vehicle")
                if vehicle.get('final_value', 0) > 0:
                    pros.append(f"Retains ${vehicle['final_value']:,.0f} in value")
                cons.append("Higher upfront costs and maintenance responsibility")
            
            # Generate recommendation
            if len(pros) > len(cons):
                overall_rec = "Recommended - strong value proposition with multiple advantages"
            elif len(cons) > len(pros):
                overall_rec = "Consider carefully - some potential drawbacks to evaluate"
            else:
                overall_rec = "Solid option - balanced pros and cons"
            
            # Best use case
            if is_affordable and annual_cost > 0:
                if vehicle['transaction_type'].lower() == 'lease':
                    best_use_case = "Drivers who prefer lower monthly payments and latest features"
                else:
                    best_use_case = "Long-term ownership and building vehicle equity"
            else:
                best_use_case = "Budget-conscious buyers seeking maximum value"
            
            vehicle_recommendations[vehicle_name] = {
                'pros': pros,
                'cons': cons,
                'overall_recommendation': overall_rec,
                'best_use_case': best_use_case
            }
        
        return {
            'vehicle_recommendations': vehicle_recommendations,
            'key_insights': comparison_results.get('insights', [])
        }