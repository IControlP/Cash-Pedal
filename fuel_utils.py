"""
Fuel Cost Calculator
Calculates fuel costs based on vehicle efficiency, driving patterns, and fuel prices
"""

from typing import Dict, Any, List
import math

class FuelCostCalculator:
    """Calculator for gasoline vehicle fuel costs"""
    
    def __init__(self):
        # Driving style MPG adjustments
        self.driving_style_multipliers = {
            'gentle': 1.15,     # 15% better MPG
            'normal': 1.0,      # Baseline MPG
            'aggressive': 0.85  # 15% worse MPG
        }
        
        # Terrain MPG adjustments  
        self.terrain_multipliers = {
            'flat': 1.05,       # 5% better MPG
            'hilly': 0.95       # 5% worse MPG
        }
        
        # Typical MPG by vehicle category (baseline estimates)
        self.vehicle_mpg_estimates = {
            'compact': 32,
            'sedan': 28,
            'suv': 24,
            'truck': 20,
            'luxury': 25,
            'sports': 22,
            'hybrid': 45,
            'electric': 0  # N/A for electric
        }
    
    def calculate_annual_fuel_cost(self, annual_mileage: int, mpg: float,
                                 fuel_price: float, driving_style: str = 'normal',
                                 terrain: str = 'flat') -> float:
        """Calculate annual fuel cost for gasoline vehicles"""
        
        if mpg <= 0 or annual_mileage <= 0:
            return 0
        
        # Apply driving style and terrain adjustments to MPG
        adjusted_mpg = mpg * self.driving_style_multipliers.get(driving_style, 1.0)
        adjusted_mpg *= self.terrain_multipliers.get(terrain, 1.0)
        
        # Calculate annual gallons needed
        annual_gallons = annual_mileage / adjusted_mpg
        
        # Calculate annual cost
        annual_cost = annual_gallons * fuel_price
        
        return annual_cost
    
    def estimate_mpg_for_vehicle(self, make: str, model: str, year: int) -> float:
        """Estimate MPG for a vehicle (simplified implementation)"""
        
        # This would ideally pull from a comprehensive fuel economy database
        # For now, use simplified logic based on vehicle characteristics
        
        model_lower = model.lower()
        
        # Hybrid detection
        if any(term in model_lower for term in ['hybrid', 'prius']):
            return 45
        
        # Electric detection (should use EV calculator instead)
        if any(term in model_lower for term in ['electric', 'ev', 'volt', 'leaf']):
            return 0  # Use EV calculator
        
        # Truck detection
        if any(term in model_lower for term in ['silverado', 'f-150', 'ram', 'colorado', 'ranger', 'ridgeline']):
            if 'colorado' in model_lower or 'ranger' in model_lower:
                return 24  # Smaller trucks
            return 20  # Full-size trucks
        
        # SUV detection
        if any(term in model_lower for term in ['suburban', 'tahoe', 'expedition', 'pilot', 'passport', 'santa fe']):
            return 24
        
        # Luxury vehicle detection
        if make.lower() in ['bmw', 'mercedes-benz', 'audi', 'lexus', 'acura', 'infiniti']:
            return 25
        
        # Sports car detection
        if any(term in model_lower for term in ['corvette', 'mustang', 'camaro', 'challenger']):
            return 22
        
        # Compact car detection
        if any(term in model_lower for term in ['civic', 'corolla', 'elantra', 'sentra']):
            return 32
        
        # Default sedan MPG
        return 28
    
    def calculate_fuel_cost_breakdown(self, annual_mileage: int, mpg: float,
                                    fuel_price: float, driving_style: str = 'normal',
                                    terrain: str = 'flat') -> Dict[str, Any]:
        """Calculate detailed fuel cost breakdown"""
        
        # Base calculation
        base_mpg = mpg
        adjusted_mpg = mpg * self.driving_style_multipliers.get(driving_style, 1.0)
        adjusted_mpg *= self.terrain_multipliers.get(terrain, 1.0)
        
        annual_gallons = annual_mileage / adjusted_mpg
        annual_cost = annual_gallons * fuel_price
        
        # Calculate monthly and per-mile costs
        monthly_cost = annual_cost / 12
        cost_per_mile = annual_cost / annual_mileage if annual_mileage > 0 else 0
        
        # Calculate impact of driving style and terrain
        base_annual_gallons = annual_mileage / base_mpg
        base_annual_cost = base_annual_gallons * fuel_price
        
        driving_impact = annual_cost - base_annual_cost
        
        return {
            'annual_cost': annual_cost,
            'monthly_cost': monthly_cost,
            'cost_per_mile': cost_per_mile,
            'annual_gallons': annual_gallons,
            'base_mpg': base_mpg,
            'adjusted_mpg': adjusted_mpg,
            'fuel_price': fuel_price,
            'driving_style_impact': driving_impact,
            'mpg_adjustment_percent': ((adjusted_mpg - base_mpg) / base_mpg) * 100
        }
    
    def compare_fuel_efficiency(self, vehicles: List[Dict[str, Any]],
                              annual_mileage: int, fuel_price: float) -> Dict[str, Any]:
        """Compare fuel costs across multiple vehicles"""
        
        comparison_results = []
        
        for vehicle in vehicles:
            mpg = vehicle.get('mpg', self.estimate_mpg_for_vehicle(
                vehicle['make'], vehicle['model'], vehicle['year']))
            
            if mpg > 0:  # Skip electric vehicles
                fuel_cost = self.calculate_annual_fuel_cost(
                    annual_mileage=annual_mileage,
                    mpg=mpg,
                    fuel_price=fuel_price,
                    driving_style=vehicle.get('driving_style', 'normal'),
                    terrain=vehicle.get('terrain', 'flat')
                )
                
                comparison_results.append({
                    'vehicle': f"{vehicle['year']} {vehicle['make']} {vehicle['model']}",
                    'mpg': mpg,
                    'annual_fuel_cost': fuel_cost,
                    'annual_gallons': annual_mileage / mpg,
                    'cost_per_mile': fuel_cost / annual_mileage
                })
        
        # Sort by fuel cost (lowest first)
        comparison_results.sort(key=lambda x: x['annual_fuel_cost'])
        
        return {
            'vehicles': comparison_results,
            'most_efficient': comparison_results[0] if comparison_results else None,
            'least_efficient': comparison_results[-1] if comparison_results else None,
            'cost_difference': (comparison_results[-1]['annual_fuel_cost'] - 
                              comparison_results[0]['annual_fuel_cost']) if len(comparison_results) > 1 else 0,
            'analysis_parameters': {
                'annual_mileage': annual_mileage,
                'fuel_price': fuel_price
            }
        }
    
    def calculate_fuel_savings_scenarios(self, base_mpg: float, annual_mileage: int,
                                       fuel_price: float) -> Dict[str, Any]:
        """Calculate fuel savings under different scenarios"""
        
        base_cost = self.calculate_annual_fuel_cost(annual_mileage, base_mpg, fuel_price)
        
        scenarios = {
            'improved_driving': {
                'description': '10% better driving efficiency',
                'mpg': base_mpg * 1.1,
                'annual_savings': 0
            },
            'reduced_mileage_10': {
                'description': '10% less driving',
                'mpg': base_mpg,
                'mileage': annual_mileage * 0.9,
                'annual_savings': 0
            },
            'reduced_mileage_20': {
                'description': '20% less driving', 
                'mpg': base_mpg,
                'mileage': annual_mileage * 0.8,
                'annual_savings': 0
            },
            'fuel_price_increase_10': {
                'description': '10% fuel price increase',
                'mpg': base_mpg,
                'fuel_price': fuel_price * 1.1,
                'annual_cost_increase': 0
            }
        }
        
        for scenario_name, scenario in scenarios.items():
            scenario_mileage = scenario.get('mileage', annual_mileage)
            scenario_mpg = scenario.get('mpg', base_mpg)
            scenario_fuel_price = scenario.get('fuel_price', fuel_price)
            
            scenario_cost = self.calculate_annual_fuel_cost(
                scenario_mileage, scenario_mpg, scenario_fuel_price
            )
            
            if 'increase' in scenario_name:
                scenario['annual_cost_increase'] = scenario_cost - base_cost
            else:
                scenario['annual_savings'] = base_cost - scenario_cost
                scenario['annual_cost'] = scenario_cost
        
        return {
            'base_annual_cost': base_cost,
            'scenarios': scenarios
        }
    
    def get_fuel_efficiency_insights(self, mpg: float, vehicle_category: str,
                                   driving_style: str, annual_mileage: int) -> List[str]:
        """Generate fuel efficiency insights and recommendations"""
        
        insights = []
        
        # Compare to category average
        category_avg = self.vehicle_mpg_estimates.get(vehicle_category, 28)
        if mpg > category_avg * 1.1:
            insights.append(f"Excellent fuel efficiency - {((mpg/category_avg)-1)*100:.0f}% above category average")
        elif mpg < category_avg * 0.9:
            insights.append(f"Below average fuel efficiency - {((category_avg/mpg)-1)*100:.0f}% below category average")
        else:
            insights.append("Fuel efficiency is near category average")
        
        # Driving style recommendations
        if driving_style == 'aggressive':
            potential_savings = mpg * 0.15  # 15% improvement potential
            insights.append(f"Gentle driving could improve efficiency by ~{potential_savings:.1f} MPG")
        
        # High mileage considerations
        if annual_mileage > 20000:
            insights.append("High annual mileage makes fuel efficiency especially important")
        elif annual_mileage < 8000:
            insights.append("Low annual mileage reduces the impact of fuel efficiency on total costs")
        
        # General recommendations
        insights.append("Regular maintenance (air filter, tire pressure) can improve MPG by 5-10%")
        insights.append("Consider route planning and trip consolidation to reduce total mileage")
        
        return insights
    
    def calculate_break_even_mpg(self, current_annual_cost: float, new_vehicle_price_premium: float,
                               annual_mileage: int, fuel_price: float, years: int) -> float:
        """Calculate required MPG improvement to justify a more expensive, efficient vehicle"""
        
        # Total fuel savings needed over the analysis period
        total_savings_needed = new_vehicle_price_premium
        annual_savings_needed = total_savings_needed / years
        
        # Calculate required new annual fuel cost
        required_new_annual_cost = current_annual_cost - annual_savings_needed
        
        # Calculate required gallons
        required_annual_gallons = required_new_annual_cost / fuel_price
        
        # Calculate required MPG
        required_mpg = annual_mileage / required_annual_gallons
        
        return required_mpg

