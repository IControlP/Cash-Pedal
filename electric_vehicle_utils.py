"""
Electric Vehicle Cost Calculator
Calculates electricity costs for electric vehicles based on efficiency and charging patterns
"""

from typing import Dict, Any, List
import math

class EVCostCalculator:
    """Calculator for electric vehicle energy costs"""
    
    def __init__(self):
        # Charging efficiency losses
        self.charging_efficiency = {
            'home_level1': 0.85,    # 15% loss for Level 1 (120V)
            'home_level2': 0.90,    # 10% loss for Level 2 (240V)
            'public_dc_fast': 0.85, # 15% loss for DC fast charging
            'public_level2': 0.88   # 12% loss for public Level 2
        }
        
        # Typical charging costs (per kWh)
        self.charging_cost_multipliers = {
            'home': 1.0,           # Use residential rate
            'public_level2': 1.5,  # 50% premium for public Level 2
            'public_dc_fast': 2.5, # 150% premium for DC fast charging
            'workplace': 0.5       # Often subsidized or free
        }
        
        # Typical EV efficiency by category (kWh per 100 miles)
        self.ev_efficiency_estimates = {
            'compact': 28,    # e.g., Nissan Leaf
            'sedan': 32,      # e.g., Tesla Model 3
            'suv': 38,        # e.g., Tesla Model Y
            'luxury': 42,     # e.g., BMW iX
            'truck': 50,      # e.g., Ford F-150 Lightning
            'performance': 45 # e.g., Tesla Model S Plaid
        }
        
        # Charging pattern assumptions
        self.default_charging_patterns = {
            'home_primary': {
                'home': 0.80,
                'workplace': 0.15,
                'public_level2': 0.03,
                'public_dc_fast': 0.02
            },
            'mixed': {
                'home': 0.60,
                'workplace': 0.20,
                'public_level2': 0.15,
                'public_dc_fast': 0.05
            },
            'public_heavy': {
                'home': 0.40,
                'workplace': 0.10,
                'public_level2': 0.35,
                'public_dc_fast': 0.15
            }
        }
    
    def calculate_annual_electricity_cost(self, annual_mileage: int, vehicle_efficiency: float,
                                        electricity_rate: float, charging_preference: str = 'mixed') -> float:
        """Calculate annual electricity cost for an EV"""
        
        if annual_mileage <= 0 or vehicle_efficiency <= 0:
            return 0
        
        # Calculate total kWh needed per year
        annual_kwh_needed = (annual_mileage / 100) * vehicle_efficiency
        
        # Get charging pattern
        charging_pattern = self.default_charging_patterns.get(charging_preference, 
                                                            self.default_charging_patterns['mixed'])
        
        total_cost = 0
        
        # Calculate cost for each charging type
        for charging_type, percentage in charging_pattern.items():
            if percentage > 0:
                # kWh for this charging type
                kwh_for_type = annual_kwh_needed * percentage
                
                # Account for charging efficiency losses
                if charging_type == 'home':
                    efficiency = self.charging_efficiency['home_level2']
                    cost_multiplier = self.charging_cost_multipliers['home']
                elif charging_type == 'workplace':
                    efficiency = self.charging_efficiency['home_level2']
                    cost_multiplier = self.charging_cost_multipliers['workplace']
                elif charging_type == 'public_level2':
                    efficiency = self.charging_efficiency['public_level2']
                    cost_multiplier = self.charging_cost_multipliers['public_level2']
                elif charging_type == 'public_dc_fast':
                    efficiency = self.charging_efficiency['public_dc_fast']
                    cost_multiplier = self.charging_cost_multipliers['public_dc_fast']
                else:
                    efficiency = 0.90
                    cost_multiplier = 1.0
                
                # Calculate actual kWh needed (accounting for losses)
                actual_kwh_needed = kwh_for_type / efficiency
                
                # Calculate cost
                effective_rate = electricity_rate * cost_multiplier
                cost_for_type = actual_kwh_needed * effective_rate
                
                total_cost += cost_for_type
        
        return total_cost
    
    def estimate_ev_efficiency(self, make: str, model: str, year: int) -> float:
        """Estimate EV efficiency (kWh per 100 miles)"""
        
        model_lower = model.lower()
        
        # Specific model efficiency estimates (kWh/100 miles)
        specific_efficiencies = {
            'leaf': 30,           # Nissan Leaf
            'model 3': 28,        # Tesla Model 3
            'model s': 38,        # Tesla Model S
            'model x': 42,        # Tesla Model X
            'model y': 32,        # Tesla Model Y
            'mustang mach-e': 35, # Ford Mustang Mach-E
            'ioniq': 25,          # Hyundai Ioniq
            'bolt': 28,           # Chevrolet Bolt
            'e-tron': 45,         # Audi e-tron
            'i3': 27,             # BMW i3
            'i4': 35,             # BMW i4
            'ix': 42,             # BMW iX
            'taycan': 44,         # Porsche Taycan
            'id.4': 33,           # Volkswagen ID.4
            'polestar': 38        # Polestar models
        }
        
        # Check for specific model matches
        for model_key, efficiency in specific_efficiencies.items():
            if model_key in model_lower:
                return efficiency
        
        # Fall back to category estimates
        if any(term in model_lower for term in ['truck', 'pickup', 'lightning']):
            return self.ev_efficiency_estimates['truck']
        elif any(term in model_lower for term in ['suv', 'crossover']):
            return self.ev_efficiency_estimates['suv']
        elif make.lower() in ['bmw', 'mercedes-benz', 'audi', 'porsche']:
            return self.ev_efficiency_estimates['luxury']
        elif any(term in model_lower for term in ['performance', 'sport', 'plaid']):
            return self.ev_efficiency_estimates['performance']
        elif any(term in model_lower for term in ['compact', 'small']):
            return self.ev_efficiency_estimates['compact']
        else:
            return self.ev_efficiency_estimates['sedan']  # Default
    
    def calculate_ev_cost_breakdown(self, annual_mileage: int, vehicle_efficiency: float,
                                  electricity_rate: float, charging_preference: str = 'mixed') -> Dict[str, Any]:
        """Calculate detailed EV cost breakdown"""
        
        # Total energy needed
        annual_kwh_needed = (annual_mileage / 100) * vehicle_efficiency
        
        # Get charging pattern
        charging_pattern = self.default_charging_patterns.get(charging_preference,
                                                            self.default_charging_patterns['mixed'])
        
        breakdown = {
            'total_annual_cost': 0,
            'charging_breakdown': {},
            'total_kwh_consumed': 0,
            'average_cost_per_kwh': 0,
            'cost_per_mile': 0,
            'monthly_cost': 0
        }
        
        total_kwh_consumed = 0
        
        # Calculate for each charging type
        for charging_type, percentage in charging_pattern.items():
            if percentage > 0:
                kwh_for_type = annual_kwh_needed * percentage
                
                # Get efficiency and cost multiplier
                if charging_type == 'home':
                    efficiency = self.charging_efficiency['home_level2']
                    cost_multiplier = self.charging_cost_multipliers['home']
                elif charging_type == 'workplace':
                    efficiency = self.charging_efficiency['home_level2']
                    cost_multiplier = self.charging_cost_multipliers['workplace']
                elif charging_type == 'public_level2':
                    efficiency = self.charging_efficiency['public_level2']
                    cost_multiplier = self.charging_cost_multipliers['public_level2']
                elif charging_type == 'public_dc_fast':
                    efficiency = self.charging_efficiency['public_dc_fast']
                    cost_multiplier = self.charging_cost_multipliers['public_dc_fast']
                else:
                    efficiency = 0.90
                    cost_multiplier = 1.0
                
                # Calculate consumption and cost
                actual_kwh_consumed = kwh_for_type / efficiency
                effective_rate = electricity_rate * cost_multiplier
                cost = actual_kwh_consumed * effective_rate
                
                breakdown['charging_breakdown'][charging_type] = {
                    'percentage': percentage * 100,
                    'kwh_needed': kwh_for_type,
                    'kwh_consumed': actual_kwh_consumed,
                    'effective_rate': effective_rate,
                    'annual_cost': cost,
                    'efficiency_loss': kwh_for_type * (1 - efficiency)
                }
                
                breakdown['total_annual_cost'] += cost
                total_kwh_consumed += actual_kwh_consumed
        
        # Calculate summary metrics
        breakdown['total_kwh_consumed'] = total_kwh_consumed
        breakdown['average_cost_per_kwh'] = (breakdown['total_annual_cost'] / total_kwh_consumed 
                                           if total_kwh_consumed > 0 else 0)
        breakdown['cost_per_mile'] = (breakdown['total_annual_cost'] / annual_mileage 
                                    if annual_mileage > 0 else 0)
        breakdown['monthly_cost'] = breakdown['total_annual_cost'] / 12
        
        return breakdown
    
    def compare_charging_strategies(self, annual_mileage: int, vehicle_efficiency: float,
                                  electricity_rate: float) -> Dict[str, Any]:
        """Compare different charging strategy costs"""
        
        strategy_results = {}
        
        for strategy_name, pattern in self.default_charging_patterns.items():
            cost = self.calculate_annual_electricity_cost(
                annual_mileage, vehicle_efficiency, electricity_rate, strategy_name
            )
            
            strategy_results[strategy_name] = {
                'annual_cost': cost,
                'monthly_cost': cost / 12,
                'cost_per_mile': cost / annual_mileage if annual_mileage > 0 else 0,
                'charging_pattern': pattern
            }
        
        # Find cheapest and most expensive
        sorted_strategies = sorted(strategy_results.items(), key=lambda x: x[1]['annual_cost'])
        
        return {
            'strategies': strategy_results,
            'cheapest': sorted_strategies[0],
            'most_expensive': sorted_strategies[-1],
            'cost_difference': sorted_strategies[-1][1]['annual_cost'] - sorted_strategies[0][1]['annual_cost']
        }
    
    def calculate_gas_vs_ev_comparison(self, annual_mileage: int, gas_mpg: float,
                                     gas_price: float, ev_efficiency: float,
                                     electricity_rate: float, charging_preference: str = 'mixed') -> Dict[str, Any]:
        """Compare gasoline vs electric vehicle operating costs"""
        
        # Calculate gas vehicle annual fuel cost
        annual_gallons = annual_mileage / gas_mpg if gas_mpg > 0 else 0
        gas_annual_cost = annual_gallons * gas_price
        
        # Calculate EV annual electricity cost
        ev_annual_cost = self.calculate_annual_electricity_cost(
            annual_mileage, ev_efficiency, electricity_rate, charging_preference
        )
        
        # Calculate savings
        annual_savings = gas_annual_cost - ev_annual_cost
        cost_per_mile_gas = gas_annual_cost / annual_mileage if annual_mileage > 0 else 0
        cost_per_mile_ev = ev_annual_cost / annual_mileage if annual_mileage > 0 else 0
        
        return {
            'gas_vehicle': {
                'annual_cost': gas_annual_cost,
                'cost_per_mile': cost_per_mile_gas,
                'annual_gallons': annual_gallons
            },
            'electric_vehicle': {
                'annual_cost': ev_annual_cost,
                'cost_per_mile': cost_per_mile_ev,
                'annual_kwh': (annual_mileage / 100) * ev_efficiency
            },
            'comparison': {
                'annual_savings': annual_savings,
                'monthly_savings': annual_savings / 12,
                'savings_percentage': (annual_savings / gas_annual_cost * 100) if gas_annual_cost > 0 else 0,
                'ev_cost_advantage': annual_savings > 0
            }
        }
    
    def get_ev_insights(self, annual_cost: float, vehicle_efficiency: float,
                       charging_preference: str, electricity_rate: float) -> List[str]:
        """Generate EV-specific insights and recommendations"""
        
        insights = []
        
        # Efficiency insights
        if vehicle_efficiency <= 30:
            insights.append("Excellent efficiency - among the most efficient EVs available")
        elif vehicle_efficiency <= 35:
            insights.append("Good efficiency - above average for electric vehicles")
        elif vehicle_efficiency >= 45:
            insights.append("Lower efficiency - consider more efficient models for cost savings")
        
        # Charging insights
        if charging_preference == 'home_primary':
            insights.append("Home charging provides the lowest cost per kWh")
            insights.append("Consider time-of-use electricity rates for additional savings")
        elif charging_preference == 'public_heavy':
            insights.append("Heavy public charging increases costs significantly")
            insights.append("Installing home charging could reduce annual costs by 30-50%")
        
        # Cost insights
        monthly_cost = annual_cost / 12
        if monthly_cost < 50:
            insights.append("Very low 'fuel' costs - major advantage of electric vehicles")
        elif monthly_cost > 100:
            insights.append("Higher electricity costs - review charging habits and rates")
        
        # General EV recommendations
        insights.append("Consider solar panels to further reduce charging costs")
        insights.append("Look for utility rebates and time-of-use rate programs")
        insights.append("Plan charging around off-peak hours when possible")
        
        return insights
    
    def calculate_home_charging_setup_cost(self, charging_level: str = 'level2') -> Dict[str, Any]:
        """Calculate cost of setting up home charging"""
        
        setup_costs = {
            'level1': {
                'equipment_cost': 0,        # Uses standard outlet
                'installation_cost': 0,     # No installation needed
                'total_cost': 0,
                'charging_speed': '3-5 miles per hour',
                'description': 'Standard 120V outlet - slowest but no setup cost'
            },
            'level2_basic': {
                'equipment_cost': 500,      # Basic Level 2 charger
                'installation_cost': 800,   # Electrical work for 240V outlet
                'total_cost': 1300,
                'charging_speed': '25-40 miles per hour',
                'description': 'Basic 240V charger - good for most users'
            },
            'level2_premium': {
                'equipment_cost': 1200,     # Premium Level 2 charger with smart features
                'installation_cost': 1000,  # More complex installation
                'total_cost': 2200,
                'charging_speed': '25-40 miles per hour',
                'description': 'Smart charger with WiFi, scheduling, and monitoring'
            }
        }
        
        return setup_costs.get(charging_level, setup_costs['level2_basic'])
    
    def calculate_charging_time(self, battery_capacity_kwh: float, current_charge_percent: float,
                              target_charge_percent: float, charging_power_kw: float) -> Dict[str, Any]:
        """Calculate charging time for different scenarios"""
        
        # Energy needed to charge
        energy_needed = battery_capacity_kwh * ((target_charge_percent - current_charge_percent) / 100)
        
        if energy_needed <= 0 or charging_power_kw <= 0:
            return {'charging_time_hours': 0, 'charging_time_minutes': 0}
        
        # Basic charging time (doesn't account for charging curve)
        charging_time_hours = energy_needed / charging_power_kw
        charging_time_minutes = charging_time_hours * 60
        
        # Adjust for real-world charging curve (charging slows down as battery fills)
        if target_charge_percent > 80:
            # Charging slows significantly above 80%
            adjustment_factor = 1.3
        elif target_charge_percent > 90:
            # Even slower above 90%
            adjustment_factor = 1.6
        else:
            adjustment_factor = 1.0
        
        actual_charging_time_hours = charging_time_hours * adjustment_factor
        actual_charging_time_minutes = actual_charging_time_hours * 60
        
        return {
            'energy_needed_kwh': energy_needed,
            'theoretical_charging_time_hours': charging_time_hours,
            'actual_charging_time_hours': actual_charging_time_hours,
            'actual_charging_time_minutes': actual_charging_time_minutes,
            'charging_power_kw': charging_power_kw,
            'adjustment_factor': adjustment_factor
        }

