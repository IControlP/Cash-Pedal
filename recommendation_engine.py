"""
Automated Recommendation Engine
Generates intelligent recommendations and pros/cons analysis for vehicles
"""

from typing import Dict, Any, List, Tuple
import math

class RecommendationEngine:
    """Engine for generating automated vehicle recommendations"""
    
    def __init__(self):
        # Scoring weights for different factors
        self.scoring_weights = {
            'cost': 0.35,           # 35% weight on cost
            'affordability': 0.25,  # 25% weight on affordability
            'reliability': 0.20,    # 20% weight on reliability
            'efficiency': 0.15,     # 15% weight on efficiency
            'features': 0.05        # 5% weight on features
        }
        
        # Brand reliability scores (1-5 scale)
        self.brand_reliability = {
            'Toyota': 4.7,
            'Honda': 4.6,
            'Mazda': 4.4,
            'Hyundai': 4.2,
            'Kia': 4.1,
            'Subaru': 4.0,
            'Nissan': 3.8,
            'Chevrolet': 3.5,
            'Ford': 3.4,
            'Ram': 3.2,
            'BMW': 3.8,
            'Mercedes-Benz': 3.6,
            'Audi': 3.7,
            'Volkswagen': 3.3,
            'Jeep': 3.0
        }
        
        # Market segment characteristics
        self.segment_characteristics = {
            'compact': {'fuel_efficient': True, 'affordable': True, 'spacious': False, 'luxury': False},
            'sedan': {'fuel_efficient': True, 'affordable': True, 'spacious': True, 'luxury': False},
            'suv': {'fuel_efficient': False, 'affordable': True, 'spacious': True, 'luxury': False},
            'truck': {'fuel_efficient': False, 'affordable': False, 'spacious': True, 'luxury': False},
            'luxury': {'fuel_efficient': False, 'affordable': False, 'spacious': True, 'luxury': True},
            'sports': {'fuel_efficient': False, 'affordable': False, 'spacious': False, 'luxury': True}
        }
    
    def generate_vehicle_recommendations(self, vehicles: List[Dict[str, Any]], 
                                       comparison_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive recommendations for vehicle comparison"""
        
        if not vehicles:
            return {'error': 'No vehicles provided for recommendations'}
        
        # Calculate recommendation scores for each vehicle
        vehicle_scores = []
        for vehicle in vehicles:
            if vehicle.get('calculation_successful', True):
                score = self._calculate_overall_score(vehicle)
                vehicle_scores.append({**vehicle, 'overall_score': score})
            else:
                vehicle_scores.append({**vehicle, 'overall_score': 0})
        
        # Sort by overall score
        vehicle_scores.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Generate pros and cons for each vehicle
        vehicle_analysis = []
        for vehicle in vehicle_scores:
            analysis = self._generate_pros_cons(vehicle)
            vehicle_analysis.append(analysis)
        
        # Generate decision factors
        decision_factors = self._generate_decision_factors(vehicle_scores)
        
        # Create final recommendation
        final_recommendation = self._generate_final_recommendation(vehicle_scores, comparison_results)
        
        # Generate key insights
        key_insights = self._generate_key_insights(vehicle_scores, comparison_results)
        
        return {
            'vehicle_analysis': vehicle_analysis,
            'decision_factors': decision_factors,
            'final_recommendation': final_recommendation,
            'key_insights': key_insights,
            'best_by_criteria': self._get_best_by_criteria(vehicle_scores),
            'scoring_breakdown': self._get_scoring_breakdown(vehicle_scores)
        }
    
    def _calculate_overall_score(self, vehicle: Dict[str, Any]) -> float:
        """Calculate overall recommendation score for a vehicle"""
        
        scores = {}
        
        # Cost score (lower is better, normalized to 0-100)
        annual_cost = vehicle.get('annual_cost', 0)
        if annual_cost > 0:
            # Assume $20k annual cost = 0 points, $5k = 100 points
            scores['cost'] = max(0, 100 - ((annual_cost - 5000) / 150))
        else:
            scores['cost'] = 0
        
        # Affordability score
        affordability_percentage = vehicle.get('affordability_score', 20)
        # 10% of income = 100 points, 25% = 0 points
        scores['affordability'] = max(0, 100 - ((affordability_percentage - 10) * 6.67))
        
        # Reliability score
        brand_reliability = self.brand_reliability.get(vehicle.get('make', ''), 3.5)
        scores['reliability'] = (brand_reliability / 5.0) * 100
        
        # Efficiency score (cost per mile)
        cost_per_mile = vehicle.get('cost_per_mile', 1.0)
        # $0.30/mile = 100 points, $0.70/mile = 0 points
        scores['efficiency'] = max(0, 100 - ((cost_per_mile - 0.30) * 250))
        
        # Features score (simplified - based on transaction type and vehicle value)
        if vehicle.get('transaction_type', '').lower() == 'lease':
            scores['features'] = 80  # Leases often get newer features
        else:
            purchase_price = vehicle.get('purchase_price', 30000)
            # $20k = 40 points, $50k = 100 points
            scores['features'] = min(100, max(40, 40 + ((purchase_price - 20000) / 500)))
        
        # Calculate weighted overall score
        overall_score = 0
        for factor, weight in self.scoring_weights.items():
            overall_score += scores.get(factor, 50) * weight
        
        return min(100, max(0, overall_score))
    
    def _generate_pros_cons(self, vehicle: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pros and cons for a specific vehicle"""
        
        pros = []
        cons = []
        
        # Cost-based pros/cons
        annual_cost = vehicle.get('annual_cost', 0)
        if annual_cost < 8000:
            pros.append(f"Low annual cost of ${annual_cost:,.0f}")
        elif annual_cost > 15000:
            cons.append(f"High annual cost of ${annual_cost:,.0f}")
        
        # Affordability pros/cons
        affordability_score = vehicle.get('affordability_score', 20)
        if affordability_score < 12:
            pros.append("Excellent affordability - well within budget")
        elif affordability_score > 20:
            cons.append("May strain budget at current income level")
        
        # Transaction type pros/cons
        transaction_type = vehicle.get('transaction_type', '').lower()
        if transaction_type == 'lease':
            pros.append("Lower monthly payments with lease option")
            pros.append("Warranty coverage during lease term")
            cons.append("No equity building")
            cons.append("Mileage restrictions apply")
        else:
            pros.append("Build equity through ownership")
            pros.append("No mileage restrictions")
            cons.append("Higher monthly payments")
            cons.append("Responsible for maintenance after warranty")
        
        # Brand-based pros/cons
        make = vehicle.get('make', '')
        reliability_score = self.brand_reliability.get(make, 3.5)
        
        if reliability_score >= 4.5:
            pros.append(f"{make} has excellent reliability ratings")
        elif reliability_score >= 4.0:
            pros.append(f"{make} has good reliability ratings")
        elif reliability_score < 3.5:
            cons.append(f"{make} has below-average reliability ratings")
        
        # Efficiency pros/cons
        cost_per_mile = vehicle.get('cost_per_mile', 0)
        if cost_per_mile < 0.35:
            pros.append("Very efficient - low cost per mile")
        elif cost_per_mile > 0.60:
            cons.append("Higher operating costs per mile")
        
        # Value retention (for purchases)
        if transaction_type == 'purchase':
            final_value = vehicle.get('final_value', 0)
            purchase_price = vehicle.get('purchase_price', 1)
            if final_value / purchase_price > 0.4:
                pros.append("Good value retention expected")
            elif final_value / purchase_price < 0.25:
                cons.append("Higher depreciation expected")
        
        # Determine best use case
        best_for = self._determine_best_use_case(vehicle)
        
        return {
            'vehicle_name': vehicle['vehicle_name'],
            'pros': pros,
            'cons': cons,
            'best_for': best_for,
            'overall_score': vehicle.get('overall_score', 0),
            'recommendation_level': self._get_recommendation_level(vehicle.get('overall_score', 0))
        }
    
    def _determine_best_use_case(self, vehicle: Dict[str, Any]) -> str:
        """Determine the best use case for a vehicle"""
        
        annual_cost = vehicle.get('annual_cost', 0)
        affordability_score = vehicle.get('affordability_score', 20)
        transaction_type = vehicle.get('transaction_type', '').lower()
        make = vehicle.get('make', '').lower()
        
        # Budget-conscious buyers
        if affordability_score < 12 and annual_cost < 10000:
            return "Budget-conscious buyers seeking reliable transportation"
        
        # Luxury buyers
        elif make in ['bmw', 'mercedes-benz', 'audi', 'lexus']:
            return "Buyers prioritizing luxury features and brand prestige"
        
        # Lease-specific scenarios
        elif transaction_type == 'lease':
            return "Buyers wanting lower payments and latest features with warranty coverage"
        
        # High-mileage drivers
        elif vehicle.get('annual_mileage', 12000) > 20000:
            if transaction_type == 'purchase':
                return "High-mileage drivers who need ownership flexibility"
            else:
                return "Not recommended for high-mileage drivers due to lease restrictions"
        
        # Efficiency focused
        elif vehicle.get('cost_per_mile', 1.0) < 0.40:
            return "Efficiency-focused buyers prioritizing low operating costs"
        
        # Default
        else:
            return "General buyers seeking reliable transportation"
    
    def _get_recommendation_level(self, overall_score: float) -> str:
        """Get recommendation level based on overall score"""
        
        if overall_score >= 80:
            return "Highly Recommended"
        elif overall_score >= 65:
            return "Recommended"
        elif overall_score >= 50:
            return "Consider with Reservations"
        else:
            return "Not Recommended"
    
    def _generate_decision_factors(self, vehicle_scores: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate key decision factors for comparison"""
        
        factors = [
            {
                'factor': 'Total Cost of Ownership',
                'description': 'Consider both upfront and ongoing costs over your planned ownership/lease period'
            },
            {
                'factor': 'Budget Impact',
                'description': 'Ensure monthly payments fit comfortably within your budget guidelines'
            },
            {
                'factor': 'Usage Patterns',
                'description': 'Match vehicle choice to your driving habits, especially for lease mileage limits'
            },
            {
                'factor': 'Long-term Value',
                'description': 'Consider depreciation and resale value for purchases, end-of-lease costs for leases'
            },
            {
                'factor': 'Brand Reliability',
                'description': 'Factor in manufacturer reliability ratings and warranty coverage'
            }
        ]
        
        # Add specific factors based on the vehicles in comparison
        has_lease = any(v.get('transaction_type', '').lower() == 'lease' for v in vehicle_scores)
        has_purchase = any(v.get('transaction_type', '').lower() == 'purchase' for v in vehicle_scores)
        
        if has_lease and has_purchase:
            factors.append({
                'factor': 'Lease vs Purchase Decision',
                'description': 'Weigh lower lease payments against equity building and ownership flexibility'
            })
        
        return factors
    
    def _generate_final_recommendation(self, vehicle_scores: List[Dict[str, Any]], 
                                     comparison_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate final recommendation"""
        
        if not vehicle_scores:
            return {'vehicle_name': 'N/A', 'reasoning': 'No vehicles available for recommendation'}
        
        best_vehicle = vehicle_scores[0]  # Already sorted by overall score
        
        reasoning_parts = []
        
        # Score-based reasoning
        overall_score = best_vehicle.get('overall_score', 0)
        if overall_score >= 75:
            reasoning_parts.append("Scores highest across multiple evaluation criteria")
        
        # Cost reasoning
        annual_cost = best_vehicle.get('annual_cost', 0)
        if annual_cost < 10000:
            reasoning_parts.append("offers competitive annual costs")
        
        # Affordability reasoning
        if best_vehicle.get('is_affordable', False):
            reasoning_parts.append("fits well within your budget guidelines")
        
        # Reliability reasoning
        make = best_vehicle.get('make', '')
        reliability_score = self.brand_reliability.get(make, 3.5)
        if reliability_score >= 4.0:
            reasoning_parts.append(f"{make} brand provides excellent reliability")
        
        # Transaction type reasoning
        transaction_type = best_vehicle.get('transaction_type', '').lower()
        if transaction_type == 'lease':
            reasoning_parts.append("provides lower monthly payments with lease benefits")
        else:
            reasoning_parts.append("allows you to build equity through ownership")
        
        # Combine reasoning
        if reasoning_parts:
            reasoning = f"The {best_vehicle['vehicle_name']} " + ", ".join(reasoning_parts) + "."
        else:
            reasoning = f"The {best_vehicle['vehicle_name']} represents the best balance of cost, reliability, and value based on your criteria."
        
        return {
            'vehicle_name': best_vehicle['vehicle_name'],
            'reasoning': reasoning,
            'next_steps': 'Schedule a test drive, verify insurance quotes, and review financing options before making your final decision.',
            'confidence_level': self._calculate_recommendation_confidence(vehicle_scores)
        }
    
    def _calculate_recommendation_confidence(self, vehicle_scores: List[Dict[str, Any]]) -> str:
        """Calculate confidence level in recommendation"""
        
        if len(vehicle_scores) < 2:
            return "Low - Limited comparison data"
        
        best_score = vehicle_scores[0].get('overall_score', 0)
        second_best_score = vehicle_scores[1].get('overall_score', 0)
        
        score_gap = best_score - second_best_score
        
        if score_gap > 15:
            return "High - Clear leader in analysis"
        elif score_gap > 8:
            return "Medium - Moderate advantage over alternatives"
        else:
            return "Low - Very close comparison, consider personal preferences"
    
    def _generate_key_insights(self, vehicle_scores: List[Dict[str, Any]], 
                             comparison_results: Dict[str, Any]) -> List[str]:
        """Generate key insights from the comparison"""
        
        insights = []
        
        if not vehicle_scores:
            return ["No vehicles available for insight generation"]
        
        # Cost insights
        costs = [v.get('annual_cost', 0) for v in vehicle_scores if v.get('annual_cost', 0) > 0]
        if costs:
            cost_range = max(costs) - min(costs)
            if cost_range > 5000:
                insights.append(f"Annual costs vary significantly by ${cost_range:,.0f} - choose carefully based on budget")
            elif cost_range < 1500:
                insights.append("All options have similar costs - focus on features and preferences")
        
        # Affordability insights
        affordable_count = sum(1 for v in vehicle_scores if v.get('is_affordable', False))
        total_count = len(vehicle_scores)
        
        if affordable_count == total_count:
            insights.append("All vehicles meet affordability guidelines - excellent position for choice")
        elif affordable_count == 0:
            insights.append("Consider extending budget or looking at lower-cost alternatives")
        else:
            insights.append(f"{affordable_count} of {total_count} vehicles meet strict affordability guidelines")
        
        # Transaction type insights
        lease_count = sum(1 for v in vehicle_scores if v.get('transaction_type', '').lower() == 'lease')
        purchase_count = total_count - lease_count
        
        if lease_count > 0 and purchase_count > 0:
            insights.append("Mix of lease and purchase options provides flexibility in decision making")
        
        # Brand diversity insights
        brands = set(v.get('make', '') for v in vehicle_scores)
        if len(brands) > 1:
            insights.append(f"Comparison across {len(brands)} brands provides good market coverage")
        
        # Reliability insights
        avg_reliability = sum(self.brand_reliability.get(v.get('make', ''), 3.5) for v in vehicle_scores) / len(vehicle_scores)
        if avg_reliability >= 4.0:
            insights.append("All brands in comparison have above-average reliability ratings")
        elif avg_reliability < 3.5:
            insights.append("Consider reliability track record when making final decision")
        
        return insights[:6]  # Limit to top 6 insights
    
    def _get_best_by_criteria(self, vehicle_scores: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Get best vehicle by different criteria"""
        
        if not vehicle_scores:
            return {}
        
        # Filter successful calculations
        valid_vehicles = [v for v in vehicle_scores if v.get('calculation_successful', True)]
        
        if not valid_vehicles:
            return {}
        
        criteria = {}
        
        # Lowest cost
        criteria['lowest_cost'] = min(valid_vehicles, key=lambda x: x.get('annual_cost', float('inf')))
        
        # Most affordable
        criteria['most_affordable'] = min(valid_vehicles, key=lambda x: x.get('affordability_score', float('inf')))
        
        # Best value (highest overall score)
        criteria['best_value'] = max(valid_vehicles, key=lambda x: x.get('overall_score', 0))
        
        # Best efficiency
        criteria['best_efficiency'] = min(valid_vehicles, key=lambda x: x.get('cost_per_mile', float('inf')))
        
        # Most reliable brand
        criteria['most_reliable'] = max(valid_vehicles, 
                                      key=lambda x: self.brand_reliability.get(x.get('make', ''), 0))
        
        return criteria
    
    def _get_scoring_breakdown(self, vehicle_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get detailed scoring breakdown for transparency"""
        
        breakdown = {
            'scoring_methodology': {
                'cost_weight': f"{self.scoring_weights['cost']*100:.0f}%",
                'affordability_weight': f"{self.scoring_weights['affordability']*100:.0f}%",
                'reliability_weight': f"{self.scoring_weights['reliability']*100:.0f}%",
                'efficiency_weight': f"{self.scoring_weights['efficiency']*100:.0f}%",
                'features_weight': f"{self.scoring_weights['features']*100:.0f}%"
            },
            'score_ranges': {
                'excellent': '80-100 points',
                'good': '65-79 points',
                'fair': '50-64 points',
                'poor': 'Below 50 points'
            }
        }
        
        return breakdown

# Test function
def test_recommendation_engine():
    """Test the recommendation engine"""
    engine = RecommendationEngine()
    
    # Create sample vehicles for testing
    vehicles = [
        {
            'vehicle_name': '2023 Toyota Camry LE',
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2023,
            'transaction_type': 'Purchase',
            'annual_cost': 8500,
            'total_cost': 42500,
            'cost_per_mile': 0.35,
            'affordability_score': 14,
            'is_affordable': True,
            'purchase_price': 28000,
            'final_value': 15000,
            'calculation_successful': True
        },
        {
            'vehicle_name': '2023 Honda Civic LX',
            'make': 'Honda',
            'model': 'Civic',
            'year': 2023,
            'transaction_type': 'Lease',
            'annual_cost': 7200,
            'total_cost': 21600,
            'cost_per_mile': 0.30,
            'affordability_score': 12,
            'is_affordable': True,
            'calculation_successful': True
        }
    ]
    
    # Mock comparison results
    comparison_results = {
        'analysis': {
            'cost_statistics': {
                'min_annual_cost': 7200,
                'max_annual_cost': 8500,
                'cost_range': 1300
            }
        }
    }
    
    print("Testing recommendation engine...")
    recommendations = engine.generate_vehicle_recommendations(vehicles, comparison_results)
    
    # Print results
    print(f"\nFinal Recommendation:")
    final_rec = recommendations.get('final_recommendation', {})
    print(f"Vehicle: {final_rec.get('vehicle_name', 'N/A')}")
    print(f"Reasoning: {final_rec.get('reasoning', 'N/A')}")
    print(f"Confidence: {final_rec.get('confidence_level', 'N/A')}")
    
    print(f"\nKey Insights:")
    for insight in recommendations.get('key_insights', [])[:3]:
        print(f"• {insight}")
    
    print(f"\nBest by Criteria:")
    best_criteria = recommendations.get('best_by_criteria', {})
    for criterion, vehicle in best_criteria.items():
        if vehicle:
            print(f"  {criterion.replace('_', ' ').title()}: {vehicle.get('vehicle_name', 'N/A')}")

if __name__ == "__main__":
    test_recommendation_engine()