# Test function
def test_fuel_calculator():
    """Test the fuel cost calculator"""
    calculator = FuelCostCalculator()
    
    # Test basic fuel cost calculation
    annual_cost = calculator.calculate_annual_fuel_cost(
        annual_mileage=12000,
        mpg=28,
        fuel_price=3.50,
        driving_style='normal',
        terrain='flat'
    )
    
    print(f"Annual fuel cost: ${annual_cost:.0f}")
    
    # Test detailed breakdown
    breakdown = calculator.calculate_fuel_cost_breakdown(
        annual_mileage=12000,
        mpg=28,
        fuel_price=3.50,
        driving_style='aggressive',
        terrain='hilly'
    )
    
    print(f"\nDetailed Breakdown:")
    print(f"Base MPG: {breakdown['base_mpg']:.1f}")
    print(f"Adjusted MPG: {breakdown['adjusted_mpg']:.1f}")
    print(f"Annual gallons: {breakdown['annual_gallons']:.0f}")
    print(f"Cost per mile: ${breakdown['cost_per_mile']:.3f}")
    print(f"Driving impact: ${breakdown['driving_style_impact']:+.0f}")
    
    # Test MPG estimation
    estimated_mpg = calculator.estimate_mpg_for_vehicle("Toyota", "Camry", 2023)
    print(f"\nEstimated MPG for Toyota Camry: {estimated_mpg}")
    
    # Test insights
    insights = calculator.get_fuel_efficiency_insights(28, 'sedan', 'normal', 12000)
    print(f"\nFuel Efficiency Insights:")
    for insight in insights:
        print(f"• {insight}")

if __name__ == "__main__":
    test_fuel_calculator()