# Test function
def test_ev_calculator():
    """Test the EV cost calculator"""
    calculator = EVCostCalculator()
    
    # Test basic cost calculation
    annual_cost = calculator.calculate_annual_electricity_cost(
        annual_mileage=12000,
        vehicle_efficiency=32,  # kWh per 100 miles
        electricity_rate=0.12,  # $0.12 per kWh
        charging_preference='mixed'
    )
    
    print(f"Annual electricity cost: ${annual_cost:.0f}")
    
    # Test detailed breakdown
    breakdown = calculator.calculate_ev_cost_breakdown(
        annual_mileage=12000,
        vehicle_efficiency=32,
        electricity_rate=0.12,
        charging_preference='mixed'
    )
    
    print(f"\nDetailed Breakdown:")
    print(f"Total annual cost: ${breakdown['total_annual_cost']:.0f}")
    print(f"Monthly cost: ${breakdown['monthly_cost']:.0f}")
    print(f"Cost per mile: ${breakdown['cost_per_mile']:.3f}")
    print(f"Total kWh consumed: {breakdown['total_kwh_consumed']:.0f}")
    
    print(f"\nCharging Breakdown:")
    for charging_type, details in breakdown['charging_breakdown'].items():
        print(f"  {charging_type.replace('_', ' ').title()}: {details['percentage']:.0f}% - ${details['annual_cost']:.0f}")
    
    # Test gas vs EV comparison
    comparison = calculator.calculate_gas_vs_ev_comparison(
        annual_mileage=12000,
        gas_mpg=28,
        gas_price=3.50,
        ev_efficiency=32,
        electricity_rate=0.12,
        charging_preference='mixed'
    )
    
    print(f"\nGas vs EV Comparison:")
    print(f"Gas vehicle annual cost: ${comparison['gas_vehicle']['annual_cost']:.0f}")
    print(f"EV annual cost: ${comparison['electric_vehicle']['annual_cost']:.0f}")
    print(f"Annual savings with EV: ${comparison['comparison']['annual_savings']:.0f}")
    print(f"Savings percentage: {comparison['comparison']['savings_percentage']:.1f}%")
    
    # Test charging strategies
    strategies = calculator.compare_charging_strategies(12000, 32, 0.12)
    
    print(f"\nCharging Strategy Comparison:")
    for strategy, details in strategies['strategies'].items():
        print(f"  {strategy.replace('_', ' ').title()}: ${details['annual_cost']:.0f}")
    
    # Test insights
    insights = calculator.get_ev_insights(annual_cost, 32, 'mixed', 0.12)
    print(f"\nEV Insights:")
    for insight in insights:
        print(f"• {insight}")

if __name__ == "__main__":
    test_ev_calculator()